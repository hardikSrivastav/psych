'use client';

import React from 'react';

interface MessageProps {
  message: {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    metadata?: any;
  };
}

const Message: React.FC<MessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} fade-in`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        <div
          className={`px-4 py-3 rounded-lg ${
            isUser
              ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
              : 'bg-white/20 backdrop-blur-md text-white border border-white/20'
          }`}
        >
          <div className="text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </div>
          
          {message.metadata && !isUser && (
            <div className="mt-2 pt-2 border-t border-white/20 text-xs text-white/60">
              <div className="flex items-center space-x-4">
                <span>⏱️ {message.metadata.response_time_ms}ms</span>
                <span>📊 {message.metadata.chunks_retrieved} sources</span>
                <span>💬 {message.metadata.tokens_used} tokens</span>
              </div>
            </div>
          )}
        </div>
        
        <div className={`text-xs text-white/50 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {message.timestamp.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </div>
      </div>
      
      <div className={`w-8 h-8 rounded-full flex items-center justify-center mx-2 ${
        isUser ? 'order-1 bg-gradient-to-br from-blue-400 to-purple-500' : 'order-2 bg-gradient-to-br from-green-400 to-blue-500'
      }`}>
        <span className="text-white text-sm font-bold">
          {isUser ? '👤' : '🧠'}
        </span>
      </div>
    </div>
  );
};

export default Message;
