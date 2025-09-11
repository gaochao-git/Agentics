from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import StreamingHttpResponse
from django.utils import timezone
import json
import time
from .models import Conversation, Message, AgentConfig, Document, DocumentVersion
from .serializers import (ConversationSerializer, ChatRequestSerializer, AgentConfigSerializer,
                         DocumentSerializer, DocumentEditRequestSerializer)
from .base import AgentType, AgentMessage
from .initialization import lazy_get_agent_manager
from .utils import markdown_to_plain_text, extract_title_from_content, detect_document_type
from asgiref.sync import sync_to_async
import asyncio


@method_decorator(csrf_exempt, name='dispatch')
class ChatView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """处理聊天请求"""
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        message_content = data['message']
        agent_type_str = data.get('agent_type', 'general_qa')
        conversation_id = data.get('conversation_id')
        document_id = data.get('document_id')

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
            is_user_message=True,
            document_id=document_id
        )

        try:
            # 使用同步方式运行异步代码
            response = asyncio.run(self._process_message_async(message_content, agent_type))
            
            # 创建或更新文档
            if response.success and response.content:
                document = self._create_or_update_document(
                    conversation.id, 
                    response.content, 
                    agent_type_str,
                    document_id
                )
                document_id = document.id
            
            # 创建智能体响应消息
            agent_message = Message.objects.create(
                conversation_id=conversation.id,
                content=response.content,
                agent_type=agent_type_str,
                is_user_message=False,
                document_id=document_id,
                metadata={
                    'execution_time': response.execution_time,
                    'success': response.success
                }
            )

            return Response({
                'conversation_id': conversation.id,
                'document_id': document_id,
                'response': response.content,
                'formatted_response': markdown_to_plain_text(response.content),
                'agent_type': agent_type_str,
                'success': response.success,
                'execution_time': response.execution_time
            })

        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _create_or_update_document(self, conversation_id, content, agent_type, document_id=None):
        """创建或更新文档"""
        if document_id:
            # 更新现有文档
            try:
                document = Document.objects.get(id=document_id)
                document.current_version += 1
                document.updated_at = timezone.now()
                document.save()
            except Document.DoesNotExist:
                document = None
        else:
            document = None
            
        if not document:
            # 创建新文档
            title = extract_title_from_content(content)
            doc_type = detect_document_type(content, agent_type)
            
            document = Document.objects.create(
                conversation_id=conversation_id,
                title=title,
                document_type=doc_type,
                current_version=1
            )
        
        # 创建文档版本
        DocumentVersion.objects.create(
            document_id=document.id,
            version_number=document.current_version,
            content=content,
            raw_content=content,
            formatted_content=markdown_to_plain_text(content),
            operation_type='create' if document.current_version == 1 else 'edit'
        )
        
        return document

    async def _process_message_async(self, message_content, agent_type):
        """异步处理消息"""
        agent_manager = lazy_get_agent_manager()
        return await agent_manager.process_message(message_content, agent_type)



