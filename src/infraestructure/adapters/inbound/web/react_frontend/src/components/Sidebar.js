//C:\Users\ivan.forero\OneDrive - PROGASUR SA ESP\Documentos\PYTHON\tsis_umb_data_science\src\infraestructure\adapters\inbound\web\react_frontend\src\components\Sidebar.js
import React from 'react';
import './Sidebar.css';


function Sidebar({ onSelect }) {
  return (
    <div className="sidebar">
      <h2>Opciones</h2>
      <ul>
        <li onClick={() => onSelect('list')}>Listado de Archivos</li>
        <li onClick={() => onSelect('upload')}>Cargar Archivo</li>
        <li onClick={() => onSelect('uploadDir')}>Cargar Archivos Desde Directorio</li>
        <li onClick={() => onSelect('config')}>Configuración General</li>
        <li onClick={() => onSelect('dashboard')}>Tablero</li>
        <li onClick={() => onSelect('levelRanges')}>Rangos de Nivel</li>        
      </ul>
    </div>
  );
}

export default Sidebar; // Asegúrate de que el componente se exporta correctamente
