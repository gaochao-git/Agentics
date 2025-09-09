from django.urls import path
from .views import GeneralQAView, get_conversations, get_conversation

urlpatterns = [
    path('chat/', GeneralQAView.as_view(), name='general_qa_chat'),
    path('conversations/', get_conversations, name='general_qa_conversations'),
    path('conversations/<int:conversation_id>/', get_conversation, name='general_qa_conversation'),
]