@method_decorator(csrf_exempt, name='dispatch')
class StreamChatView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """流式输出聊天响应"""
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

        def generate_stream():
            """生成流式响应"""
            try:
                # 创建或获取对话
                if conversation_id:
                    conversation = Conversation.objects.get(id=conversation_id)
                else:
                    conversation = Conversation.objects.create(
                        user_id=request.user.id if request.user.is_authenticated else None
                    )
                
                # 发送对话ID
                yield f"data: {json.dumps({'type': 'conversation_id', 'data': conversation.id})}\n\n"
                
                # 处理消息
                response = asyncio.run(self._process_message_async(message_content, agent_type))
                
                if response.success:
                    # 分段发送内容
                    content = response.content
                    chunk_size = 50  # 每次发送的字符数
                    
                    for i in range(0, len(content), chunk_size):
                        chunk = content[i:i + chunk_size]
                        yield f"data: {json.dumps({'type': 'content', 'data': chunk})}\n\n"
                        time.sleep(0.1)  # 模拟打字机效果
                    
                    # 发送完成信号和格式化内容
                    yield f"data: {json.dumps({'type': 'complete', 'data': {'raw_content': content, 'formatted_content': markdown_to_plain_text(content)}})}\n\n"
                else:
                    yield f"data: {json.dumps({'type': 'error', 'data': response.content})}\n\n"
                    
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"

        response = StreamingHttpResponse(
            generate_stream(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['Connection'] = 'keep-alive'
        response['Access-Control-Allow-Origin'] = '*'
        return response

    async def _process_message_async(self, message_content, agent_type):
        """异步处理消息"""
        agent_manager = lazy_get_agent_manager()
        return await agent_manager.process_message(message_content, agent_type)


@method_decorator(csrf_exempt, name='dispatch')
class DocumentEditView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """编辑文档内容"""
        serializer = DocumentEditRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        document_id = data['document_id']
        operation = data['operation']
        instruction = data['instruction']
        target_version = data.get('target_version')

        try:
            document = Document.objects.get(id=document_id)
            
            # 获取目标版本内容
            if target_version:
                version = DocumentVersion.objects.get(
                    document_id=document_id, 
                    version_number=target_version
                )
                base_content = version.content
            else:
                # 使用当前版本
                version = DocumentVersion.objects.get(
                    document_id=document_id, 
                    version_number=document.current_version
                )
                base_content = version.content

            # 构建编辑指令
            edit_instruction = self._build_edit_instruction(operation, instruction, base_content)
            
            # 处理编辑请求
            response = asyncio.run(self._process_edit_async(edit_instruction))
            
            if response.success:
                # 创建新版本
                new_version_number = document.current_version + 1
                document.current_version = new_version_number
                document.save()
                
                DocumentVersion.objects.create(
                    document_id=document.id,
                    version_number=new_version_number,
                    content=response.content,
                    raw_content=response.content,
                    formatted_content=markdown_to_plain_text(response.content),
                    version_note=f"{operation}: {instruction}",
                    operation_type=operation
                )
                
                return Response({
                    'success': True,
                    'document_id': document.id,
                    'new_version': new_version_number,
                    'content': response.content,
                    'formatted_content': markdown_to_plain_text(response.content)
                })
            else:
                return Response({
                    'success': False,
                    'error': response.content
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Document.DoesNotExist:
            return Response(
                {'error': 'Document not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _build_edit_instruction(self, operation, instruction, base_content):
        """构建编辑指令"""
        operation_prompts = {
            'expand': f"请对以下内容进行扩写，具体要求：{instruction}\n\n原内容：\n{base_content}",
            'compress': f"请对以下内容进行缩写，具体要求：{instruction}\n\n原内容：\n{base_content}",
            'polish': f"请对以下内容进行润色，具体要求：{instruction}\n\n原内容：\n{base_content}",
            'edit': f"请对以下内容进行修改，具体要求：{instruction}\n\n原内容：\n{base_content}"
        }
        return operation_prompts.get(operation, f"{instruction}\n\n{base_content}")

    async def _process_edit_async(self, instruction):
        """异步处理编辑请求"""
        agent_manager = lazy_get_agent_manager()
        # 使用通用问答助手进行编辑
        return await agent_manager.process_message(instruction, AgentType.GENERAL_QA)


class DocumentView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, document_id=None):
        """获取文档详情"""
        if document_id:
            try:
                document = Document.objects.get(id=document_id)
                serializer = DocumentSerializer(document)
                return Response(serializer.data)
            except Document.DoesNotExist:
                return Response(
                    {'error': 'Document not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # 获取文档列表
            conversation_id = request.query_params.get('conversation_id')
            if conversation_id:
                documents = Document.objects.filter(conversation_id=conversation_id)
            else:
                documents = Document.objects.all()[:50]  # 限制返回数量
            
            serializer = DocumentSerializer(documents, many=True)
            return Response(serializer.data)

    def delete(self, request, document_id):
        """删除文档"""
        try:
            document = Document.objects.get(id=document_id)
            # 删除所有版本
            DocumentVersion.objects.filter(document_id=document_id).delete()
            document.delete()
            return Response({'success': True})
        except Document.DoesNotExist:
            return Response(
                {'error': 'Document not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class ConversationListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        conversations = Conversation.objects.filter(
            user_id=request.user.id if request.user.is_authenticated else None
        )
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)


class AgentListView(APIView):
    permission_classes = [AllowAny]  # 允许所有用户访问
    
    def get(self, request):
        agent_manager = lazy_get_agent_manager()
        agents = agent_manager.list_agents()
        return Response(agents)