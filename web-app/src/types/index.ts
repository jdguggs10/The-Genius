export type MessageType = {
  role: 'user' | 'assistant';
  content: string;
  id?: string;
  responseId?: string; // OpenAI response ID for state management
  structuredAdvice?: {
    main_advice: string;
    reasoning?: string;
    confidence_score?: number;
    alternatives?: Array<{
      player: string;
      reason?: string;
    }>;
    model_identifier?: string;
  };
};

export type AdviceRequest = {
  conversation?: MessageType[];
  previous_response_id?: string; // For OpenAI state management
  enable_web_search?: boolean;
  model?: string;
  prompt_type?: 'default' | 'detailed' | 'baseball' | 'football' | 'basketball';
}; 