import axios from 'axios';

// API client configuration
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production' 
    ? '/api' 
    : process.env.REACT_APP_API_URL || 'http://localhost:5669',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging and error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API methods
export const chatAPI = {
  // Get available models
  getModels: async () => {
    const response = await api.get('/chat/models');
    return response.data;
  },

  // Get all conversations
  getConversations: async () => {
    const response = await api.get('/chat/conversations');
    return response.data;
  },

  // Create new conversation
  createConversation: async (modelProvider, modelName, title = 'New Chat') => {
    const response = await api.post('/chat/conversations', null, {
      params: {
        model_provider: modelProvider,
        model_name: modelName,
        title,
      },
    });
    return response.data;
  },

  // Get specific conversation
  getConversation: async (conversationId) => {
    const response = await api.get(`/chat/conversations/${conversationId}`);
    return response.data;
  },

  // Delete conversation
  deleteConversation: async (conversationId) => {
    const response = await api.delete(`/chat/conversations/${conversationId}`);
    return response.data;
  },

  // Send message
  sendMessage: async (conversationId, message, modelProvider, modelName, fileContent = null) => {
    const requestData = {
      message,
      model_provider: modelProvider,
      model_name: modelName,
      conversation_id: conversationId,
      file_content: fileContent,
    };
    
    const response = await api.post(`/chat/conversations/${conversationId}/messages`, requestData);
    return response.data;
  },

  // Send standalone message (creates conversation if needed)
  sendStandaloneMessage: async (message, modelProvider, modelName, conversationId = null, fileContent = null) => {
    const requestData = {
      message,
      model_provider: modelProvider,
      model_name: modelName,
      conversation_id: conversationId,
      file_content: fileContent,
    };
    
    const response = await api.post('/chat/message', requestData);
    return response.data;
  },

  // Upload file
  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/chat/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// Health check
export const healthAPI = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;