import React, { useState } from 'react';
import { UploadCloud, FileJson, CheckCircle, AlertTriangle } from 'lucide-react';
import { API_BASE_URL } from '../config';
import './UploadLogs.css';

const UploadLogs = () => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, uploading, success, error
  const [message, setMessage] = useState('');

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (uploadedFile) => {
    const allowedExtensions = ['.json', '.log', '.txt', '.csv'];
    const fileName = uploadedFile.name.toLowerCase();
    const isValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext));

    if (!isValidExtension && uploadedFile.type !== "application/json") {
      setStatus('error');
      setMessage('Unsupported file format. Please upload .json, .log, .txt, or .csv files.');
      return;
    }
    setFile(uploadedFile);
    setStatus('idle');
    setMessage('');
  };

  const handleUpload = () => {
    if (!file) return;

    setStatus('uploading');
    setMessage('Processing file...');

    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        let payload;
        let isJson = false;
        const rawContent = e.target.result;

        try {
          const jsonContent = JSON.parse(rawContent);
          payload = Array.isArray(jsonContent) ? jsonContent : [jsonContent];
          isJson = true;
        } catch (jsonErr) {
          // Fallback to raw text if not valid JSON
          payload = rawContent;
          isJson = false;
        }

        setMessage('Uploading to secure database...');
        
        const response = await fetch(`${API_BASE_URL}/upload_logs`, {
          method: 'POST',
          headers: { 
            'Content-Type': isJson ? 'application/json' : 'text/plain' 
          },
          body: isJson ? JSON.stringify(payload) : payload
        });

        const data = await response.json();
        
        if (data.success) {
          setStatus('success');
          setMessage(data.message || 'Logs uploaded successfully!');
          setFile(null);
        } else {
          setStatus('error');
          setMessage(data.message || 'Server rejected the upload.');
        }

      } catch (err) {
        console.error("Upload failed:", err);
        setStatus('error');
        setMessage(`Network error: Could not reach backend at ${API_BASE_URL}. (${err.message || 'Server waking up or CORS error'})`);
      }
    };
    
    reader.readAsText(file);
  };

  return (
    <div className="upload-page">
      <div className="page-header">
        <h1>Upload External Logs</h1>
        <p className="text-muted">Import security logs (JSON, Log, TXT) directly into the centralized Logvista database for analysis.</p>
      </div>

      <div className="upload-container">
        <div 
          className={`drop-zone ${dragActive ? 'active' : ''} ${file ? 'has-file' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input 
            type="file" 
            id="file-upload" 
            accept=".json,.log,.txt,.csv,application/json,text/plain" 
            onChange={handleChange} 
            className="hidden-input"
          />
          
          <label htmlFor="file-upload" className="drop-zone-content">
            {!file ? (
              <>
                <UploadCloud size={48} className="upload-icon pulse-slow" />
                <h3>Drag & Drop JSON File Here</h3>
                <p>or click to browse from your system</p>
                <div className="format-badges">
                  <span className="badge">.JSON</span>
                </div>
              </>
            ) : (
              <div className="selected-file">
                <FileJson size={48} className="file-icon" />
                <div className="file-info">
                  <h4>{file.name}</h4>
                  <p>{(file.size / 1024).toFixed(2)} KB</p>
                </div>
                <button 
                  className="outline-btn small" 
                  onClick={(e) => { e.preventDefault(); setFile(null); }}
                >
                  Remove
                </button>
              </div>
            )}
          </label>
        </div>

        {status === 'error' && (
          <div className="alert-message error">
            <AlertTriangle size={18} />
            <span>{message}</span>
          </div>
        )}

        {status === 'success' && (
          <div className="alert-message success">
            <CheckCircle size={18} />
            <span>{message}</span>
          </div>
        )}

        <div className="upload-actions">
          <button 
            className="primary-btn full-width" 
            onClick={handleUpload}
            disabled={!file || status === 'uploading'}
          >
            {status === 'uploading' ? 'PROCESSING...' : 'UPLOAD TO DATABASE'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UploadLogs;
