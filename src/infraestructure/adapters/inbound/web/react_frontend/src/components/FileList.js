import React, { useEffect, useState } from 'react';
import './FileList.css'; 
function FileList() {
  const [files, setFiles] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/files')
      .then(response => response.json())
      .then(data => setFiles(data.files))
      .catch(error => console.error('Error fetching files:', error));
  }, []);

    
  return (
    <div className="file-list">
      <h2>Archivos Cargados</h2>
      <ul>
        {files.map((file, index) => (
          <li key={index}>{file}</li>
        ))}
      </ul>
    </div>
  );
} 

export default FileList; // Asegúrate de que el componente se exporta correctamente
