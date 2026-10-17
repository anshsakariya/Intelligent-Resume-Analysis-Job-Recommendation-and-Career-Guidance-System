from django.db import models
from django.contrib.auth.models import User
from jobs.models import Job

class JobRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_recommendations')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='recommendations')
    match_score = models.IntegerField(default=0, help_text="Calculated match percentage (0-100)")
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-match_score']
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.username} -> {self.job.title} ({self.match_score}% Match)"
