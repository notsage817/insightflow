import React, { useRef, useEffect } from 'react';
import Message from './Message';

const ChatArea = ({ messages, loading = false }) => {
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  if (messages.length === 0 && !loading) {
    return (
      <div className="chat-container">
        <div className="empty-state">
          <h2>Welcome to Semantix Chat</h2>
          <p>Start a conversation with your AI assistant</p>
          <p>Choose a model from the dropdown above and send a message to begin</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-container">
      <div className="messages-container">
        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}
        
        {loading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="loading">
                <span>AI is thinking</span>
                <div className="loading-dots">
                  <div className="loading-dot"></div>
                  <div className="loading-dot"></div>
                  <div className="loading-dot"></div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatArea;