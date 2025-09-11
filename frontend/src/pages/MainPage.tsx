import React, { useEffect, useRef, useState } from 'react';
import { Layout, Typography, Spin, Alert } from 'antd';
import AgentSidebar from '../components/AgentSidebar';
import ChatInput from '../components/ChatInput';
import MessageItem from '../components/MessageItem';
import StreamOutput from '../components/StreamOutput';
import { useAppStore } from '../store';
import { agentApi } from '../agents/core/api';
import { useStreaming } from '../hooks/useStreaming';
import { Message } from '../types';

const { Header, Content } = Layout;
const { Title } = Typography;

const MainPage: React.FC = () => {
  const {
    selectedAgent,
    currentConversation,
    loading,
    error,
    setSelectedAgent,
    setCurrentConversation,
    setLoading,
    setError,
    addMessage
  } = useAppStore();

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [streamingMessage, setStreamingMessage] = useState<{
    userMessage: Message;
    conversationId?: number;
    documentId?: number;
    rawContent?: string;
  } | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [currentConversation?.messages, streamingMessage]);

  const { isStreaming, streamContent, startStream, stopStream } = useStreaming({
    onComplete: (data) => {
      if (streamingMessage) {
        const agentMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: data.raw_content,
          agent_type: selectedAgent,
          is_user_message: false,
          created_at: new Date().toISOString()
        };

        addMessage(agentMessage);

        if (!currentConversation && streamingMessage.conversationId) {
          setCurrentConversation({
            id: streamingMessage.conversationId,
            title: streamingMessage.userMessage.content.substring(0, 50) + 
                   (streamingMessage.userMessage.content.length > 50 ? '...' : ''),
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            messages: [streamingMessage.userMessage, agentMessage]
          });
        }
      }
      setStreamingMessage(null);
    },
    onError: (error) => {
      setError(error);
      setStreamingMessage(null);
    },
    onConversationId: (conversationId) => {
      if (streamingMessage) {
        setStreamingMessage(prev => ({ ...prev!, conversationId }));
      }
    }
  });

  const handleSendMessage = async (content: string) => {
    setError(null);

    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      agent_type: selectedAgent,
      is_user_message: true,
      created_at: new Date().toISOString()
    };

    addMessage(userMessage);
    setStreamingMessage({
      userMessage,
      conversationId: currentConversation?.id
    });

    // 启动流式响应
    startStream(content, selectedAgent, currentConversation?.id);
  };

  const handleCopy = () => {
    // 可以添加复制成功的提示
    console.log('Content copied to clipboard');
  };

  const handleRegenerate = () => {
    if (streamingMessage) {
      // 重新生成当前响应
      startStream(
        streamingMessage.userMessage.content, 
        selectedAgent, 
        streamingMessage.conversationId
      );
    }
  };

  const handleEdit = async (instruction: string, operation: 'expand' | 'compress' | 'polish' | 'edit') => {
    if (!streamingMessage?.documentId) {
      setError('无法编辑：未找到关联文档');
      return;
    }

    try {
      const response = await agentApi.editDocument({
        document_id: streamingMessage.documentId,
        operation,
        instruction
      });

      if (response.success) {
        // 更新显示内容
        // 这里可以添加版本管理逻辑
        console.log('Document edited successfully:', response);
      }
    } catch (err: any) {
      setError(err.response?.data?.error || '编辑失败');
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#fff', padding: '0 24px', borderBottom: '1px solid #f0f0f0' }}>
        <Title level={3} style={{ margin: 0, lineHeight: '64px' }}>
          企业智能体系统
        </Title>
      </Header>
      
      <Layout>
        <AgentSidebar 
          selectedAgent={selectedAgent} 
          onAgentSelect={setSelectedAgent}
        />
        
        <Layout style={{ padding: '0' }}>
          <Content style={{ 
            display: 'flex', 
            flexDirection: 'column',
            height: 'calc(100vh - 64px)'
          }}>
            <div style={{ 
              flex: 1, 
              padding: '16px', 
              overflowY: 'auto',
              background: '#f5f5f5'
            }}>
              {error && (
                <Alert
                  message="错误"
                  description={error}
                  type="error"
                  closable
                  onClose={() => setError(null)}
                  style={{ marginBottom: '16px' }}
                />
              )}

              {currentConversation?.messages.map((message: Message) => (
                <MessageItem key={message.id} message={message} />
              ))}

              {/* 流式输出显示 */}
              {streamingMessage && (
                <div style={{ marginBottom: '16px' }}>
                  <MessageItem message={streamingMessage.userMessage} />
                  <StreamOutput
                    content={streamContent}
                    rawContent={streamingMessage.rawContent || streamContent}
                    isStreaming={isStreaming}
                    onCopy={handleCopy}
                    onRegenerate={handleRegenerate}
                    onEdit={handleEdit}
                    documentId={streamingMessage.documentId}
                  />
                </div>
              )}

              {loading && !isStreaming && (
                <div style={{ textAlign: 'center', padding: '20px' }}>
                  <Spin size="large" />
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
            
            <ChatInput 
              onSendMessage={handleSendMessage}
              loading={isStreaming || loading}
            />
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
};

export default MainPage;