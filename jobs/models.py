from django.db import models
from django.contrib.auth.models import User
from skills.models import Skill
from resumes.models import Resume

class Job(models.Model):
    EXPERIENCE_CHOICES = [
        ('Entry Level', 'Entry Level (0-2 years)'),
        ('Mid Level', 'Mid Level (3-5 years)'),
        ('Senior Level', 'Senior Level (5+ years)'),
    ]

    EMPLOYMENT_CHOICES = [
        ('Full-Time', 'Full-Time'),
        ('Part-Time', 'Part-Time'),
        ('Contract', 'Contract'),
        ('Remote', 'Remote'),
    ]

    title = models.CharField(max_length=150)
    company = models.CharField(max_length=150)
    description = models.TextField()
    required_skills = models.ManyToManyField(Skill, related_name='required_in_jobs')
    preferred_skills = models.ManyToManyField(Skill, related_name='preferred_in_jobs', blank=True)
    experience_level = models.CharField(max_length=50, choices=EXPERIENCE_CHOICES, default='Entry Level')
    location = models.CharField(max_length=100, default='Remote / Hybrid')
    salary = models.CharField(max_length=100, default='$80,000 - $110,000 / year')
    employment_type = models.CharField(max_length=50, choices=EMPLOYMENT_CHOICES, default='Full-Time')
    posted_date = models.DateTimeField(auto_now_add=True)
    application_url = models.URLField(default='https://example.com/careers')
    is_sample_data = models.BooleanField(default=True, help_text="Designates realistic sample benchmark job data")

    class Meta:
        ordering = ['-posted_date']

    def __str__(self):
        return f"{self.title} at {self.company}"


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('Submitted', 'Submitted'),
        ('Under Review', 'Under Review'),
        ('Shortlisted', 'Shortlisted'),
        ('Interviewing', 'Interviewing'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    experience_years = models.CharField(max_length=50, blank=True, default='0-2 years')
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True, related_name='job_applications')
    custom_resume_file = models.FileField(upload_to='application_resumes/%Y/%m/', blank=True, null=True)
    cover_letter = models.TextField(blank=True, help_text="Why are you a good fit for this role?")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Submitted')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-applied_at']
        unique_together = ('job', 'user')

    def __str__(self):
        return f"{self.full_name} - {self.job.title} ({self.status})"

