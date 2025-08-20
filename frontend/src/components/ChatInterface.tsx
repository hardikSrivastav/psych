'use client';

import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import Message from './Message';
import MessageInput from './MessageInput';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: {
    chunks_retrieved?: number;
    response_time_ms?: number;
    tokens_used?: number;
  };
}

interface ChatInterfaceProps {
  sessionId?: string | null;
  setSessionId?: (sessionId: string) => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ sessionId, setSessionId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (content: string) => {
    if (!content.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await axios.post('/api/chat', {
        message: content.trim(),
        session_id: sessionId
      }, {
        timeout: 30000
      });

      const { response: assistantResponse, session_id, metadata } = response.data;

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: assistantResponse,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        metadata
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      if (setSessionId && session_id) {
        setSessionId(session_id);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      background: '#000000'
    }}>
      {/* Messages Container */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '20px 0',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {messages.length === 0 ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            color: '#666666',
            fontFamily: 'monospace',
            fontSize: '14px',
            textAlign: 'center',
            padding: '40px 20px'
          }}>
            <div style={{
              background: '#111111',
              border: '1px solid #22c55e',
              borderRadius: '8px',
              padding: '40px',
              maxWidth: '500px'
            }}>
              <h3 style={{
                color: '#22c55e',
                fontSize: '16px',
                marginBottom: '16px',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                WELCOME TO AI PSYCHOLOGIST
              </h3>
              <p style={{
                color: '#ffffff',
                fontSize: '14px',
                lineHeight: '1.6',
                marginBottom: '20px'
              }}>
                I'm here to provide scientifically-grounded therapeutic support. 
                Share what's on your mind, and I'll respond with evidence-based guidance.
              </p>
              <div style={{
                width: '100%',
                height: '2px',
                background: '#22c55e',
                marginTop: '20px'
              }}></div>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <Message
              key={message.id}
              role={message.role}
              content={message.content}
              timestamp={message.timestamp}
              metadata={message.metadata}
            />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Loading indicator */}
      {isLoading && (
        <div style={{
          padding: '20px',
          textAlign: 'center',
          color: '#22c55e',
          fontFamily: 'monospace',
          fontSize: '12px',
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          AI IS THINKING...
        </div>
      )}

      {/* Message Input */}
      <MessageInput onSendMessage={sendMessage} isLoading={isLoading} />
    </div>
  );
};

export default ChatInterface;
