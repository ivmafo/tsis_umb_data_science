import React, { useEffect, useState } from 'react';
import './FileList.css'; 

function FileList() {
  const [files, setFiles] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetch('http://localhost:8000/files')
      .then(response => response.json())
      .then(data => setFiles(data.files))
      .catch(error => console.error('Error fetching files:', error));
  }, []);

  const filteredFiles = files.filter(file =>
    file.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getFileIcon = (fileName) => {
    const extension = fileName.split('.').pop().toLowerCase();
    switch(extension) {
      case 'pdf':
        return 'fas fa-file-pdf';
      case 'doc':
      case 'docx':
        return 'fas fa-file-word';
      case 'xls':
      case 'xlsx':
        return 'fas fa-file-excel';
      case 'jpg':
      case 'jpeg':
      case 'png':
        return 'fas fa-file-image';
      default:
        return 'fas fa-file';
    }
  };

  return (
    <div className="file-list">
      <h2>Archivos Cargados</h2>
      <div className="search-container">
        <input
          type="text"
          placeholder="Buscar archivos..."
          className="search-input"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
      <div className="cards-container">
        {filteredFiles.map((file, index) => (
          <div key={index} className="file-card">
            <div className="file-icon"></div>
            <div className="file-name">{file}</div>
            <div className="file-actions">
              <button className="action-button" title="Descargar">
                <i className="fas fa-download"></i>
              </button>
              <button className="action-button" title="Ver">
                <i className="fas fa-eye"></i>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default FileList;
