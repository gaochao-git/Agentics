from django.urls import path
from .views import ChatView, ConversationListView, AgentListView, StreamChatView, DocumentEditView, DocumentView

urlpatterns = [
    path('chat/', ChatView.as_view(), name='chat'),
    path('stream-chat/', StreamChatView.as_view(), name='stream_chat'),
    path('conversations/', ConversationListView.as_view(), name='conversations'),
    path('list/', AgentListView.as_view(), name='agent_list'),
    path('documents/', DocumentView.as_view(), name='documents'),
    path('documents/<int:document_id>/', DocumentView.as_view(), name='document_detail'),
    path('documents/edit/', DocumentEditView.as_view(), name='document_edit'),
]