from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/agents/', include('agents.core.urls')),
    path('api/agents/general-qa/', include('agents.general_qa.urls')),
    path('api/agents/speech-writer/', include('agents.speech_writer.urls')),
    path('api/agents/news-writer/', include('agents.news_writer.urls')),
    path('api/agents/official-document/', include('agents.official_document.urls')),
    path('api/agents/research-report/', include('agents.research_report.urls')),
    path('api/agents/code-assistant/', include('agents.code_assistant.urls')),
    path('api/agents/data-analysis/', include('agents.data_analysis.urls')),
]