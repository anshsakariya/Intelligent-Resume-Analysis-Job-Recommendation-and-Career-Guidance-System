from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    EXPERIENCE_LEVEL_CHOICES = [
        ('Entry Level', 'Entry Level (0-2 years)'),
        ('Mid Level', 'Mid Level (3-5 years)'),
        ('Senior Level', 'Senior Level (5+ years)'),
    ]

    TARGET_ROLE_CHOICES = [
        ('Python Developer', 'Python Developer'),
        ('Django Developer', 'Django Developer'),
        ('Full Stack Developer', 'Full Stack Developer'),
        ('Backend Developer', 'Backend Developer'),
        ('Data Analyst', 'Data Analyst'),
        ('Data Scientist', 'Data Scientist'),
        ('Machine Learning Engineer', 'Machine Learning Engineer'),
        ('AI Engineer', 'AI Engineer'),
        ('Software Developer', 'Software Developer'),
    ]

    WORK_MODE_CHOICES = [
        ('Remote', 'Remote'),
        ('Hybrid', 'Hybrid'),
        ('On-site', 'On-site'),
        ('Flexible', 'Flexible'),
    ]

    NOTICE_PERIOD_CHOICES = [
        ('Immediate', 'Immediate / Serving Notice'),
        ('15 Days', '15 Days'),
        ('30 Days', '30 Days'),
        ('60 Days', '60 Days'),
        ('90 Days', '90 Days'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True, default='')

    # Social & Portfolio Links
    linkedin_url = models.URLField(max_length=200, blank=True)
    github_url = models.URLField(max_length=200, blank=True)
    portfolio_url = models.URLField(max_length=200, blank=True)

    # Education
    education = models.CharField(max_length=100, blank=True, help_text="e.g. Master of Computer Applications (MCA)")
    degree = models.CharField(max_length=100, blank=True)
    university = models.CharField(max_length=150, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    
    # Career Details
    experience_level = models.CharField(max_length=50, choices=EXPERIENCE_LEVEL_CHOICES, default='Entry Level')
    current_role = models.CharField(max_length=100, blank=True, default='Student / Job Seeker')
    target_role = models.CharField(max_length=100, choices=TARGET_ROLE_CHOICES, default='Python Developer')
    years_of_experience = models.IntegerField(default=0)
    key_skills = models.CharField(max_length=255, blank=True, help_text="e.g. Python, Django, REST API, React, SQL")
    preferred_work_mode = models.CharField(max_length=50, choices=WORK_MODE_CHOICES, default='Remote')
    notice_period = models.CharField(max_length=50, choices=NOTICE_PERIOD_CHOICES, default='Immediate')
    expected_salary = models.CharField(max_length=50, blank=True, help_text="e.g. ₹6,00,000 - ₹10,00,000 / yr or 10 LPA")
    career_goal = models.TextField(blank=True, default='Looking to build a successful career in software development and AI.')

    # Profile Picture
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, help_text="Profile picture (JPG, PNG, max 2MB)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.target_role})"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, full_name=f"{instance.first_name} {instance.last_name}".strip() or instance.username)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
