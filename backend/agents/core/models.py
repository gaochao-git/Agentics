from django.db import models
from django.contrib.auth.models import User


class Conversation(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']


class Document(models.Model):
    """文档模型，用于版本控制"""
    id = models.AutoField(primary_key=True)
    conversation_id = models.IntegerField()
    title = models.CharField(max_length=200, default="未命名文档")
    document_type = models.CharField(max_length=50)  # 文档类型
    current_version = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']


class DocumentVersion(models.Model):
    """文档版本模型"""
    id = models.AutoField(primary_key=True)
    document_id = models.IntegerField()
    version_number = models.IntegerField()
    content = models.TextField()
    raw_content = models.TextField()  # markdown原文
    formatted_content = models.TextField()  # 格式化后的纯文本
    version_note = models.CharField(max_length=500, blank=True)  # 版本说明
    operation_type = models.CharField(max_length=50)  # 操作类型：create, edit, expand, compress, polish
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_number']
        unique_together = ['document_id', 'version_number']


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    conversation_id = models.IntegerField()
    document_id = models.IntegerField(null=True, blank=True)  # 关联的文档ID
    content = models.TextField()
    agent_type = models.CharField(max_length=50)
    is_user_message = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class AgentConfig(models.Model):
    agent_type = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_enabled = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)