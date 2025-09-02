import React from 'react';
import { Card, Avatar, Typography, Tag } from 'antd';
import { UserOutlined, RobotOutlined } from '@ant-design/icons';
import { Message } from '../types';

const { Text, Paragraph } = Typography;

interface MessageItemProps {
  message: Message;
}

const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  const isUser = message.is_user_message;
  
  const getAgentName = (agentType: string) => {
    const agentNames: Record<string, string> = {
      'general_qa': '通用问答助手',
      'speech_writer': '发言稿智能体',
      'news_writer': '新闻稿智能体',
      'official_document': '智能公文智能体',
      'research_report': '智能研报智能体',
      'code_assistant': '智能代码智能体',
      'data_analysis': '数据分析智能体'
    };
    return agentNames[agentType] || agentType;
  };

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: isUser ? 'flex-end' : 'flex-start',
      marginBottom: '16px'
    }}>
      <Card
        style={{ 
          maxWidth: '70%',
          background: isUser ? '#1890ff' : '#f6f6f6',
          color: isUser ? '#fff' : '#000'
        }}
        bodyStyle={{ padding: '12px 16px' }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
          <Avatar 
            icon={isUser ? <UserOutlined /> : <RobotOutlined />} 
            size="small"
            style={{ background: isUser ? '#fff' : '#1890ff', color: isUser ? '#1890ff' : '#fff' }}
          />
          <div style={{ flex: 1 }}>
            <div style={{ marginBottom: '4px' }}>
              <Text strong style={{ color: isUser ? '#fff' : '#000' }}>
                {isUser ? '用户' : getAgentName(message.agent_type)}
              </Text>
              {!isUser && (
                <Tag size="small" style={{ marginLeft: '8px' }}>
                  {message.agent_type}
                </Tag>
              )}
            </div>
            <Paragraph 
              style={{ 
                margin: 0, 
                color: isUser ? '#fff' : '#000',
                whiteSpace: 'pre-wrap'
              }}
            >
              {message.content}
            </Paragraph>
            {message.metadata?.execution_time && (
              <Text type="secondary" style={{ fontSize: '12px', color: isUser ? '#ccc' : '#666' }}>
                执行时间: {message.metadata.execution_time.toFixed(2)}s
              </Text>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default MessageItem;