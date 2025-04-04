import React from 'react';
import './Sidebar.css';
import { 
    FaFileAlt, 
    FaUpload, 
    FaFolderOpen, 
    FaCogs, 
    FaChartBar, 
    FaLayerGroup,
    FaPlane,
    FaChartArea
} from 'react-icons/fa';

function Sidebar({ onSelect }) {
    return (
        <div className="sidebar">
            <div className="sidebar-header">
                <h2>Opciones</h2>
            </div>
            <ul className="sidebar-menu">
                <li onClick={() => onSelect('list')}>
                    <FaFileAlt className="menu-icon" />
                    <span>Listado de Archivos</span>
                </li>
                <li onClick={() => onSelect('upload')}>
                    <FaUpload className="menu-icon" />
                    <span>Cargar Archivo</span>
                </li>
                <li onClick={() => onSelect('uploadDir')}>
                    <FaFolderOpen className="menu-icon" />
                    <span>Cargar Archivos Desde Directorio</span>
                </li>
                <li onClick={() => onSelect('config')}>
                    <FaCogs className="menu-icon" />
                    <span>Configuración General</span>
                </li>
                <li onClick={() => onSelect('dashboard')}>
                    <FaChartBar className="menu-icon" />
                    <span>Tablero</span>
                </li>
                <li onClick={() => onSelect('levelRanges')}>
                    <FaLayerGroup className="menu-icon" />
                    <span>Rangos de Nivel</span>
                </li>
                <li onClick={() => onSelect('atc-capacity')}>
                    <FaPlane className="menu-icon" />
                    <span>ATC Capacity</span>
                </li>
                <li onClick={() => onSelect('sector-analysis')}>
                    <FaChartArea className="menu-icon" />
                    <span>Análisis de Sectores</span>
                </li>
            </ul>
        </div>
    );
}

export default Sidebar;
