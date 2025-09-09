import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Loader2, Sparkles } from 'lucide-react';
import { agentApi } from '../core/api';
import { ChatMessage, Agent } from '../../types';

interface GeneralQAChatProps {
  conversationId?: number;
  onNewConversation?: (id: number) => void;
}

const GeneralQAChat: React.FC<GeneralQAChatProps> = ({ 
  conversationId, 
  onNewConversation 
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [agent, setAgent] = useState<Agent | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadAgentInfo();
    if (conversationId) {
      loadConversation(conversationId);
    }
  }, [conversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadAgentInfo = async () => {
    try {
      const agents = await agentApi.getAgents();
      const generalAgent = agents.find(a => a.type === 'general_qa');
      setAgent(generalAgent || null);
    } catch (error) {
      console.error('Failed to load agent info:', error);
    }
  };

  const loadConversation = async (id: number) => {
    try {
      const conversation = await agentApi.getConversation(id);
      const chatMessages: ChatMessage[] = (conversation.messages || []).map(msg => ({
        id: parseInt(msg.id),
        content: msg.content,
        role: msg.is_user_message ? 'user' : 'assistant',
        timestamp: msg.created_at,
        metadata: msg.metadata
      }));
      setMessages(chatMessages);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now(),
      content: input,
      role: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await agentApi.chat({
        message: input,
        agent_type: 'general_qa',
        conversation_id: conversationId
      });

      const botMessage: ChatMessage = {
        id: Date.now() + 1,
        content: response.content,
        role: 'assistant',
        timestamp: new Date().toISOString(),
        metadata: response.metadata
      };

      setMessages(prev => [...prev, botMessage]);

      if (!conversationId && response.conversation_id && onNewConversation) {
        onNewConversation(response.conversation_id);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: ChatMessage = {
        id: Date.now() + 1,
        content: '抱歉，处理消息时出现错误。请稍后再试。',
        role: 'assistant',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatMessage = (content: string) => {
    return content.split('\n').map((line, index) => (
      <span key={index}>
        {line}
        {index < content.split('\n').length - 1 && <br />}
      </span>
    ));
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4 rounded-t-lg">
        <div className="flex items-center space-x-3">
          <div className="bg-white/20 p-2 rounded-full">
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-semibold">{agent?.name || '通用问答助手'}</h2>
            <p className="text-sm text-white/80">
              {agent?.description || '智能对话助手，支持多种场景问答'}
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <Bot className="w-16 h-16 mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-600 mb-2">
              欢迎使用通用问答助手
            </h3>
            <p className="text-gray-500">
              我可以回答各种问题，也可以帮您连接到其他专业智能体。
            </p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex items-start space-x-2 max-w-xs lg:max-w-md`}>
              {message.role === 'assistant' && (
                <div className="bg-blue-100 p-2 rounded-full">
                  <Bot className="w-4 h-4 text-blue-600" />
                </div>
              )}
              <div
                className={`px-4 py-2 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <div className="text-sm">
                  {formatMessage(message.content)}
                </div>
                {message.metadata && (
                  <div className="mt-2 text-xs opacity-70">
                    {message.metadata.current_agent && (
                      <span>当前智能体: {message.metadata.current_agent}</span>
                    )}
                  </div>
                )}
              </div>
              {message.role === 'user' && (
                <div className="bg-purple-100 p-2 rounded-full">
                  <User className="w-4 h-4 text-purple-600" />
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-2">
              <div className="bg-blue-100 p-2 rounded-full">
                <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />
              </div>
              <div className="px-4 py-2 bg-gray-100 rounded-lg">
                <div className="text-sm text-gray-600">正在思考...</div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4">
        <div className="flex space-x-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入您的问题..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows={1}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default GeneralQAChat;