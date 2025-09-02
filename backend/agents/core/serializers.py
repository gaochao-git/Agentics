from rest_framework import serializers
from .models import Conversation, Message, AgentConfig


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'agent_type', 'is_user_message', 'metadata', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'messages']


class AgentConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentConfig
        fields = ['agent_type', 'name', 'description', 'is_enabled', 'config']


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField()
    agent_type = serializers.CharField(default='general_qa')
    conversation_id = serializers.IntegerField(required=False)