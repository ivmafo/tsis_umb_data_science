import type { ReactNode } from 'react';
import { Sidebar } from './Sidebar';

interface MainLayoutProps {
    /** Contenido dinámico inyectado por el Router o switch de vistas */
    children: ReactNode;
    /** Identificador de la vista actual para resaltado de Sidebar */
    currentView: string;
    /** Navegador de estados de vista superior */
    onNavigate: (view: string) => void;
}

/**
 * Componente de Infraestructura: Esqueleto Maestro de la Aplicación.
 * 
 * Proporciona el marco estructural unificado para toda la plataforma,
 * integrando la barra lateral de navegación y el contenedor principal
 * de renderizado con animaciones de entrada.
 * 
 * Atributos Técnicos:
 * - Layout Responsivo: Main lateral con margen fijo para la Sidebar (72 units).
 * - Optimización de Contenido: Max-width de 1600px para evitar dispersión en monitores ultra-wide.
 * - Transiciones: Animación fade-in nativa para mejorar la percepción de carga.
 * 
 * @param props - Inyección de hijos y control de navegación.
 */
export const MainLayout = ({ children, currentView, onNavigate }: MainLayoutProps) => {
    return (
        <div className="min-h-screen bg-slate-50 flex">
            {/* Componente de Navegación Lateral */}
            <Sidebar currentView={currentView} onSelect={onNavigate} />

            {/* Área de Trabajo Principal */}
            <main className="flex-1 ml-72 p-8 transition-all duration-300">
                <div className="max-w-[1600px] mx-auto animate-fade-in">
                    {children}
                </div>
            </main>
        </div>
    );
};
