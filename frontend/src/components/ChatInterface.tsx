'use client';

import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import { sendChatMessage } from '../lib/api';
import type { Message, ModelVisibility, ChatResponse } from '../types';

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [claudeMessages, setClaudeMessages] = useState<Message[]>([]);
  const [openaiMessages, setOpenaiMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [modelVisibility, setModelVisibility] = useState<ModelVisibility>({
    claude: true,
    openai: true,
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const claudeEndRef = useRef<HTMLDivElement>(null);
  const openaiEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    claudeEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    openaiEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, claudeMessages, openaiMessages]);

  const handleSend = async () => {
    console.log('handleSend called', { inputValue, isLoading });
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    // 共通メッセージリストに追加
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputValue('');

    // ユーザーメッセージをすぐに両方のチャットに表示
    const updatedClaudeMessages = [...claudeMessages, userMessage];
    const updatedOpenaiMessages = [...openaiMessages, userMessage];

    console.log('Setting user message in both chats:', userMessage);
    console.log('Claude messages before:', claudeMessages.length, 'after:', updatedClaudeMessages.length);
    console.log('OpenAI messages before:', openaiMessages.length, 'after:', updatedOpenaiMessages.length);

    setClaudeMessages(updatedClaudeMessages);
    setOpenaiMessages(updatedOpenaiMessages);
    setIsLoading(true);

    try {
      // API呼び出し
      const response = await sendChatMessage(newMessages, 'both');

      // Claudeのレスポンス処理
      if (response.responses.claude?.success) {
        const claudeResponse: Message = {
          role: 'assistant',
          content: response.responses.claude.response,
          timestamp: new Date(),
        };
        setClaudeMessages(prev => [...prev, claudeResponse]);
      } else if (response.responses.claude?.error) {
        const claudeError: Message = {
          role: 'assistant',
          content: `エラー: ${response.responses.claude.error}`,
          timestamp: new Date(),
        };
        setClaudeMessages(prev => [...prev, claudeError]);
      }

      // OpenAIのレスポンス処理
      if (response.responses.openai?.success) {
        const openaiResponse: Message = {
          role: 'assistant',
          content: response.responses.openai.response,
          timestamp: new Date(),
        };
        setOpenaiMessages(prev => [...prev, openaiResponse]);
      } else if (response.responses.openai?.error) {
        const openaiError: Message = {
          role: 'assistant',
          content: `エラー: ${response.responses.openai.error}`,
          timestamp: new Date(),
        };
        setOpenaiMessages(prev => [...prev, openaiError]);
      }

    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'エラーが発生しました。もう一度お試しください。',
        timestamp: new Date(),
      };
      setClaudeMessages(prev => [...prev, errorMessage]);
      setOpenaiMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleModelVisibility = (model: 'claude' | 'openai') => {
    console.log('toggleModelVisibility called', { model });
    setModelVisibility(prev => ({
      ...prev,
      [model]: !prev[model],
    }));
  };

  const visibleModelsCount = Object.values(modelVisibility).filter(Boolean).length;

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* ヘッダー */}
      <div className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-900">
          Jグランツ補助金検索チャット
        </h1>
        <p className="text-sm text-gray-600 mt-1">
          補助金情報をAIに質問して検索できます
        </p>

        {/* モデル表示切り替えボタン */}
        <div className="flex gap-2 mt-3">
          <button
            onClick={() => toggleModelVisibility('claude')}
            className={`px-4 py-2 rounded-lg font-semibold text-sm transition-colors ${
              modelVisibility.claude
                ? 'bg-[#D97757] hover:bg-[#CC9B7A] text-white'
                : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
            }`}
          >
            Claude {modelVisibility.claude ? '✓' : '✗'}
          </button>
          <button
            onClick={() => toggleModelVisibility('openai')}
            className={`px-4 py-2 rounded-lg font-semibold text-sm transition-colors ${
              modelVisibility.openai
                ? 'bg-[#10A37F] hover:bg-[#1A7F64] text-white'
                : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
            }`}
          >
            ChatGPT {modelVisibility.openai ? '✓' : '✗'}
          </button>
        </div>
      </div>

      {/* チャットエリア */}
      <div className="flex-1 overflow-hidden">
        <div className={`grid ${visibleModelsCount === 2 ? 'grid-cols-2' : 'grid-cols-1'} gap-6 h-full p-6`}>
          {/* Claude チャット */}
          {modelVisibility.claude && (
            <div className="flex flex-col bg-white rounded-lg shadow-md overflow-hidden">
              <div className="bg-[#D97757] text-white px-4 py-3 font-bold">
                Claude
              </div>
              <div className="flex-1 overflow-y-auto p-6">
                {claudeMessages.map((msg, idx) => (
                  <ChatMessage key={idx} message={msg} model="claude" />
                ))}
                {isLoading && (
                  <div className="flex justify-start mb-3">
                    <div className="bg-gray-100 rounded-2xl px-4 py-3 border border-gray-200">
                      <div className="flex items-center gap-2">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-[#D97757] rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-[#D97757] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-[#D97757] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                        <span className="text-sm text-gray-600">Claudeが考え中...</span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={claudeEndRef} />
              </div>
            </div>
          )}

          {/* OpenAI チャット */}
          {modelVisibility.openai && (
            <div className="flex flex-col bg-white rounded-lg shadow-md overflow-hidden">
              <div className="bg-[#10A37F] text-white px-4 py-3 font-bold">
                ChatGPT
              </div>
              <div className="flex-1 overflow-y-auto p-6">
                {openaiMessages.map((msg, idx) => (
                  <ChatMessage key={idx} message={msg} model="openai" />
                ))}
                {isLoading && (
                  <div className="flex justify-start mb-3">
                    <div className="bg-gray-100 rounded-2xl px-4 py-3 border border-gray-200">
                      <div className="flex items-center gap-2">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-[#10A37F] rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-[#10A37F] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-[#10A37F] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                        <span className="text-sm text-gray-600">ChatGPTが考え中...</span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={openaiEndRef} />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 入力エリア */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <div className="flex gap-3">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="補助金について質問してください..."
            className="flex-1 resize-none border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !inputValue.trim()}
            className="px-6 py-3 bg-[#0EA5E9] text-white font-semibold rounded-lg hover:bg-[#0284C7] disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? '送信中...' : '送信'}
          </button>
        </div>
      </div>
    </div>
  );
}
