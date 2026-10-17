import os
import google.generativeai as genai
from django.conf import settings

from agents.resume_agent import ResumeAgent
from agents.job_agent import JobAgent
from agents.planner_agent import PlannerAgent
from resumes.models import Resume
from roadmap.models import Roadmap
from skills.models import UserSkill

class AgentOrchestrator:
    """
    Central Orchestrator that receives user natural language queries, classifies intent,
    routes the request to the appropriate specialized sub-agent (ResumeAgent, JobAgent, PlannerAgent),
    and synthesizes a personalized response using Gemini API or local context.
    """

    def __init__(self):
        self.resume_agent = ResumeAgent()
        self.job_agent = JobAgent()
        self.planner_agent = PlannerAgent()
        
        self.api_key = getattr(settings, 'GEMINI_API_KEY', '')
        if self.api_key:
            genai.configure(api_key=self.api_key)

    def route_and_process(self, user, query):
        """
        Determines intent and delegates query processing.
        Returns tuple: (response_text, agent_name)
        """
        q_lower = query.lower()

        # 1. Resume Agent Routing
        if any(kw in q_lower for kw in ['resume', 'ats', 'score', 'weakness', 'cv', 'summary', 'improvement']):
            latest_resume = Resume.objects.filter(user=user).order_by('-uploaded_at').first()
            if not latest_resume:
                return ("You haven't uploaded a PDF resume yet! Please go to the **Resume Analysis** section and upload your resume to calculate your ATS score and get tailored feedback.", "ResumeAgent")
            
            analysis = getattr(latest_resume, 'analysis', None)
            if not analysis:
                analysis = self.resume_agent.analyze_resume(latest_resume)

            response = f"### Resume Agent Analysis\n\n"
            response += f"**Your Current ATS Score:** {analysis.ats_score}/100\n\n"
            response += f"**Strengths:**\n" + "\n".join([f"- {s}" for s in analysis.strengths]) + "\n\n"
            response += f"**Areas for Improvement:**\n" + "\n".join([f"- {w}" for w in analysis.weaknesses]) + "\n\n"
            response += f"**Actionable Suggestions:**\n" + "\n".join([f"- {s}" for s in analysis.suggestions])
            return (response, "ResumeAgent")

        # 2. Job Agent Routing
        if any(kw in q_lower for kw in ['job', 'vacancy', 'apply', 'career', 'matching', 'hiring', 'company', 'position', 'recommend']):
            recommendations = self.job_agent.recommend_jobs(user)
            if not recommendations:
                return ("No matching jobs were found in the database. Please make sure your target career role is set in your Profile.", "JobAgent")

            top_rec = recommendations[0]
            response = f"### Job Recommendation Agent\n\n"
            response += f"Based on your profile and skills, your top job match is **{top_rec.job.title}** at **{top_rec.job.company}** with a **{top_rec.match_score}% Match Fit**.\n\n"
            response += f"**Matched Skills:** {', '.join(top_rec.matched_skills) if top_rec.matched_skills else 'None'}\n\n"
            response += f"**Missing Skills to Learn:** {', '.join(top_rec.missing_skills) if top_rec.missing_skills else 'None'}\n\n"
            response += f"**Overview:** {top_rec.explanation}\n\n"
            response += f"You can explore all {len(recommendations)} recommended job matches in the **Jobs** tab!"
            return (response, "JobAgent")

        # 3. Planner Agent Routing
        if any(kw in q_lower for kw in ['roadmap', 'learn', 'skill gap', 'curriculum', 'missing skill', 'plan', 'week', 'month', 'next']):
            gap_info = self.planner_agent.identify_skill_gap(user)
            active_roadmap = Roadmap.objects.filter(user=user).order_by('-created_at').first()
            if not active_roadmap:
                active_roadmap = self.planner_agent.generate_roadmap(user)

            tasks = active_roadmap.tasks.all()
            pending_tasks = [t.title for t in tasks if t.status != 'Completed'][:4]

            response = f"### Planner Agent Curriculum Advice\n\n"
            response += f"**Target Career Goal:** {gap_info['target_role']}\n\n"
            response += f"**Missing Skills Identified:** {', '.join(gap_info['missing_skills']) if gap_info['missing_skills'] else 'No major skill gaps!'}\n\n"
            response += f"**Next High-Priority Learning Tasks:**\n" + "\n".join([f"1. {t}" for t in pending_tasks]) + "\n\n"
            response += "You can track and check off your completed learning tasks in the **Learning Roadmap** section!"
            return (response, "PlannerAgent")

        # 4. General Career Consultation using Gemini API or Context Synthesis
        if self.api_key:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                profile = getattr(user, 'profile', None)
                target_role = profile.target_role if profile else 'Developer'
                user_skills = UserSkill.objects.filter(user=user, is_extracted=True).select_related('skill')
                skills_list = [us.skill.name for us in user_skills]

                prompt = f"""
                You are AI Career Mentor, an intelligent, empathetic career guide.
                User Context:
                - Username: {user.username}
                - Target Role: {target_role}
                - Extracted Skills: {', '.join(skills_list)}
                - User Question: "{query}"

                Provide a helpful, encouraging, structured response (with bullet points where appropriate). Keep it concise, practical, and highly relevant to their target role.
                """
                response = model.generate_content(prompt)
                return (response.text.strip(), "Orchestrator")
            except Exception as e:
                print(f"Gemini Chatbot API Fallback: {e}")

        # Local Synthesis Fallback
        profile = getattr(user, 'profile', None)
        target_role = profile.target_role if profile else 'Software Professional'
        user_skills = UserSkill.objects.filter(user=user, is_extracted=True).select_related('skill')
        skills_str = ', '.join([us.skill.name for us in user_skills]) if user_skills.exists() else 'Python, SQL'

        response = f"As your **AI Career Mentor**, I analyzed your profile for the **{target_role}** track.\n\n"
        response += f"Currently, your detected core skills include: **{skills_str}**.\n\n"
        response += f"Here are 3 key recommendations to advance your career:\n"
        response += f"1. **Resume Optimization**: Upload an updated PDF resume to verify your ATS formatting score.\n"
        response += f"2. **Targeted Skill Mastery**: Focus on mastering REST APIs, Docker, and Database optimization.\n"
        response += f"3. **Hands-on Portfolio**: Build 2 production-ready projects and showcase them on GitHub.\n\n"
        response += "Feel free to ask me specific questions about your **resume**, **job matches**, or **learning roadmap**!"
        return (response, "Orchestrator")
