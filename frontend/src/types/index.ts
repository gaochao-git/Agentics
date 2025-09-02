export enum AgentType {
  GENERAL_QA = 'general_qa',
  SPEECH_WRITER = 'speech_writer',
  NEWS_WRITER = 'news_writer',
  OFFICIAL_DOCUMENT = 'official_document',
  RESEARCH_REPORT = 'research_report',
  CODE_ASSISTANT = 'code_assistant',
  DATA_ANALYSIS = 'data_analysis'
}

export interface Message {
  id: string;
  content: string;
  agent_type: string;
  is_user_message: boolean;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

export interface Agent {
  type: string;
  name: string;
  description: string;
  capabilities: string[];
}

export interface ChatRequest {
  message: string;
  agent_type?: string;
  conversation_id?: number;
}

export interface ChatResponse {
  conversation_id: number;
  response: string;
  agent_type: string;
  success: boolean;
  execution_time: number;
}