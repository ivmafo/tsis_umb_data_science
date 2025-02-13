import React from 'react';
import './Sidebar.css';

function Sidebar({ onSelect }) {
  return (
    <div className="sidebar">
      <h2>Opciones</h2>
      <ul>
        <li onClick={() => onSelect('upload')}>Cargar Archivo</li>
        <li onClick={() => onSelect('list')}>Listado de Archivos</li>
      </ul>
    </div>
  );
}

export default Sidebar; // Asegúrate de que el componente se exporta correctamente
