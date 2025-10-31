import axios from 'axios';
import type { Message, ChatApiResponse, SubsidySearchResult, SubsidyDetail } from '../types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * チャットメッセージを送信
 */
export async function sendChatMessage(
  messages: Message[],
  model: 'both' | 'claude' | 'openai' = 'both'
): Promise<ChatApiResponse> {
  const response = await apiClient.post<ChatApiResponse>('/api/chat', {
    messages,
    model,
  });
  return response.data;
}

/**
 * 補助金を検索
 */
export async function searchSubsidies(
  keyword: string,
  acceptance?: number,
  targetArea?: string,
  sort: string = 'created_date',
  order: string = 'DESC'
): Promise<SubsidySearchResult> {
  const response = await apiClient.post<SubsidySearchResult>('/api/subsidies/search', {
    keyword,
    acceptance,
    target_area: targetArea,
    sort,
    order,
  });
  return response.data;
}

/**
 * 募集中の補助金を検索
 */
export async function searchActiveSubsidies(
  keyword: string,
  targetArea?: string
): Promise<SubsidySearchResult> {
  const response = await apiClient.get<SubsidySearchResult>('/api/subsidies/active', {
    params: { keyword, target_area: targetArea },
  });
  return response.data;
}

/**
 * 補助金の詳細を取得
 */
export async function getSubsidyDetail(subsidyId: string): Promise<{ success: boolean; subsidy: SubsidyDetail; error?: string }> {
  const response = await apiClient.post('/api/subsidies/detail', {
    subsidy_id: subsidyId,
  });
  return response.data;
}

/**
 * ヘルスチェック
 */
export async function healthCheck(): Promise<{ status: string; api_keys: any }> {
  const response = await apiClient.get('/api/health');
  return response.data;
}
