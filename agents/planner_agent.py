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

    def identify_skill_gap(self, user):
        """
        Calculates existing skills vs missing skills for user's target career role.
        """
        profile = getattr(user, 'profile', None)
        target_role = profile.target_role if profile else 'Python Developer'

        # Extracted user skills
        user_skills = UserSkill.objects.filter(user=user, is_extracted=True).select_related('skill')
        existing_skills = set(us.skill.name for us in user_skills)

        # Target career required skills from database jobs
        relevant_jobs = Job.objects.filter(title__icontains=target_role)
        required_skills = set()
        if relevant_jobs.exists():
            for job in relevant_jobs:
                for skill in job.required_skills.all():
                    required_skills.add(skill.name)
                for skill in job.preferred_skills.all():
                    required_skills.add(skill.name)
        
        # Standard fallback target skill sets if DB jobs not enough
        role_skill_defaults = {
            'Python Developer': ['Python', 'Django', 'SQL', 'PostgreSQL', 'REST API', 'Git', 'Docker', 'Redis', 'Testing'],
            'Django Developer': ['Python', 'Django', 'REST API', 'PostgreSQL', 'Redis', 'Celery', 'Docker', 'Git', 'HTML', 'CSS'],
            'Full Stack Developer': ['JavaScript', 'React', 'Python', 'Django', 'HTML', 'CSS', 'PostgreSQL', 'Git', 'REST API'],
            'Data Analyst': ['Python', 'SQL', 'Pandas', 'NumPy', 'Data Science', 'PostgreSQL', 'Git'],
            'Data Scientist': ['Python', 'Data Science', 'Machine Learning', 'Pandas', 'NumPy', 'Scikit-learn', 'SQL', 'PyTorch'],
            'Machine Learning Engineer': ['Python', 'Machine Learning', 'PyTorch', 'TensorFlow', 'Scikit-learn', 'Docker', 'AWS', 'Git'],
            'AI Engineer': ['Python', 'Generative AI', 'Machine Learning', 'PyTorch', 'NLTK', 'REST API', 'Docker', 'AWS'],
            'Backend Developer': ['Python', 'REST API', 'SQL', 'PostgreSQL', 'Redis', 'Docker', 'Git', 'Linux'],
            'Software Developer': ['Python', 'SQL', 'Git', 'GitHub', 'REST API', 'Docker', 'Testing', 'Linux'],
        }

        if not required_skills:
            defaults = role_skill_defaults.get(target_role, role_skill_defaults['Python Developer'])
            required_skills = set(defaults)

        missing_skills = list(required_skills.difference(existing_skills))

        # Save missing skills as target skills in UserSkill model (batch optimized)
        if missing_skills:
            existing_target_names = set(
                UserSkill.objects.filter(user=user, is_target=True).values_list('skill__name', flat=True)
            )
            to_add = [s for s in missing_skills if s not in existing_target_names]
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
            'existing_skills': list(existing_skills),
            'missing_skills': missing_skills,
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

        # Rule-Based Fallback Synthesizer
        fallback_phases = [
            {
                'phase': 'Month 1: Core Fundamentals & Missing Basics',
                'items': [
                    ('Core Language Mastery', f"Deep dive into fundamental concepts for {target_role}. Focus on data structures, OOP, and syntax.", 'High Priority', 12),
                    ('Version Control & Workflow', "Master Git branching, commits, GitHub pull requests, and open-source collaboration best practices.", 'Medium Priority', 8),
                ]
            },
            {
                'phase': 'Month 2: Advanced Frameworks & Databases',
                'items': [
                    ('Database Design & Queries', "Learn SQL schema design, relationships, indexing, and PostgreSQL optimization.", 'High Priority', 15),
                    ('Framework & API Mastery', f"Build backend APIs and modular applications focusing on missing skills: {', '.join(missing_skills[:3]) if missing_skills else 'REST APIs'}.", 'High Priority', 20),
                ]
            },
            {
                'phase': 'Month 3: Portfolio Projects & Interview Prep',
                'items': [
                    ('Cap-Stone Capable Project', f"Build and deploy a full-stack, production-ready {target_role} project with live deployment.", 'High Priority', 25),
                    ('Technical Interview Preparation', "Practice System Design, Data Structures & Algorithms, and mock technical interview questions.", 'Medium Priority', 15),
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
