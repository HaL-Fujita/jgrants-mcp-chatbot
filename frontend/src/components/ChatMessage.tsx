import React from 'react';
import type { Message } from '../types';

interface ChatMessageProps {
  message: Message;
  model?: 'claude' | 'openai';
}

export default function ChatMessage({ message, model }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-primary-500 text-white'
            : 'bg-gray-100 text-gray-900 border border-gray-200'
        }`}
      >
        {!isUser && model && (
          <div className="text-xs font-semibold mb-1 opacity-70">
            {model === 'claude' ? 'Claude' : 'ChatGPT'}
          </div>
        )}
        <div className="whitespace-pre-wrap break-words">
          {message.content}
        </div>
        {message.timestamp && (
          <div className="text-xs mt-2 opacity-60">
            {new Date(message.timestamp).toLocaleTimeString('ja-JP')}
          </div>
        )}
      </div>
    </div>
  );
}
