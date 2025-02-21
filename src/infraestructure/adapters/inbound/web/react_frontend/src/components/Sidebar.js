//C:\Users\ivan.forero\OneDrive - PROGASUR SA ESP\Documentos\PYTHON\tsis_umb_data_science\src\infraestructure\adapters\inbound\web\react_frontend\src\components\Sidebar.js
import React from 'react';
import './Sidebar.css';


function Sidebar({ onSelect }) {
  return (
    <div className="sidebar">
      <h2>Opciones</h2>
      <ul>
        <li onClick={() => onSelect('')}>Calculo Capacidad A. DCA</li>
        <li onClick={() => onSelect('')}>Calculo Capacidad A. OASI</li>
        <li onClick={() => onSelect('')}>Calculo Capacidad A. UMB</li>
        <li onClick={() => onSelect('')}>Calculo Analisis DCA</li>
        <li onClick={() => onSelect('list')}>Listado de Archivos</li>
        <li onClick={() => onSelect('upload')}>Cargar Archivo</li>
        <li onClick={() => onSelect('uploadDir')}>Cargar Archivos Desde Directorio</li>        
      </ul>
    </div>
  );
}

export default Sidebar; // Asegúrate de que el componente se exporta correctamente
