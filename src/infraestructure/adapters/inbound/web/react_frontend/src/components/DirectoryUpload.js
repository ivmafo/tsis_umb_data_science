import React, { useState, useRef } from 'react';
import './FileUpload.css';

function DirectoryUpload({ onUploadSuccess }) {
  const [directory, setDirectory] = useState('');
  const [message, setMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef(null);

  const handleDirectoryChange = (event) => {
    setDirectory(event.target.value);
  };

  const handleFileSelect = (event) => {
    const files = event.target.files;
    if (files.length > 0) {
      // Get the directory path from the first file
      const path = files[0].webkitRelativePath.split('/')[0];
      setDirectory(path);
    }
  };

  const uploadFromDirectory = async () => {
    if (!directory) {
      setMessage('Por favor, ingresa una ruta de directorio.');
      return;
    }

    setIsProcessing(true);
    setMessage('Procesando archivos...');

    try {
      const response = await fetch('http://localhost:8000/upload-directory', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ directory_path: directory }),
      });

      const result = await response.json();
      
      if (response.ok) {
        setMessage(`${result.message}\nArchivos procesados: ${result.processed_files.join(', ')}`);
        if (result.errors.length > 0) {
          setMessage(prev => `${prev}\nErrores: ${result.errors.map(e => e.file).join(', ')}`);
        }
        if (onUploadSuccess) {
          onUploadSuccess();
        }
      } else {
        setMessage(`Error: ${result.detail}`);
      }
    } catch (error) {
      console.error('Error processing directory:', error);
      setMessage('Error al procesar el directorio.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="file-upload">
      <h2>Cargar Archivos desde Directorio</h2>
      <div className="directory-input">
        <input 
          type="text" 
          value={directory}
          onChange={handleDirectoryChange}
          placeholder="Ingresa la ruta del directorio"
        />
        <input
          type="file"
          ref={fileInputRef}
          webkitdirectory="true"
          directory="true"
          style={{ display: 'none' }}
          onChange={handleFileSelect}
        />
        <button 
          onClick={() => fileInputRef.current.click()}
          className="select-dir-btn"
        >
          Seleccionar Directorio
        </button>
      </div>
      <button 
        onClick={uploadFromDirectory}
        disabled={isProcessing}
        className="process-btn"
      >
        {isProcessing ? 'Procesando...' : 'Procesar Directorio'}
      </button>
      <div className="message">{message}</div>
    </div>
  );
}

export default DirectoryUpload;