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

export interface ChatMessage {
  id: number;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
  agent_type?: string;
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
  content: string;
  metadata: Record<string, any>;
  agent_type: string;
  success: boolean;
  execution_time: number;
}

export interface DocumentVersion {
  id: number;
  version_number: number;
  formatted_content: string;
  version_note: string;
  operation_type: string;
  created_at: string;
}

export interface Document {
  id: number;
  conversation_id: number;
  title: string;
  document_type: string;
  current_version: number;
  created_at: string;
  updated_at: string;
  versions?: DocumentVersion[];
}

export interface DocumentEditRequest {
  document_id: number;
  operation: 'expand' | 'compress' | 'polish' | 'edit';
  instruction: string;
  target_version?: number;
}

export interface DocumentEditResponse {
  success: boolean;
  document_id: number;
  new_version: number;
  content: string;
  formatted_content: string;
  error?: string;
}