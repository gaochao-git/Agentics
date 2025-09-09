from django.db import models
from django.contrib.auth.models import User


class Conversation(models.Model):
    title = models.CharField(max_length=200, default='新对话')
    agent_type = models.CharField(max_length=50, default='general_qa')
    user_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'general_qa_conversations'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} - {self.agent_type}"


class Message(models.Model):
    ROLE_CHOICES = [
        ('user', '用户'),
        ('assistant', '助手'),
        ('system', '系统')
    ]
    
    conversation_id = models.IntegerField()
    content = models.TextField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'general_qa_messages'
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."