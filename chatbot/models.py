from django.db import models
from django.contrib.auth.models import User

class ChatConversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_conversations')
    title = models.CharField(max_length=150, default='Career Advice Session')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.created_at.strftime('%b %d')})"

class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('ai', 'AI Career Mentor'),
    ]

    AGENT_CHOICES = [
        ('Orchestrator', 'Central Orchestrator'),
        ('ResumeAgent', 'Resume Agent'),
        ('JobAgent', 'Job Agent'),
        ('PlannerAgent', 'Planner Agent'),
    ]

    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES, default='user')
    message = models.TextField()
    agent_type = models.CharField(max_length=50, choices=AGENT_CHOICES, default='Orchestrator')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.sender.upper()} - {self.agent_type}] {self.message[:40]}..."
