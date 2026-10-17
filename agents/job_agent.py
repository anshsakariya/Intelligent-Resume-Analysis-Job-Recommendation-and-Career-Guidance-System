from jobs.services import recommend_jobs_for_user

class JobAgent:
    """
    Agent responsible for analyzing user skills, target career goal,
    matching against available job postings, and providing job advice.
    """

    def recommend_jobs(self, user, force_refresh=False):
        """
        Calculates and ranks job matches for the user.
        """
        return recommend_jobs_for_user(user, force_refresh=force_refresh)

    def explain_job_match(self, job_recommendation):
        """
        Generates detailed summary text for a specific job match.
        """
        job = job_recommendation.job
        score = job_recommendation.match_score
        matched = job_recommendation.matched_skills
        missing = job_recommendation.missing_skills

        summary = f"### Job Fit Summary for {job.title} at {job.company}\n\n"
        summary += f"**Overall Fit Score:** {score}%\n\n"
        summary += f"**Key Matched Skills ({len(matched)}):** {', '.join(matched) if matched else 'None'}\n\n"
        summary += f"**Skill Gap ({len(missing)}):** {', '.join(missing) if missing else 'All key skills present!'}\n\n"
        summary += f"**Recommendation:** {job_recommendation.explanation}"
        return summary
