import React from 'react';
import ReactMarkdown from 'react-markdown';

const Message = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`message ${message.role}`}>
      <div className="message-content">
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
          // For assistant messages, render markdown
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
        )}
        
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