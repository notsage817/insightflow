import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import ChatInput from './components/ChatInput';
import ModelSelector from './components/ModelSelector';
import FileUploadModal from './components/FileUploadModal';
import { chatAPI } from './services/api';

function App() {
  // State management
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [selectedModel, setSelectedModel] = useState(null);
  const [loading, setLoading] = useState(false);
  const [conversationsLoading, setConversationsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isFileUploadOpen, setIsFileUploadOpen] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Load specific conversation when selected
  useEffect(() => {
    if (currentConversationId) {
      loadConversation(currentConversationId);
    } else {
      setCurrentConversation(null);
    }
  }, [currentConversationId]);

  const loadConversations = async () => {
    try {
      setConversationsLoading(true);
      const conversationsData = await chatAPI.getConversations();
      setConversations(conversationsData);
      console.log('Loaded conversations:', conversationsData.length);
    } catch (err) {
      console.error('Failed to load conversations:', err);
      setError('Failed to load conversations');
    } finally {
      setConversationsLoading(false);
    }
  };

  const loadConversation = async (conversationId) => {
    try {
      const conversationData = await chatAPI.getConversation(conversationId);
      setCurrentConversation(conversationData);
      console.log('Loaded conversation:', conversationId);
    } catch (err) {
      console.error('Failed to load conversation:', err);
      setError('Failed to load conversation');
    }
  };

  const handleNewChat = () => {
    setCurrentConversationId(null);
    setCurrentConversation(null);
    setUploadedFile(null);
    console.log('Started new chat');
  };

  const handleSelectConversation = (conversationId) => {
    setCurrentConversationId(conversationId);
    setUploadedFile(null);
    console.log('Selected conversation:', conversationId);
  };

  const handleSendMessage = async (message) => {
    if (!selectedModel) {
      setError('Please select a model first');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      console.log('Sending message:', {
        message,
        model: selectedModel,
        conversationId: currentConversationId,
        fileContent: uploadedFile?.content
      });

      let response;
      
      if (currentConversationId) {
        // Send to existing conversation
        response = await chatAPI.sendMessage(
          currentConversationId,
          message,
          selectedModel.provider,
          selectedModel.name,
          uploadedFile?.content || null
        );
      } else {
        // Create new conversation
        response = await chatAPI.sendStandaloneMessage(
          message,
          selectedModel.provider,
          selectedModel.name,
          null,
          uploadedFile?.content || null
        );
        
        // Update current conversation ID
        setCurrentConversationId(response.conversation_id);
      }

      console.log('Message sent successfully:', response);

      // Reload conversations and current conversation
      await loadConversations();
      await loadConversation(response.conversation_id);
      
      // Clear uploaded file after sending
      setUploadedFile(null);

    } catch (err) {
      console.error('Failed to send message:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to send message';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleModelChange = (model) => {
    setSelectedModel(model);
    console.log('Selected model:', model);
  };

  const handleOpenFileUpload = () => {
    setIsFileUploadOpen(true);
  };

  const handleCloseFileUpload = () => {
    setIsFileUploadOpen(false);
  };

  const handleFileProcessed = (fileData) => {
    setUploadedFile(fileData);
    console.log('File processed:', fileData.filename);
  };

  return (
    <div className="app">
      <Sidebar
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        loading={conversationsLoading}
      />
      
      <div className="main-content">
        <ModelSelector
          selectedModel={selectedModel}
          onModelChange={handleModelChange}
        />
        
        {error && (
          <div className="error-message" style={{ margin: '16px' }}>
            {error}
          </div>
        )}
        
        <ChatArea
          messages={currentConversation?.messages || []}
          loading={loading}
        />
        
        <ChatInput
          onSendMessage={handleSendMessage}
          onOpenFileUpload={handleOpenFileUpload}
          disabled={loading || !selectedModel}
          uploadedFile={uploadedFile}
        />
      </div>
      
      <FileUploadModal
        isOpen={isFileUploadOpen}
        onClose={handleCloseFileUpload}
        onFileProcessed={handleFileProcessed}
      />
    </div>
  );
}

export default App;