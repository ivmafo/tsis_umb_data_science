// src\infraestructure\adapters\inbound\web\react_frontend\src\components\Sidebar.js
/**
 * Módulo que implementa la barra lateral de navegación,
 * siguiendo los principios de arquitectura hexagonal y clean architecture.
 * 
 * Este componente actúa como un adaptador de interfaz de usuario en la capa
 * de infraestructura, proporcionando la navegación principal entre las
 * diferentes funcionalidades de la aplicación.
 */

import React from 'react';
import './Sidebar.css';

/**
 * Componente de barra lateral para navegación.
 * 
 * Implementa la interfaz de usuario para la navegación principal,
 * actuando como un adaptador primario que comunica las selecciones
 * del usuario al componente padre.
 * 
 * @component
 * @param {Object} props - Propiedades del componente
 * @param {Function} props.onSelect - Callback para manejar la selección de opciones
 */
function Sidebar({ onSelect }) {
    return (
        <div className="sidebar">
            <div className="sidebar-header">
                <h2>Opciones</h2>
            </div>
            <ul className="sidebar-menu">
                <li onClick={() => onSelect('list')}>Listado de Archivos</li>
                <li onClick={() => onSelect('upload')}>Cargar Archivo</li>
                <li onClick={() => onSelect('uploadDir')}>Cargar Archivos Desde Directorio</li>
                <li onClick={() => onSelect('config')}>Configuración General</li>
                <li onClick={() => onSelect('dashboard')}>Tablero</li>
                <li onClick={() => onSelect('levelRanges')}>Rangos de Nivel</li>     
                <li onClick={() => onSelect('atc-capacity')}>ATC Capacity</li>
                <li onClick={() => onSelect('sector-analysis')}>Análisis de Sectores</li>
            </ul>
        </div>
    );
}

export default Sidebar;
