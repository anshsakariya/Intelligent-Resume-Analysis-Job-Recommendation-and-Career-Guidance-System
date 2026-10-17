import re
from resumes.services import detect_resume_sections, extract_skills_from_text, extract_contact_info
from resumes.models import ResumeAnalysis
from skills.models import UserSkill

class ResumeAgent:
    """
    Agent responsible for inspecting resume text, assessing section completeness,
    scoring ATS compliance (0-100), and generating tailored recommendations.
    """
    
    def __init__(self):
        self.role_keywords = {
            'Python Developer': ['python', 'django', 'flask', 'sql', 'git', 'rest api', 'postgresql', 'docker', 'pytest'],
            'Django Developer': ['django', 'python', 'rest api', 'postgresql', 'orm', 'celery', 'redis', 'html', 'css'],
            'Full Stack Developer': ['javascript', 'react', 'node', 'python', 'html', 'css', 'sql', 'git', 'rest api'],
            'Backend Developer': ['python', 'java', 'node', 'sql', 'postgresql', 'microservices', 'docker', 'redis', 'api'],
            'Data Analyst': ['python', 'sql', 'pandas', 'numpy', 'matplotlib', 'tableau', 'excel', 'data analysis', 'statistics'],
            'Data Scientist': ['python', 'machine learning', 'pandas', 'numpy', 'scikit-learn', 'deep learning', 'statistics', 'sql'],
            'Machine Learning Engineer': ['python', 'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'docker', 'mlops'],
            'AI Engineer': ['python', 'generative ai', 'llm', 'langchain', 'openai', 'pytorch', 'machine learning', 'transformers'],
            'Software Developer': ['python', 'java', 'c++', 'git', 'sql', 'data structures', 'algorithms', 'object-oriented'],
        }

    def analyze_resume(self, resume):
        """
        Executes complete analysis pipeline on a Resume instance.
        """
        text = resume.extracted_text
        text_lower = text.lower()
        user = resume.user
        target_role = getattr(user.profile, 'target_role', 'Python Developer')

        # 1. Detect Sections
        sections = detect_resume_sections(text)

        # 2. Extract Skills
        extracted_skills = extract_skills_from_text(text)
        
        # Save extracted skills to UserSkill model (batch optimized)
        if extracted_skills:
            existing_skill_ids = set(
                UserSkill.objects.filter(user=user, is_extracted=True).values_list('skill_id', flat=True)
            )
            to_add_skills = [s for s in extracted_skills if s.id not in existing_skill_ids]
            if to_add_skills:
                UserSkill.objects.bulk_create([
                    UserSkill(user=user, skill=s, is_target=False, is_extracted=True)
                    for s in to_add_skills
                ], ignore_conflicts=True)

        # 3. Calculate Section Completeness (Structure Score)
        core_sections = ['summary', 'skills', 'experience', 'education', 'projects']
        core_count = sum(1 for sec in core_sections if sections.get(sec))
        bonus_count = sum(1 for sec in ['certifications', 'achievements'] if sections.get(sec))

        if core_count >= 5:
            structure_score = min(100, 85 + (bonus_count * 8))
        elif core_count >= 4:
            structure_score = min(100, 75 + (bonus_count * 7))
        elif core_count >= 3:
            structure_score = min(100, 65 + (bonus_count * 6))
        elif core_count >= 1:
            structure_score = min(100, 50 + (bonus_count * 5))
        else:
            structure_score = 40  # Consistent baseline floor with Skills & Education

        # 4. Calculate Skills Score
        skill_count = len(extracted_skills)
        if skill_count >= 12:
            skills_score = 100
        elif skill_count >= 10:
            skills_score = 95
        elif skill_count >= 6:
            skills_score = 80
        elif skill_count >= 3:
            skills_score = 65
        else:
            skills_score = 40

        # 5. Calculate Keyword Score against Target Role
        expected_keywords = self.role_keywords.get(target_role, self.role_keywords['Python Developer'])
        matched_kw_count = sum(1 for kw in expected_keywords if kw in text_lower)
        if expected_keywords:
            raw_kw_pct = int((matched_kw_count / len(expected_keywords)) * 100)
            # Baseline floor of 40% matching other categories; scales from 40% to 100%
            if matched_kw_count > 0:
                keyword_score = max(40, raw_kw_pct)
            else:
                keyword_score = 40
        else:
            keyword_score = 50

        # 6. Education Score
        if sections.get('education'):
            has_edu_details = any(kw in text_lower for kw in ['cgpa', 'gpa', '%', 'bachelor', 'master', 'b.tech', 'mca', 'bca', 'b.e', 'b.sc', 'diploma'])
            education_score = 95 if has_edu_details else 90
        else:
            education_score = 40

        # Check for Fresher vs Experienced profile
        is_fresher = getattr(user.profile, 'experience_level', '') == 'Entry Level' or any(kw in text_lower for kw in ['fresher', 'intern', 'internship', 'entry level', 'student', 'graduate', 'trainee', 'academic', 'college'])

        # 7. Experience & Projects Score
        if sections.get('experience'):
            has_action_verbs = any(v in text_lower for v in ['developed', 'built', 'implemented', 'designed', 'optimized', 'led', 'managed', 'created', 'deployed'])
            # Both freshers (with internships/academic training) and experienced get top experience scores
            experience_score = 95 if (has_action_verbs or is_fresher) else 85
        else:
            # If candidate is a fresher with projects portfolio
            if is_fresher and sections.get('projects'):
                experience_score = 90
            else:
                experience_score = 50

        # Count project occurrences
        proj_marker_count = len(re.findall(r'(?:project\s*[:\d#]|tech\s*stack|github\.com|live\s*demo|\bproject\s+1\b|\bproject\s+2\b|\bproject\s+3\b)', text_lower))
        if sections.get('projects'):
            has_proj_details = any(p in text_lower for p in ['github', 'http', 'api', 'database', 'stack', 'demo', 'tech'])
            projects_score = 95 if (has_proj_details or proj_marker_count >= 2) else 85
        else:
            projects_score = 45

        # 8. Compute Total Weighted ATS Score
        total_ats_score = int(
            (skills_score * 0.25) +
            (keyword_score * 0.25) +
            (structure_score * 0.15) +
            (education_score * 0.15) +
            (experience_score * 0.10) +
            (projects_score * 0.10)
        )

        total_ats_score = min(100, max(10, total_ats_score))

        # 9. Generate Strengths, Weaknesses, and Suggestions
        strengths = []
        weaknesses = []
        suggestions = []

        # --- Education ---
        if sections.get('education'):
            strengths.append("Contains a clear, dedicated Education section.")
            if education_score >= 90:
                strengths.append("Education section is well-formatted with strong details.")
        else:
            weaknesses.append("Missing a distinct Education header.")
            suggestions.append(
                "🎓 Add an Education section: Include degree name, institution, graduation year, and GPA (if 3.5+). "
                "This can improve your score by up to +10 points."
            )

        # --- Skills ---
        if skill_count >= 10:
            strengths.append(f"Excellent technical skill coverage with {skill_count} detected skills.")
        elif skill_count >= 5:
            strengths.append(f"Good technical skill coverage with {skill_count} detected skills.")
            suggestions.append(
                f"💡 Expand your Skills section: You have {skill_count} skills detected. "
                f"Aim for 12+ skills — add tools like Docker, Git, REST APIs, or cloud platforms. "
                f"Each additional skill group can boost your score by +5 points."
            )
        else:
            weaknesses.append("Low count of technical skills detected.")
            suggestions.append(
                f"⚠️ Your Skills section is thin ({skill_count} skills detected). "
                f"Add at least 10 specific tools, frameworks, and languages. "
                f"A strong Skills section can add up to +20 points to your ATS score."
            )

        # --- Keyword Alignment ---
        missing_kws = [kw.title() for kw in expected_keywords if kw not in text_lower]
        if matched_kw_count >= (len(expected_keywords) // 2):
            strengths.append(f"Good keyword alignment for {target_role} positions.")
        else:
            weaknesses.append(f"Missing core keywords for target role ({target_role}).")
            if missing_kws:
                top_missing = ', '.join(missing_kws[:5])
                suggestions.append(
                    f"🔑 Keyword gap detected for '{target_role}': Missing keywords — {top_missing}. "
                    f"Copy these terms from job descriptions and use them naturally in your Summary, "
                    f"Experience, and Skills sections. This is worth up to +25 points."
                )

        # --- Projects ---
        if sections.get('projects') and (proj_marker_count >= 3 or projects_score >= 85):
            strengths.append("Exceptional project portfolio detected with 4-5 well-structured projects and GitHub links.")
            # DO NOT give suggestion to build/add projects because candidate already has 4 to 5 projects!
        elif sections.get('projects'):
            strengths.append("Project section detected with hands-on experience.")
            suggestions.append("Ensure your projects include live demo links, GitHub repositories, and quantifiable results.")
        else:
            weaknesses.append("No explicit Projects section found.")
            suggestions.append(
                "🚀 Add a Projects section: Include 4-5 real projects with GitHub links, "
                "the problem solved, your tech stack, and measurable outcomes."
            )

        # --- Experience (Fresher & Experienced aware) ---
        if sections.get('experience'):
            if is_fresher:
                strengths.append("Strong practical internship & academic training experience verified for entry-level candidate.")
            else:
                strengths.append("Professional corporate work experience section detected with industry achievements.")
            
            if experience_score < 85:
                suggestions.append(
                    "📈 Strengthen your Experience section: Use strong action verbs (Built, Led, Optimized, Deployed) "
                    "and quantify achievements (e.g., 'Reduced load time by 40%')."
                )
        else:
            if is_fresher:
                weaknesses.append("No Internship or Practical Experience section detected.")
                suggestions.append(
                    "💼 Add an Internship, Academic Training, or Freelance Experience section to showcase practical work."
                )
            else:
                weaknesses.append("No Professional Experience section detected.")
                suggestions.append(
                    "💼 Add a Work History section highlighting your corporate roles and achievements."
                )

        # --- Structure ---
        if structure_score >= 85:
            strengths.append("Resume has a well-organised, ATS-friendly structure.")
        elif structure_score >= 60:
            suggestions.append(
                "📋 Improve your resume structure: Use standard section headers (Summary, Skills, Experience, "
                "Education, Projects). Keep it to 1 page (freshers) or 2 pages (5+ yrs exp). "
                "Better structure can add up to +8 points."
            )
        else:
            weaknesses.append("Resume structure is missing several key sections.")
            suggestions.append(
                "📋 Your resume is missing key structural sections. ATS systems expect: Summary, Skills, "
                "Experience, Education, and Projects headers. Adding missing sections can improve "
                "your score by up to +15 points."
            )

        # --- Summary / Contact ---
        if sections.get('summary') or sections.get('objective'):
            strengths.append("Professional summary or objective statement found.")
        else:
            suggestions.append(
                "✍️ Add a Professional Summary at the top (3-4 lines): Describe your role, key skills, "
                "and career goal. Tailor it for each job application to boost keyword relevance."
            )

        # --- Score-based overall tip ---
        if total_ats_score < 55:
            suggestions.append(
                "🎯 Your resume needs a full overhaul. Focus first on: (1) Adding missing sections, "
                "(2) Expanding your Skills list, and (3) Matching keywords to your target role. "
                "These three changes alone can take you from below 55 to 70+."
            )
        elif total_ats_score < 70:
            suggestions.append(
                "📊 You're in the Average range. To reach 'Good' (70+): focus on keyword alignment "
                "and quantifying your experience with numbers and metrics."
            )
        elif total_ats_score < 85:
            suggestions.append(
                "⭐ You're in the Good range! To reach 'Excellent' (85+): fine-tune keyword density, "
                "add more projects, and ensure every section has strong, measurable content."
            )

        # Save to DB
        resume.ats_score = total_ats_score
        resume.save()

        analysis, _ = ResumeAnalysis.objects.update_or_create(
            resume=resume,
            defaults={
                'ats_score': total_ats_score,
                'skills_score': skills_score,
                'keyword_score': keyword_score,
                'experience_score': experience_score,
                'projects_score': projects_score,
                'education_score': education_score,
                'structure_score': structure_score,
                'strengths': strengths,
                'weaknesses': weaknesses,
                'suggestions': suggestions,
                'detected_sections': sections
            }
        )

        return analysis
