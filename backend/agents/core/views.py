from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Conversation, Message, AgentConfig
from .serializers import ConversationSerializer, ChatRequestSerializer, AgentConfigSerializer
from .base import AgentType, AgentMessage
from .initialization import lazy_get_agent_manager
from asgiref.sync import sync_to_async
import asyncio


@method_decorator(csrf_exempt, name='dispatch')
class ChatView(APIView):
    permission_classes = [AllowAny]  # 允许所有用户访问
    
    def post(self, request):
        """处理聊天请求"""
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

        # 处理对话
        if conversation_id:
            try:
                conversation = Conversation.objects.get(
                    id=conversation_id, 
                    user_id=request.user.id if request.user.is_authenticated else None
                )
            except Conversation.DoesNotExist:
                return Response(
                    {'error': 'Conversation not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            conversation = Conversation.objects.create(
                user_id=request.user.id if request.user.is_authenticated else None
            )

        # 创建用户消息
        user_message = Message.objects.create(
            conversation_id=conversation.id,
            content=message_content,
            agent_type=agent_type_str,
            is_user_message=True
        )

        try:
            # 使用同步方式运行异步代码
            response = asyncio.run(self._process_message_async(message_content, agent_type))
            
            # 创建智能体响应消息
            agent_message = Message.objects.create(
                conversation_id=conversation.id,
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

    async def _process_message_async(self, message_content, agent_type):
        """异步处理消息"""
        agent_manager = lazy_get_agent_manager()
        return await agent_manager.process_message(message_content, agent_type)


class ConversationListView(APIView):
    permission_classes = [AllowAny]  # 允许所有用户访问
    
    def get(self, request):
        conversations = Conversation.objects.filter(user=request.user if request.user.is_authenticated else None)
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)


class AgentListView(APIView):
    permission_classes = [AllowAny]  # 允许所有用户访问
    
    def get(self, request):
        agent_manager = lazy_get_agent_manager()
        agents = agent_manager.list_agents()
        return Response(agents)