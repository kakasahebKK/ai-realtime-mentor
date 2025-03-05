export interface Message {
    id: string;
    role: 'customer' | 'support agent';
    content: string;
    timestamp: string;
  }
  
  export interface SentimentData {
    sentiment: string;
    score: number;
    reason: string;
  }
  
  export interface ChatResponse {
    message: Message;
    sentiment: SentimentData;
    suggestions: string[];
  }
  
  export type ConnectionStatusType = 'connecting' | 'connected' | 'disconnected' | 'error';
