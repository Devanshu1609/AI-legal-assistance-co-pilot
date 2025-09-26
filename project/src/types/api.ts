export interface DocumentReport {
  document_id: string;
  table_of_contents?: string;
  executive_summary?: string;
  key_points?: string;
  complex_clauses?: string;
  risk_assessment?: string;
  recommendations?: string;
  unclear_missing?: string;
  appendix?: string;
  [key: string]: string | undefined;
}

export interface ChatMessage {
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}