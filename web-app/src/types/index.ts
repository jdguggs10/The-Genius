export type MessageType = {
  role: 'user' | 'assistant';
  content: string;
  id?: string;
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