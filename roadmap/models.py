from django.db import models
from django.contrib.auth.models import User

class Roadmap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roadmaps')
    target_role = models.CharField(max_length=100)
    hours_per_day = models.IntegerField(default=2)
    days_per_week = models.IntegerField(default=5)
    target_completion_date = models.DateField(null=True, blank=True)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s Roadmap for {self.target_role}"

class RoadmapTask(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        ('High Priority', 'High Priority'),
        ('Medium Priority', 'Medium Priority'),
        ('Low Priority', 'Low Priority'),
    ]

    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    phase_name = models.CharField(max_length=100, default='Month 1: Fundamentals')
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default='High Priority')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    estimated_hours = models.IntegerField(default=10)
    order = models.IntegerField(default=1)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"[{self.status}] {self.title} ({self.phase_name})"
