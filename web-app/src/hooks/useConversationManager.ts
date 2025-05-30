import { useState, useCallback } from 'react';
import type { MessageType } from '../types';

interface ConversationState {
  messages: MessageType[];
  lastResponseId: string | null;
}

export function useConversationManager() {
  const [conversationState, setConversationState] = useState<ConversationState>({
    messages: [],
    lastResponseId: null
  });

  const addMessage = useCallback((message: MessageType) => {
    setConversationState(prev => ({
      ...prev,
      messages: [...prev.messages, message]
    }));
  }, []);

  const updateMessage = useCallback((messageId: string, updates: Partial<MessageType>) => {
    setConversationState(prev => ({
      ...prev,
      messages: prev.messages.map(msg => 
        msg.id === messageId ? { ...msg, ...updates } : msg
      )
    }));
  }, []);

  const setLastResponseId = useCallback((responseId: string | null) => {
    setConversationState(prev => ({
      ...prev,
      lastResponseId: responseId
    }));
  }, []);

  const clearConversation = useCallback(() => {
    setConversationState({
      messages: [],
      lastResponseId: null
    });
  }, []);

  const getConversationForAPI = useCallback(() => {
    // Return the conversation in the format expected by the backend
    return conversationState.messages.filter(msg => msg.content.trim() !== '');
  }, [conversationState.messages]);

  return {
    messages: conversationState.messages,
    lastResponseId: conversationState.lastResponseId,
    addMessage,
    updateMessage,
    setLastResponseId,
    clearConversation,
    getConversationForAPI
  };
} 