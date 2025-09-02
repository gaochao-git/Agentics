import React from 'react';
import { Layout, Menu, Typography } from 'antd';
import {
  MessageOutlined,
  SoundOutlined,
  FileTextOutlined,
  BankOutlined,
  BarChartOutlined,
  CodeOutlined,
  DashboardOutlined
} from '@ant-design/icons';

const { Sider } = Layout;
const { Title } = Typography;

interface AgentSidebarProps {
  selectedAgent: string;
  onAgentSelect: (agentType: string) => void;
}

const AgentSidebar: React.FC<AgentSidebarProps> = ({ selectedAgent, onAgentSelect }) => {
  const menuItems = [
    {
      key: 'general_qa',
      icon: <MessageOutlined />,
      label: '通用问答助手'
    },
    {
      key: 'speech_writer',
      icon: <SoundOutlined />,
      label: '发言稿智能体'
    },
    {
      key: 'news_writer',
      icon: <FileTextOutlined />,
      label: '新闻稿智能体'
    },
    {
      key: 'official_document',
      icon: <BankOutlined />,
      label: '智能公文智能体'
    },
    {
      key: 'research_report',
      icon: <BarChartOutlined />,
      label: '智能研报智能体'
    },
    {
      key: 'code_assistant',
      icon: <CodeOutlined />,
      label: '智能代码智能体'
    },
    {
      key: 'data_analysis',
      icon: <DashboardOutlined />,
      label: '数据分析智能体'
    }
  ];

  return (
    <Sider width={250} style={{ background: '#fff' }}>
      <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0' }}>
        <Title level={4} style={{ margin: 0 }}>智能体选择</Title>
      </div>
      <Menu
        mode="inline"
        selectedKeys={[selectedAgent]}
        items={menuItems}
        onClick={({ key }) => onAgentSelect(key)}
        style={{ borderRight: 0 }}
      />
    </Sider>
  );
};

export default AgentSidebar;