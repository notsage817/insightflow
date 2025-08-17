import React, { useState, useRef, useEffect } from 'react';
import { Send, Plus } from 'lucide-react';

const ChatInput = ({ onSendMessage, onOpenFileUpload, disabled = false, uploadedFile = null }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, [message]);

  // Focus textarea on mount
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  const handleSubmit = () => {
    if (message.trim() && !disabled) {
      console.log('Sending message:', message.trim());
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e) => {
    // Send on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleChange = (e) => {
    setMessage(e.target.value);
  };

  return (
    <div className="input-container">
      {uploadedFile && (
        <div style={{
          maxWidth: '768px',
          margin: '0 auto 12px auto',
          padding: '8px 12px',
          backgroundColor: '#f0f9ff',
          border: '1px solid #bae6fd',
          borderRadius: '6px',
          fontSize: '14px',
          color: '#0369a1',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          📎 {uploadedFile.filename} ({uploadedFile.type}) - Ready to send
        </div>
      )}
      
      <div className="input-wrapper">
        <textarea
          ref={textareaRef}
          className="message-input"
          placeholder="Message Semantix Chat..."
          value={message}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          rows={1}
        />
        
        <div className="input-actions">
          <button
            type="button"
            className="action-btn"
            onClick={onOpenFileUpload}
            disabled={disabled}
            title="Upload file"
          >
            <Plus size={16} />
          </button>
          
          <button
            type="button"
            className={`action-btn send ${!message.trim() || disabled ? '' : 'enabled'}`}
            onClick={handleSubmit}
            disabled={!message.trim() || disabled}
            title="Send message"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;