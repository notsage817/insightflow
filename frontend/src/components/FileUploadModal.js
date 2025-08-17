import React, { useState, useRef } from 'react';
import { X, Upload, File } from 'lucide-react';
import { chatAPI } from '../services/api';

const FileUploadModal = ({ isOpen, onClose, onFileProcessed }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  if (!isOpen) return null;

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileSelect = () => {
    fileInputRef.current?.click();
  };

  const handleFileInputChange = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileUpload = async (file) => {
    setIsUploading(true);
    setError(null);

    try {
      console.log('Uploading file:', file.name);
      const result = await chatAPI.uploadFile(file);
      console.log('File uploaded successfully:', result);
      
      // Pass the processed file content to parent
      onFileProcessed(result);
      onClose();
    } catch (err) {
      console.error('File upload error:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to upload file';
      setError(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-content">
        <div className="modal-header">
          <h3 className="modal-title">Upload File</h3>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div
          className={`file-upload-area ${isDragOver ? 'dragover' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleFileSelect}
        >
          <input
            ref={fileInputRef}
            type="file"
            className="file-input"
            accept=".pdf,.txt"
            onChange={handleFileInputChange}
          />
          
          {isUploading ? (
            <div className="loading">
              <Upload size={24} />
              <span>Uploading...</span>
              <div className="loading-dots">
                <div className="loading-dot"></div>
                <div className="loading-dot"></div>
                <div className="loading-dot"></div>
              </div>
            </div>
          ) : (
            <>
              <File size={48} style={{ color: '#6b7280', marginBottom: '16px' }} />
              <p className="upload-text">
                <strong>Click to upload</strong> or drag and drop
              </p>
              <p className="upload-text" style={{ fontSize: '12px', marginTop: '8px' }}>
                Supported formats: PDF, TXT (max 10MB)
              </p>
            </>
          )}
        </div>

        <div style={{ marginTop: '16px', fontSize: '14px', color: '#6b7280' }}>
          <p>Your file will be processed and its content will be included with your next message.</p>
        </div>
      </div>
    </div>
  );
};

export default FileUploadModal;