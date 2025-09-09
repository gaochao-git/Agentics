import { create } from 'zustand';
import { Agent, Conversation, Message } from '../types';

interface AppState {
  agents: Agent[];
  conversations: Conversation[];
  currentConversation: Conversation | null;
  selectedAgent: string;
  loading: boolean;
  error: string | null;
  
  setAgents: (agents: Agent[]) => void;
  setConversations: (conversations: Conversation[]) => void;
  setCurrentConversation: (conversation: Conversation | null) => void;
  setSelectedAgent: (agentType: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  addMessage: (message: Message) => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  agents: [],
  conversations: [],
  currentConversation: null,
  selectedAgent: 'general_qa',
  loading: false,
  error: null,

  setAgents: (agents) => set({ agents }),
  setConversations: (conversations) => set({ conversations }),
  setCurrentConversation: (conversation) => set({ currentConversation: conversation }),
  setSelectedAgent: (agentType) => set({ selectedAgent: agentType }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  
  addMessage: (message) => {
    const { currentConversation } = get();
    if (currentConversation) {
      const updatedConversation = {
        ...currentConversation,
        messages: [...currentConversation.messages, message]
      };
      set({ currentConversation: updatedConversation });
    }
  }
}));