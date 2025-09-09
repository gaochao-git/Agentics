import axios from 'axios';
import { ChatRequest, ChatResponse, Conversation, Agent } from '../../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

export const agentApi = {
  chat: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post('/agents/chat/', request);
    return response.data;
  },

  getConversations: async (): Promise<Conversation[]> => {
    const response = await apiClient.get('/agents/conversations/');
    return response.data;
  },

  getAgents: async (): Promise<Agent[]> => {
    const response = await apiClient.get('/agents/list/');
    return response.data;
  },

  getConversation: async (id: number): Promise<Conversation> => {
    const response = await apiClient.get(`/agents/conversations/${id}/`);
    return response.data;
  }
};

export default agentApi;