import React, { useState, useEffect } from 'react';
import GeneralQAChat from './GeneralQAChat';
import { agentApi } from '../core/api';
import { Conversation } from '../../types';
import { Plus, MessageCircle, Clock } from 'lucide-react';

const GeneralQAPage: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversationId, setSelectedConversationId] = useState<number | undefined>();
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const data = await agentApi.getConversations();
      setConversations(data.filter(c => c.agent_type === 'general_qa'));
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const handleNewConversation = async (id: number) => {
    setSelectedConversationId(id);
    await loadConversations();
  };

  const createNewConversation = () => {
    setSelectedConversationId(undefined);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) {
      return '刚刚';
    } else if (diffHours < 24) {
      return `${diffHours}小时前`;
    } else if (diffDays < 7) {
      return `${diffDays}天前`;
    } else {
      return date.toLocaleDateString('zh-CN');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">通用问答助手</h1>
          <p className="text-gray-600">智能对话助手，支持多种场景问答和专业智能体路由</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow">
              <div className="p-4 border-b">
                <button
                  onClick={createNewConversation}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                >
                  <Plus className="w-4 h-4" />
                  <span>新建对话</span>
                </button>
              </div>

              <div className="p-4">
                <h3 className="text-sm font-medium text-gray-700 mb-3">历史对话</h3>
                <div className="space-y-2">
                  {conversations.map((conversation) => (
                    <button
                      key={conversation.id}
                      onClick={() => setSelectedConversationId(conversation.id)}
                      className={`w-full text-left p-3 rounded-lg transition-colors ${
                        selectedConversationId === conversation.id
                          ? 'bg-blue-50 border-blue-200 border'
                          : 'hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <MessageCircle className="w-4 h-4 text-gray-400 mt-0.5" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {conversation.title || '新对话'}
                          </p>
                          <div className="flex items-center space-x-1 text-xs text-gray-500 mt-1">
                            <Clock className="w-3 h-3" />
                            <span>{formatDate(conversation.updated_at)}</span>
                          </div>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>

                {conversations.length === 0 && (
                  <div className="text-center py-8">
                    <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-sm text-gray-500">暂无历史对话</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Chat Area */}
          <div className="lg:col-span-3">
            <div className="h-[600px]">
              <GeneralQAChat
                conversationId={selectedConversationId}
                onNewConversation={handleNewConversation}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GeneralQAPage;