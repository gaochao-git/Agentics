from django.urls import path
from .views import ChatView, ConversationListView, AgentListView

urlpatterns = [
    path('chat/', ChatView.as_view(), name='chat'),
    path('conversations/', ConversationListView.as_view(), name='conversations'),
    path('list/', AgentListView.as_view(), name='agent_list'),
]