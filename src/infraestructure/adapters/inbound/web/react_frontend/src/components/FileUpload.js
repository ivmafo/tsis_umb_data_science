import React, { useState, useEffect } from 'react';
import './FileUpload.css';

function FileUpload({ onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [message, setMessage] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [processStatus, setProcessStatus] = useState({
    status: 'idle',
    total_rows: 0,
    processed_rows: 0,
    percentage: 0
  });

  useEffect(() => {
    let intervalId;
    let isActive = true; // Flag to prevent updates after component unmounts

    if (isUploading) {
      // Start polling immediately
      checkProcessStatus();
      
      intervalId = setInterval(checkProcessStatus, 100); // More frequent updates
    }

    async function checkProcessStatus() {
      if (!isActive) return;

      try {
        const response = await fetch('http://localhost:8000/api/process-status', {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          },
          timeout: 5000 // 5 segundos de timeout
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!isActive) return;

        setProcessStatus(prevStatus => ({
          ...prevStatus,
          status: data.status,
          total_rows: data.total_rows,
          processed_rows: data.processed_rows,
          percentage: data.percentage
        }));
        
        if (data.status === 'completed' || data.status === 'error') {
          clearInterval(intervalId);
          setIsUploading(false);
          if (onUploadSuccess) {
            onUploadSuccess();
          }
        }
      } catch (error) {
        console.error('Error checking status:', error);
        // No detener el polling en caso de error temporal
        if (error.message.includes('ERR_INSUFFICIENT_RESOURCES')) {
          await new Promise(resolve => setTimeout(resolve, 2000)); // Esperar 2 segundos antes de reintentar
        }
      }
    }

    return () => {
      isActive = false;
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [isUploading, onUploadSuccess]);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setUploadProgress(0);
    setProcessStatus({
      status: 'idle',
      total_rows: 0,
      processed_rows: 0,
      percentage: 0
    });
    setMessage('');
  };

  const uploadFile = async () => {
    if (!selectedFile) {
      setMessage('Por favor, selecciona un archivo.');
      return;
    }
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
      setIsUploading(true);
      const xhr = new XMLHttpRequest();
      
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100);
          setUploadProgress(progress);
        }
      };

      xhr.onerror = () => {
          setMessage('Error al subir el archivo.');
          setIsUploading(false);
          console.error('Upload failed:', xhr.status, xhr.statusText);
      };

      xhr.onload = async () => {
          if (xhr.status === 200) {
              try {
                  const result = JSON.parse(xhr.response);
                  setMessage(result.message);
                  if (onUploadSuccess) {
                      onUploadSuccess();
                  }
              } catch (error) {
                  console.error('Error parsing response:', error);
                  setMessage('Error al procesar la respuesta del servidor.');
              }
          } else {
              setMessage('Error al subir el archivo.');
              console.error('Upload failed:', xhr.status, xhr.statusText);
          }
          setIsUploading(false);
      };

      xhr.open('POST', 'http://localhost:8000/api/upload');
      xhr.send(formData);
    } catch (error) {
      console.error('Error uploading file:', error);
      setMessage('Error al subir el archivo.');
      setIsUploading(false);
    }
  };

  return (
    <div className="file-upload">
      <div className="upload-container">
        <input 
          type="file" 
          onChange={handleFileChange}
          disabled={isUploading}
          accept=".xlsx,.xls"
        />
        <button 
          onClick={uploadFile} 
          disabled={!selectedFile || isUploading}
          className={isUploading ? 'uploading' : ''}
        >
          {isUploading ? 'Preparando cargue...' : 'Subir Archivo'}
        </button>
      </div>

      {isUploading && (
        <>
          <div className="progress-section">
            <div className="progress-label">Progreso de carga del archivo</div>
            <div className="progress-container">
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <div className="progress-text">{uploadProgress}%</div>
            </div>
          </div>

          <div className="progress-section">
            <div className="progress-label">
              Progreso de inserción en base de datos
              {processStatus.status === 'processing' && ' (Procesando...)'}
            </div>
            <div className="progress-container">
              <div className="progress-bar">
                <div 
                  className="progress-fill database"
                  style={{ width: `${processStatus.percentage || 0}%` }}
                />
              </div>
              <div className="progress-text">
                {processStatus.processed_rows} de {processStatus.total_rows} registros ({processStatus.percentage || 0}%)
              </div>
            </div>
          </div>
        </>
      )}

      {message && (
        <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}
    </div>
  );
}

export default FileUpload;