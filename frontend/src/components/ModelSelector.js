import React, { useState, useEffect } from 'react';
import { chatAPI } from '../services/api';

const ModelSelector = ({ selectedModel, onModelChange }) => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      setLoading(true);
      const modelsData = await chatAPI.getModels();
      setModels(modelsData);
      
      // Set default model if none selected
      if (!selectedModel && modelsData.length > 0) {
        const defaultModel = modelsData.find(m => m.name === 'gpt-3.5-turbo') || modelsData[0];
        onModelChange(defaultModel);
      }
      setError(null);
    } catch (err) {
      console.error('Failed to load models:', err);
      setError('Failed to load models');
    } finally {
      setLoading(false);
    }
  };

  const handleModelChange = (e) => {
    const modelKey = e.target.value;
    const [provider, name] = modelKey.split('/');
    const model = models.find(m => m.provider === provider && m.name === name);
    if (model) {
      onModelChange(model);
    }
  };

  if (loading) {
    return (
      <div className="model-selector">
        <select className="model-dropdown" disabled>
          <option>Loading models...</option>
        </select>
      </div>
    );
  }

  if (error) {
    return (
      <div className="model-selector">
        <select className="model-dropdown" disabled>
          <option>Error loading models</option>
        </select>
      </div>
    );
  }

  const currentModelKey = selectedModel ? `${selectedModel.provider}/${selectedModel.name}` : '';

  return (
    <div className="model-selector">
      <select 
        className="model-dropdown" 
        value={currentModelKey}
        onChange={handleModelChange}
      >
        {models.length === 0 ? (
          <option value="">No models available</option>
        ) : (
          models.map((model) => (
            <option 
              key={`${model.provider}/${model.name}`} 
              value={`${model.provider}/${model.name}`}
            >
              {model.display_name}
            </option>
          ))
        )}
      </select>
    </div>
  );
};

export default ModelSelector;