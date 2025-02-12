import React, { useState } from 'react';

function App() {
  const [message, setMessage] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);

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
    
    const response = await fetch('http://localhost:8000/upload', {
      method: 'POST',
      body: formData,
    });
    
    const result = await response.json();
    setMessage(result.message);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Importar Archivos de Vuelos</h1>
        <input type="file" onChange={handleFileChange} />
        <button onClick={uploadFile}>Subir Archivo</button>
        <div>{message}</div>
      </header>
    </div>
  );
}

export default App;
