import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Copy, Check } from 'lucide-react';

const Message = ({ message }) => {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000); // Reset after 2 seconds
    } catch (err) {
      console.error('Failed to copy text: ', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = message.content;
      document.body.appendChild(textArea);
      textArea.select();
      try {
        document.execCommand('copy');
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (fallbackErr) {
        console.error('Fallback copy failed: ', fallbackErr);
      }
      document.body.removeChild(textArea);
    }
  };
  
  return (
    <div className={`message ${message.role}`}>
      <div className="message-content">
        <div style={{ position: 'relative' }}>
          {isUser ? (
            // For user messages, render plain text to preserve formatting
            <div style={{ whiteSpace: 'pre-wrap' }}>
              {message.content}
              {message.file_attachment && (
                <div style={{ marginTop: '12px', fontStyle: 'italic', opacity: 0.8 }}>
                  📎 File attached
                </div>
              )}
            </div>
          ) : (
            // For assistant messages, render markdown with copy button
            <>
              <ReactMarkdown
                components={{
                  // Custom code block styling
                  code: ({ node, inline, className, children, ...props }) => {
                    if (inline) {
                      return (
                        <code className="inline-code" {...props}>
                          {children}
                        </code>
                      );
                    }
                    return (
                      <pre>
                        <code className={className} {...props}>
                          {children}
                        </code>
                      </pre>
                    );
                  },
                  // Custom link styling
                  a: ({ children, href, ...props }) => (
                    <a
                      href={href}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        color: '#2563eb',
                        textDecoration: 'underline',
                      }}
                      {...props}
                    >
                      {children}
                    </a>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
              
              {/* Copy button for assistant messages */}
              <button
                onClick={handleCopyToClipboard}
                className="copy-button"
                title={copied ? "Copied!" : "Copy to clipboard"}
                style={{
                  position: 'absolute',
                  top: '8px',
                  right: '8px',
                  background: 'rgba(0, 0, 0, 0.1)',
                  border: 'none',
                  borderRadius: '4px',
                  padding: '6px',
                  cursor: 'pointer',
                  opacity: 0.7,
                  transition: 'opacity 0.2s, background-color 0.2s',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
                onMouseEnter={(e) => {
                  e.target.style.opacity = '1';
                  e.target.style.backgroundColor = 'rgba(0, 0, 0, 0.15)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.opacity = '0.7';
                  e.target.style.backgroundColor = 'rgba(0, 0, 0, 0.1)';
                }}
              >
                {copied ? (
                  <Check size={14} style={{ color: '#10b981' }} />
                ) : (
                  <Copy size={14} style={{ color: '#6b7280' }} />
                )}
              </button>
            </>
          )}
        </div>
        
        {/* Message metadata */}
        <div 
          style={{
            fontSize: '12px',
            marginTop: '8px',
            opacity: 0.6,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span>
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
          {message.model_used && (
            <span>
              {message.model_used}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default Message;