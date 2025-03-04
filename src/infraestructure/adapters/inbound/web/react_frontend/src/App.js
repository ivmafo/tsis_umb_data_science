import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import FileUpload from './components/FileUpload';
import FileList from './components/FileList';
import DirectoryUpload from './components/DirectoryUpload';
import ConfigManager from './components/ConfigManager';
import './App.css';

function App() {
  const [selectedOption, setSelectedOption] = useState('');
  const [refreshList, setRefreshList] = useState(false);

  const handleUploadSuccess = () => {
    setRefreshList(prev => !prev);
  };

  const renderContent = () => {
    switch (selectedOption) {
      case 'upload':
        return <FileUpload onUploadSuccess={handleUploadSuccess} />;
      case 'list':
        return <FileList refresh={refreshList} />;
      case 'uploadDir':
        return <DirectoryUpload onUploadSuccess={handleUploadSuccess} />;
      case 'config':
        return <ConfigManager />;
      default:
        return <div className="welcome-message">Seleccione una opción del menú</div>;
    }
  };

  return (
    <div className="app">
      <Sidebar onSelect={setSelectedOption} />
      <main className="content">
        {renderContent()}
      </main>
    </div>
  );
}

export default App;
