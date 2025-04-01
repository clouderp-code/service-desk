export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

export interface Article {
  id: string;
  title: string;
  content: string;
}

export interface AnalyticsData {
  responseTime: number;
  userSatisfaction: number;
  queryCount: number;
}

export interface ChatResponse {
  id: string;
  text: string;
  error?: string;
}
