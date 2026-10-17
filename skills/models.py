from django.db import models
from django.contrib.auth.models import User

class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('Programming Language', 'Programming Language'),
        ('Web Framework', 'Web Framework'),
        ('Database', 'Database'),
        ('Data Science & AI', 'Data Science & AI'),
        ('Cloud & DevOps', 'Cloud & DevOps'),
        ('Tools & Version Control', 'Tools & Version Control'),
        ('Soft Skills', 'Soft Skills'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Programming Language')
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.category})"

class UserSkill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='user_associations')
    is_extracted = models.BooleanField(default=True, help_text="Extracted automatically from resume")
    is_target = models.BooleanField(default=False, help_text="Target skill to learn for career goal")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'skill', 'is_target')

    def __str__(self):
        skill_type = "Target" if self.is_target else "Extracted"
        return f"{self.user.username} - {self.skill.name} ({skill_type})"
