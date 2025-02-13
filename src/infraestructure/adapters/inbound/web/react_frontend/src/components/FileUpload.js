import React, { useState } from 'react';
import './FileUpload.css'; 
function FileUpload({ onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [message, setMessage] = useState('');

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const uploadFile = async () => {
    if (!selectedFile) {
      setMessage('Por favor, selecciona un archivo.');
      return;
    }
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });
      const result = await response.json();
      setMessage(result.message);
      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      setMessage('Error al subir el archivo.');
    }
  };

  return (
    <div className="file-upload">
      <input type="file" onChange={handleFileChange} />
      <button onClick={uploadFile}>Subir Archivo</button>
      <div>{message}</div>
    </div>
  );
}

export default FileUpload; // Asegúrate de que el componente se exporta correctamente
