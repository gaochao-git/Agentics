from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
import json
import asyncio
from asgiref.sync import sync_to_async
from agents.core.base import AgentMessage, AgentType
from .agent import GeneralQAAgent


class GeneralQAView(View):
    def __init__(self):
        super().__init__()
        self.agent = GeneralQAAgent()

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    async def post(self, request):
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            conversation_id = data.get('conversation_id')
            
            agent_message = AgentMessage(
                id=str(conversation_id) if conversation_id else None,
                content=message,
                agent_type=AgentType.GENERAL_QA,
                timestamp=None
            )

            response = await self.agent.process(agent_message)
            
            return JsonResponse({
                'success': response.success,
                'content': response.content,
                'agent_type': response.agent_type.value,
                'execution_time': response.execution_time,
                'metadata': response.metadata,
                'conversation_id': conversation_id
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'content': f'处理请求时发生错误: {str(e)}',
                'error': str(e)
            }, status=500)

    async def get(self, request):
        """获取智能体信息"""
        return JsonResponse({
            'agent_type': 'general_qa',
            'name': '通用问答助手',
            'description': '基于LangGraph的智能通用问答助手',
            'capabilities': self.agent.get_capabilities()
        })


@sync_to_async
def get_conversations(request):
    """获取对话列表"""
    # 这里应该从数据库获取，暂时返回模拟数据
    conversations = [
        {
            'id': 1,
            'title': '关于Python的问题',
            'agent_type': 'general_qa',
            'created_at': '2024-01-15T10:30:00Z',
            'updated_at': '2024-01-15T10:35:00Z',
            'message_count': 5
        },
        {
            'id': 2,
            'title': '如何写发言稿',
            'agent_type': 'general_qa',
            'created_at': '2024-01-14T15:20:00Z',
            'updated_at': '2024-01-14T15:25:00Z',
            'message_count': 3
        }
    ]
    return JsonResponse(conversations, safe=False)


@sync_to_async
def get_conversation(request, conversation_id):
    """获取特定对话"""
    # 这里应该从数据库获取，暂时返回模拟数据
    conversation = {
        'id': conversation_id,
        'title': f'对话 #{conversation_id}',
        'agent_type': 'general_qa',
        'messages': [
            {
                'id': 1,
                'content': '你好，我想了解Python的基础知识',
                'role': 'user',
                'timestamp': '2024-01-15T10:30:00Z'
            },
            {
                'id': 2,
                'content': '你好！我很乐意为您介绍Python的基础知识。Python是一种高级编程语言，以其简洁易读的语法而闻名...',
                'role': 'assistant',
                'timestamp': '2024-01-15T10:30:05Z'
            }
        ]
    }
    return JsonResponse(conversation)