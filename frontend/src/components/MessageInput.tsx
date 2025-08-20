'use client';

import React, { useState, KeyboardEvent } from 'react';

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({ onSendMessage, isLoading = false }) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim() && !isLoading) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{
      borderTop: '1px solid #22c55e',
      padding: '20px',
      background: '#000000'
    }}>
      <div style={{
        display: 'flex',
        gap: '12px',
        alignItems: 'flex-end',
        maxWidth: '800px',
        margin: '0 auto'
      }}>
        <div style={{
          flex: 1,
          position: 'relative'
        }}>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={isLoading}
            style={{
              width: '100%',
              minHeight: '44px',
              maxHeight: '120px',
              padding: '12px 16px',
              background: '#111111',
              border: '1px solid #22c55e',
              borderRadius: '4px',
              color: '#ffffff',
              fontFamily: 'monospace',
              fontSize: '14px',
              resize: 'none',
              outline: 'none',
              lineHeight: '1.4'
            }}
          />
        </div>
        <button
          onClick={handleSend}
          disabled={!message.trim() || isLoading}
          style={{
            padding: '12px 20px',
            background: message.trim() && !isLoading ? '#22c55e' : '#333333',
            border: '1px solid #22c55e',
            borderRadius: '4px',
            color: message.trim() && !isLoading ? '#000000' : '#666666',
            fontFamily: 'monospace',
            fontSize: '12px',
            fontWeight: 'bold',
            cursor: message.trim() && !isLoading ? 'pointer' : 'not-allowed',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            transition: 'all 0.2s ease'
          }}
        >
          {isLoading ? 'SENDING...' : 'SEND'}
        </button>
      </div>
    </div>
  );
};

export default MessageInput;
