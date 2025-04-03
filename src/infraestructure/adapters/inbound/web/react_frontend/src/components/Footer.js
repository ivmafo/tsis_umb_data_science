/**
 * Módulo que implementa el pie de página de la aplicación,
 * siguiendo los principios de arquitectura hexagonal y clean architecture.
 * 
 * Este componente actúa como un adaptador de interfaz de usuario en la capa
 * de infraestructura, presentando información estática del pie de página.
 */

import React from 'react';
import './Footer.css';

/**
 * Componente para el pie de página.
 * 
 * Implementa la interfaz de usuario para mostrar información de copyright
 * y derechos de autor, actuando como un adaptador primario simple
 * que no requiere interacción con los puertos del dominio.
 * 
 * @component
 */
function Footer() {
    return (
        <footer className="footer">
            <p>&copy; 2025 Aplicacion / Algoritmos DataScience. Todos los derechos reservados. Ivan M. Forero.</p>
        </footer>
    );
}

export default Footer;
