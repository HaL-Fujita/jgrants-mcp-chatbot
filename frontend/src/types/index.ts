// メッセージの型定義
export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: Date;
}

// 補助金情報の型定義
export interface Subsidy {
  id: string;
  name: string;
  title: string;
  target_area: string;
  subsidy_max_limit: string;
  acceptance_start: string;
  acceptance_end: string;
  target_employees: string;
}

// 補助金検索結果の型定義
export interface SubsidySearchResult {
  success: boolean;
  count: number;
  subsidies: Subsidy[];
  error?: string;
}

// 補助金詳細の型定義
export interface SubsidyDetail extends Subsidy {
  subsidy_rate: string;
  purpose: string;
  outline: string;
  note: string;
  grant_guideline_url: string;
  application_form_files: number;
}

// チャットレスポンスの型定義
export interface ChatResponse {
  success: boolean;
  model: 'claude' | 'openai';
  response: string;
  tool_calls?: any[];
  error?: string;
}

// API レスポンスの型定義
export interface ChatApiResponse {
  responses: {
    claude?: ChatResponse;
    openai?: ChatResponse;
  };
}

// モデル選択の型定義
export type ModelType = 'both' | 'claude' | 'openai';

// モデル表示設定の型定義
export interface ModelVisibility {
  claude: boolean;
  openai: boolean;
}
