'use client';

import React from 'react';

interface MessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  metadata?: {
    chunks_retrieved?: number;
    response_time_ms?: number;
    tokens_used?: number;
  };
}

const Message: React.FC<MessageProps> = ({ role, content, timestamp, metadata }) => {
  const isUser = role === 'user';
  
  return (
    <div style={{
      display: 'flex',
      justifyContent: isUser ? 'flex-end' : 'flex-start',
      marginBottom: '20px',
      padding: '0 20px'
    }}>
      <div style={{
        maxWidth: '70%',
        background: isUser ? '#22c55e' : '#111111',
        border: isUser ? 'none' : '1px solid #22c55e',
        borderRadius: '8px',
        padding: '16px',
        position: 'relative'
      }}>
        {/* Role indicator */}
        <div style={{
          position: 'absolute',
          top: '-8px',
          left: isUser ? 'auto' : '16px',
          right: isUser ? '16px' : 'auto',
          background: '#000000',
          padding: '2px 8px',
          borderRadius: '4px',
          fontSize: '10px',
          color: '#22c55e',
          fontFamily: 'monospace',
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          {isUser ? 'YOU' : 'AI'}
        </div>
        
        {/* Message content */}
        <div style={{
          color: isUser ? '#000000' : '#ffffff',
          fontFamily: 'monospace',
          fontSize: '14px',
          lineHeight: '1.5',
          marginTop: '8px'
        }}>
          {content}
        </div>
        
        {/* Metadata */}
        {metadata && !isUser && (
          <div style={{
            marginTop: '12px',
            paddingTop: '12px',
            borderTop: '1px solid #333333',
            fontSize: '10px',
            color: '#666666',
            fontFamily: 'monospace',
            display: 'flex',
            gap: '12px',
            flexWrap: 'wrap'
          }}>
            {metadata.chunks_retrieved !== undefined && (
              <span>CHUNKS: {metadata.chunks_retrieved}</span>
            )}
            {metadata.response_time_ms !== undefined && (
              <span>TIME: {metadata.response_time_ms.toFixed(0)}MS</span>
            )}
            {metadata.tokens_used !== undefined && (
              <span>TOKENS: {metadata.tokens_used}</span>
            )}
          </div>
        )}
        
        {/* Timestamp */}
        {timestamp && (
          <div style={{
            marginTop: '8px',
            fontSize: '10px',
            color: '#666666',
            fontFamily: 'monospace',
            textAlign: isUser ? 'right' : 'left'
          }}>
            {timestamp}
          </div>
        )}
      </div>
    </div>
  );
};

export default Message;
