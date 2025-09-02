from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import Conversation, Message, AgentConfig
from .serializers import ConversationSerializer, ChatRequestSerializer, AgentConfigSerializer
from .base import AgentType, AgentMessage
from .initialization import agent_manager
import asyncio


class ChatView(APIView):
    async def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        message_content = data['message']
        agent_type_str = data.get('agent_type', 'general_qa')
        conversation_id = data.get('conversation_id')

        try:
            agent_type = AgentType(agent_type_str)
        except ValueError:
            return Response(
                {'error': f'Invalid agent type: {agent_type_str}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id, user=request.user)
            except Conversation.DoesNotExist:
                return Response(
                    {'error': 'Conversation not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            conversation = Conversation.objects.create(user=request.user)

        user_message = Message.objects.create(
            conversation=conversation,
            content=message_content,
            agent_type=agent_type_str,
            is_user_message=True
        )

        try:
            response = await agent_manager.process_message(message_content, agent_type)
            
            agent_message = Message.objects.create(
                conversation=conversation,
                content=response.content,
                agent_type=agent_type_str,
                is_user_message=False,
                metadata={
                    'execution_time': response.execution_time,
                    'success': response.success
                }
            )

            return Response({
                'conversation_id': conversation.id,
                'response': response.content,
                'agent_type': agent_type_str,
                'success': response.success,
                'execution_time': response.execution_time
            })

        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConversationListView(APIView):
    def get(self, request):
        conversations = Conversation.objects.filter(user=request.user)
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)


class AgentListView(APIView):
    def get(self, request):
        agents = agent_manager.list_agents()
        return Response(agents)