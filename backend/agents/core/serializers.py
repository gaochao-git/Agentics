from rest_framework import serializers
from .models import Conversation, Message, AgentConfig, Document, DocumentVersion


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'agent_type', 'is_user_message', 'metadata', 'document_id', 'created_at']


class DocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = ['id', 'version_number', 'content', 'formatted_content', 'version_note', 
                 'operation_type', 'metadata', 'created_at']


class DocumentSerializer(serializers.ModelSerializer):
    versions = DocumentVersionSerializer(many=True, read_only=True)
    current_content = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'document_type', 'current_version', 'created_at', 
                 'updated_at', 'versions', 'current_content']
    
    def get_current_content(self, obj):
        try:
            current_version = DocumentVersion.objects.get(
                document_id=obj.id, 
                version_number=obj.current_version
            )
            return current_version.formatted_content
        except DocumentVersion.DoesNotExist:
            return ""


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'messages', 'documents']


class AgentConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentConfig
        fields = ['agent_type', 'name', 'description', 'is_enabled', 'config']


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField()
    agent_type = serializers.CharField(default='general_qa')
    conversation_id = serializers.IntegerField(required=False)
    document_id = serializers.IntegerField(required=False)


class DocumentEditRequestSerializer(serializers.Serializer):
    document_id = serializers.IntegerField()
    operation = serializers.ChoiceField(choices=['expand', 'compress', 'polish', 'edit'])
    instruction = serializers.CharField()
    target_version = serializers.IntegerField(required=False)