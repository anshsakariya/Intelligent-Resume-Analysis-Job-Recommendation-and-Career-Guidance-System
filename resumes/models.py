from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to='resumes/%Y/%m/')
    original_name = models.CharField(max_length=255, blank=True, help_text="Original uploaded filename")
    extracted_text = models.TextField(blank=True)
    ats_score = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Resume ({self.uploaded_at.strftime('%Y-%m-%d')})"

class ResumeAnalysis(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='analysis')
    ats_score = models.IntegerField(default=0)
    
    # Detailed Metric Breakdown
    skills_score = models.IntegerField(default=0)
    keyword_score = models.IntegerField(default=0)
    experience_score = models.IntegerField(default=0)
    projects_score = models.IntegerField(default=0)
    education_score = models.IntegerField(default=0)
    structure_score = models.IntegerField(default=0)
    
    # NLP Insights
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    suggestions = models.JSONField(default=list)
    detected_sections = models.JSONField(default=dict)
    
    analyzed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analysis for {self.resume.user.username} - ATS: {self.ats_score}/100"
