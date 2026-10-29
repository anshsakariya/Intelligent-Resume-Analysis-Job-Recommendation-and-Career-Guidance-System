import json
import os
import google.generativeai as genai
from django.conf import settings
from django.utils import timezone

from roadmap.models import Roadmap, RoadmapTask
from skills.models import Skill, UserSkill
from jobs.models import Job

class PlannerAgent:
    """
    Agent responsible for analyzing user career goals and skill gaps to generate
    personalized, step-by-step learning roadmaps with progress tracking.
    """

    def __init__(self):
        self.api_key = getattr(settings, 'GEMINI_API_KEY', '')
        if self.api_key:
            genai.configure(api_key=self.api_key)

    # ─────────────────────────────────────────────────────────────
    # Comprehensive role → required-skills mapping
    # Only skills directly relevant to the role are listed.
    # ─────────────────────────────────────────────────────────────
    ROLE_SKILL_MAP = {
        'Python Developer': [
            'Python', 'Django', 'Flask', 'FastAPI', 'SQL', 'PostgreSQL',
            'REST API', 'Git', 'Docker', 'Redis', 'Celery', 'Testing',
            'Linux', 'Data Structures', 'OOP',
        ],
        'Django Developer': [
            'Python', 'Django', 'Django REST Framework', 'REST API',
            'PostgreSQL', 'Redis', 'Celery', 'Docker', 'Git',
            'HTML', 'CSS', 'JavaScript', 'Testing', 'Linux',
        ],
        'Full Stack Developer': [
            'JavaScript', 'React', 'Node.js', 'Python', 'Django',
            'HTML', 'CSS', 'PostgreSQL', 'MongoDB', 'Git', 'REST API',
            'TypeScript', 'Docker', 'Testing',
        ],
        'Backend Developer': [
            'Python', 'Django', 'Flask', 'FastAPI', 'REST API', 'SQL',
            'PostgreSQL', 'Redis', 'Docker', 'Git', 'Linux',
            'Celery', 'Testing', 'Microservices',
        ],
        'Data Analyst': [
            'Python', 'SQL', 'Pandas', 'NumPy', 'Matplotlib',
            'Data Visualization', 'Excel', 'Power BI', 'Statistics',
            'PostgreSQL', 'Git', 'Data Cleaning',
        ],
        'Data Scientist': [
            'Python', 'Machine Learning', 'Pandas', 'NumPy',
            'Scikit-learn', 'Statistics', 'SQL', 'Data Visualization',
            'Jupyter Notebook', 'Feature Engineering', 'Deep Learning',
            'Git',
        ],
        'Machine Learning Engineer': [
            'Python', 'Machine Learning', 'Deep Learning', 'PyTorch',
            'TensorFlow', 'Scikit-learn', 'MLOps', 'Docker', 'Git',
            'SQL', 'Feature Engineering', 'Model Deployment',
            'Data Pipelines',
        ],
        'AI Engineer': [
            'Python', 'Machine Learning', 'Deep Learning', 'NLP',
            'Generative AI', 'PyTorch', 'TensorFlow', 'LangChain',
            'REST API', 'Docker', 'Git', 'Prompt Engineering',
        ],
        'Software Developer': [
            'Python', 'SQL', 'Git', 'GitHub', 'REST API', 'Docker',
            'Testing', 'Linux', 'Data Structures', 'OOP',
            'Design Patterns', 'CI/CD',
        ],
    }

    def identify_skill_gap(self, user):
        """
        Calculates existing skills vs missing skills for user's target career role.
        Strictly restricts both existing and missing skills to the user's chosen profile/domain,
        ensuring that out-of-domain skills (e.g. AI/Data skills on a Python Developer profile)
        and redundant duplicates (Git vs GIT, NumPy vs Numpy) do not clutter the roadmap.
        """
        profile = getattr(user, 'profile', None)
        target_role = profile.target_role if profile else 'Python Developer'

        # Domain standard skills for target role
        role_skills_list = self.ROLE_SKILL_MAP.get(target_role, self.ROLE_SKILL_MAP['Python Developer'])
        # Map lowercase to standard canonical name
        role_skill_canon = {s.lower(): s for s in role_skills_list}

        # Extracted user skills from resume
        raw_user_skills = UserSkill.objects.filter(user=user, is_extracted=True).select_related('skill')

        # Strictly filter mastered skills: only include skills that belong to the target domain
        mastered_domain_skills = set()
        user_skills_lower = set()
        for us in raw_user_skills:
            name_lower = us.skill.name.strip().lower()
            user_skills_lower.add(name_lower)
            if name_lower in role_skill_canon:
                mastered_domain_skills.add(role_skill_canon[name_lower])

        # Missing skills: domain skills that user doesn't have yet
        missing_domain_skills = [
            s for s in role_skills_list
            if s.lower() not in user_skills_lower
        ]

        # Sync missing target skills in UserSkill model
        if missing_domain_skills:
            # Clean up out-of-domain target skills previously added
            UserSkill.objects.filter(user=user, is_target=True).exclude(
                skill__name__in=role_skills_list
            ).delete()

            existing_target_names = set(
                UserSkill.objects.filter(user=user, is_target=True).values_list('skill__name', flat=True)
            )
            to_add = [s for s in missing_domain_skills if s not in existing_target_names]
            if to_add:
                skills_dict = {s.name: s for s in Skill.objects.filter(name__in=to_add)}
                for s_name in to_add:
                    if s_name not in skills_dict:
                        skills_dict[s_name], _ = Skill.objects.get_or_create(name=s_name)
                UserSkill.objects.bulk_create([
                    UserSkill(user=user, skill=skills_dict[s_name], is_target=True, is_extracted=False)
                    for s_name in to_add
                ], ignore_conflicts=True)

        return {
            'existing_skills': sorted(list(mastered_domain_skills)),
            'missing_skills': missing_domain_skills,
            'target_role': target_role
        }

    def generate_roadmap(self, user, hours_per_day=2, days_per_week=5):
        """
        Generates a structured learning roadmap. Uses Gemini API if key is valid;
        otherwise falls back to rule-based curriculum synthesizer.
        """
        gap_info = self.identify_skill_gap(user)
        target_role = gap_info['target_role']
        existing_skills = gap_info['existing_skills']
        missing_skills = gap_info['missing_skills']

        # Create Roadmap Instance
        roadmap = Roadmap.objects.create(
            user=user,
            target_role=target_role,
            hours_per_day=hours_per_day,
            days_per_week=days_per_week,
            summary=f"Personalized roadmap to become a {target_role}. Focusing on mastering {len(missing_skills)} missing target skills."
        )

        # Attempt Gemini API Generation
        if self.api_key:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                You are an expert career mentor. Create a 3-month structured learning roadmap for a student aiming to become a {target_role}.
                - Known Skills: {', '.join(existing_skills) if existing_skills else 'Basic programming'}
                - Missing Target Skills to Master: {', '.join(missing_skills) if missing_skills else 'Advanced concepts'}
                - Commitment: {hours_per_day} hours/day, {days_per_week} days/week.

                IMPORTANT: Only include skills and topics that are DIRECTLY relevant to the "{target_role}" role.
                Do NOT include unrelated skills (e.g., do not suggest AWS/Cloud for a Python Developer,
                do not suggest frontend frameworks for a Data Analyst, etc.).
                Focus exclusively on the missing skills listed above and core competencies for {target_role}.

                Respond strictly with valid JSON array containing objects with these keys:
                "phase_name", "title", "description", "priority", "estimated_hours".
                Example format:
                [
                    {{"phase_name": "Month 1: Fundamentals", "title": "Master REST API & Backend Architecture", "description": "Study HTTP methods, JSON responses, and Django REST Framework.", "priority": "High Priority", "estimated_hours": 15}}
                ]
                """
                response = model.generate_content(prompt)
                res_text = response.text.strip()
                if "```json" in res_text:
                    res_text = res_text.split("```json")[1].split("```")[0].strip()
                elif "```" in res_text:
                    res_text = res_text.split("```")[1].split("```")[0].strip()
                
                tasks_data = json.loads(res_text)
                for order, t in enumerate(tasks_data, 1):
                    RoadmapTask.objects.create(
                        roadmap=roadmap,
                        title=t.get('title', 'Learning Module'),
                        description=t.get('description', ''),
                        phase_name=t.get('phase_name', 'Month 1'),
                        priority=t.get('priority', 'High Priority'),
                        estimated_hours=t.get('estimated_hours', 10),
                        order=order
                    )
                return roadmap
            except Exception as e:
                print(f"Gemini Roadmap API fallback activated due to: {e}")

        # Rule-Based Fallback Synthesizer — uses role-specific skills only
        role_defaults = self.ROLE_SKILL_MAP.get(target_role, self.ROLE_SKILL_MAP['Python Developer'])
        # Pick top missing skills for focused roadmap modules
        priority_missing = missing_skills[:5] if missing_skills else role_defaults[:5]
        secondary_missing = missing_skills[5:] if len(missing_skills) > 5 else role_defaults[5:8]

        fallback_phases = [
            {
                'phase': f'Month 1: Core {target_role} Fundamentals',
                'items': [
                    (
                        f'Core {target_role} Language & Concepts',
                        f"Deep dive into fundamental concepts for {target_role}. Focus on mastering: {', '.join(priority_missing[:3])}.",
                        'High Priority', 12
                    ),
                    (
                        'Version Control & Development Workflow',
                        "Master Git branching, commits, GitHub pull requests, and collaborative development best practices.",
                        'Medium Priority', 8
                    ),
                ]
            },
            {
                'phase': f'Month 2: Advanced {target_role} Skills',
                'items': [
                    (
                        f'{target_role} Specialized Skills',
                        f"Build expertise in role-specific skills: {', '.join(priority_missing[3:] or secondary_missing[:3])}.",
                        'High Priority', 15
                    ),
                    (
                        f'Practical {target_role} Applications',
                        f"Build real-world applications focusing on missing skills: {', '.join(secondary_missing[:3]) if secondary_missing else ', '.join(priority_missing[:3])}.",
                        'High Priority', 20
                    ),
                ]
            },
            {
                'phase': f'Month 3: {target_role} Portfolio & Interview Prep',
                'items': [
                    (
                        f'Cap-Stone {target_role} Project',
                        f"Build and deploy a full, production-ready {target_role} project showcasing all learned skills.",
                        'High Priority', 25
                    ),
                    (
                        f'{target_role} Interview Preparation',
                        f"Practice {target_role}-specific interview questions, system design concepts, and coding challenges.",
                        'Medium Priority', 15
                    ),
                ]
            }
        ]

        order = 1
        for phase in fallback_phases:
            p_name = phase['phase']
            for title, desc, prio, hrs in phase['items']:
                RoadmapTask.objects.create(
                    roadmap=roadmap,
                    title=title,
                    description=desc,
                    phase_name=p_name,
                    priority=prio,
                    estimated_hours=hrs,
                    order=order
                )
                order += 1

        return roadmap
