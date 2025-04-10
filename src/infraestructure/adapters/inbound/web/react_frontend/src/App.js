import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import FileUpload from './components/FileUpload';
import FileList from './components/FileList';
import DirectoryUpload from './components/DirectoryUpload';
import ConfigManager from './components/ConfigManager';
import Dashboard from './components/Dashboard';
import LevelRangesManager from './components/LevelRangesManager';
import ATCCapacityManager from './components/ATCCapacityManager';
import SectorAnalysisManager from './components/SectorAnalysisManager';
import RegionsManager from './components/RegionsManager'; // Add this import
import Footer from './components/Footer';
import './App.css';

function App() {
  const [selectedOption, setSelectedOption] = useState('dashboard');

  const renderContent = () => {
    switch (selectedOption) {
      case 'upload':
        return <FileUpload onUploadSuccess={() => {}} />;
      case 'list':
        return <FileList />;
      case 'uploadDir':
        return <DirectoryUpload onUploadSuccess={() => {}} />;
      case 'config':
        return <ConfigManager />;
      case 'dashboard':
        return <Dashboard />;
      case 'levelRanges':
        return <LevelRangesManager />;
      case 'sector-analysis':
        return <SectorAnalysisManager />;
      case 'atc-capacity':
        return <ATCCapacityManager />;
      case 'regions': // Add this case
        return <RegionsManager />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app">
      <Sidebar onSelect={setSelectedOption} />
      <main className="main-content">
        {renderContent()}
      </main>
      <Footer />
    </div>
  );
}

export default App;
