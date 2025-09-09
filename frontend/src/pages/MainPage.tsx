import React, { useEffect, useRef } from 'react';
import { Layout, Typography, Spin, Alert } from 'antd';
import AgentSidebar from '../components/AgentSidebar';
import ChatInput from '../components/ChatInput';
import MessageItem from '../components/MessageItem';
import { useAppStore } from '../store';
import { agentApi } from '../agents/core/api';
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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [currentConversation?.messages]);

  const handleSendMessage = async (content: string) => {
    setLoading(true);
    setError(null);

    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      agent_type: selectedAgent,
      is_user_message: true,
      created_at: new Date().toISOString()
    };

    addMessage(userMessage);

    try {
      const response = await agentApi.chat({
        message: content,
        agent_type: selectedAgent,
        conversation_id: currentConversation?.id
      });

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        agent_type: response.agent_type,
        is_user_message: false,
        metadata: {
          execution_time: response.execution_time,
          success: response.success
        },
        created_at: new Date().toISOString()
      };

      addMessage(agentMessage);

      if (!currentConversation) {
        setCurrentConversation({
          id: response.conversation_id,
          title: content.substring(0, 50) + (content.length > 50 ? '...' : ''),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          messages: [userMessage, agentMessage]
        });
      }

    } catch (err: any) {
      setError(err.response?.data?.error || '发送消息失败');
    } finally {
      setLoading(false);
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

              {loading && (
                <div style={{ textAlign: 'center', padding: '20px' }}>
                  <Spin size="large" />
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
            
            <ChatInput 
              onSendMessage={handleSendMessage}
              loading={loading}
            />
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
};

export default MainPage;