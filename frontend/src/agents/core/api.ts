import axios from 'axios';
import { ChatRequest, ChatResponse, Conversation, Agent, DocumentEditRequest, DocumentEditResponse } from '../../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

export const agentApi = {
  chat: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post('/agents/core/chat/', request);
    return response.data;
  },

  getConversations: async (): Promise<Conversation[]> => {
    const response = await apiClient.get('/agents/core/conversations/');
    return response.data;
  },

  getAgents: async (): Promise<Agent[]> => {
    const response = await apiClient.get('/agents/core/list/');
    return response.data;
  },

  getConversation: async (id: number): Promise<Conversation> => {
    const response = await apiClient.get(`/agents/core/conversations/${id}/`);
    return response.data;
  },

  editDocument: async (request: DocumentEditRequest): Promise<DocumentEditResponse> => {
    const response = await apiClient.post('/agents/core/documents/edit/', request);
    return response.data;
  },

  getDocuments: async (conversationId?: number) => {
    const params = conversationId ? { conversation_id: conversationId } : {};
    const response = await apiClient.get('/agents/core/documents/', { params });
    return response.data;
  },

  getDocument: async (documentId: number) => {
    const response = await apiClient.get(`/agents/core/documents/${documentId}/`);
    return response.data;
  }
};

export default agentApi;