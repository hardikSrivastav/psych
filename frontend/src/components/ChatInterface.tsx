'use client';

import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import Message from './Message';
import MessageInput from './MessageInput';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: any;
}

interface ChatInterfaceProps {
  sessionId: string | null;
  setSessionId: (sessionId: string | null) => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ sessionId, setSessionId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
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

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await axios.post('/api/chat', {
        message: content.trim(),
        session_id: sessionId,
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date(),
        metadata: response.data.metadata,
      };

      setMessages(prev => [...prev, assistantMessage]);
      setSessionId(response.data.session_id);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I apologize, but I\'m experiencing technical difficulties. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full px-4 py-6">
      <div className="flex-1 bg-white/10 backdrop-blur-md rounded-lg border border-white/20 flex flex-col">
        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-white/70 py-8">
              <div className="text-4xl mb-4">🧠</div>
              <h2 className="text-xl font-semibold mb-2">Welcome to AI Psychologist</h2>
              <p className="text-sm">
                I'm here to provide scientifically-grounded therapeutic support. 
                How are you feeling today?
              </p>
            </div>
          )}
          
          {messages.map((message) => (
            <Message key={message.id} message={message} />
          ))}
          
          {isLoading && (
            <div className="flex items-center space-x-2 text-white/70">
              <div className="w-2 h-2 bg-white/70 rounded-full pulse"></div>
              <div className="w-2 h-2 bg-white/70 rounded-full pulse" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-2 h-2 bg-white/70 rounded-full pulse" style={{ animationDelay: '0.4s' }}></div>
              <span className="text-sm">AI is thinking...</span>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-white/20">
          <MessageInput onSendMessage={sendMessage} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
