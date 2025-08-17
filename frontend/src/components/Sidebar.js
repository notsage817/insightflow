import React from 'react';
import { Plus, MessageSquare } from 'lucide-react';

const Sidebar = ({ 
  conversations, 
  currentConversationId, 
  onSelectConversation, 
  onNewChat,
  loading = false 
}) => {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <button className="new-chat-btn" onClick={onNewChat} disabled={loading}>
          <Plus size={16} />
          New chat
        </button>
      </div>
      
      <div className="conversations-list">
        {loading ? (
          <div style={{ padding: '12px', color: '#6b7280', fontSize: '14px' }}>
            Loading conversations...
          </div>
        ) : conversations.length === 0 ? (
          <div style={{ padding: '12px', color: '#6b7280', fontSize: '14px' }}>
            No conversations yet
          </div>
        ) : (
          conversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`conversation-item ${
                currentConversationId === conversation.id ? 'active' : ''
              }`}
              onClick={() => onSelectConversation(conversation.id)}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <MessageSquare size={14} />
                <span style={{ 
                  overflow: 'hidden', 
                  textOverflow: 'ellipsis', 
                  whiteSpace: 'nowrap',
                  flex: 1 
                }}>
                  {conversation.title}
                </span>
              </div>
              <div style={{ 
                fontSize: '12px', 
                color: '#6b7280', 
                marginTop: '4px' 
              }}>
                {new Date(conversation.updated_at).toLocaleDateString()}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Sidebar;