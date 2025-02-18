import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import FileList from './components/FileList';
import Sidebar from './components/Sidebar';
import Footer from './components/Footer';
import './App.css';

function App() {
  const [selectedView, setSelectedView] = useState('upload');

  const renderContent = () => {
    switch (selectedView) {
      case 'upload':
        return <FileUpload onUploadSuccess={() => setSelectedView('list')} />;
      case 'list':
        return <FileList />;
      default:
        return <FileUpload onUploadSuccess={() => setSelectedView('list')} />;
    }
  };

  return (
    <div className="App">
      <Sidebar onSelect={setSelectedView} />
      <div className="main-content">
        <header className="App-header">
          <h1>Operaciones:</h1>
        </header>
        {renderContent()}
        <Footer />
      </div>
    </div>
  );
}

export default App;
