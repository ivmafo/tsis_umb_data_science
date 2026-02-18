import { useState } from 'react';
import {
    FaFileAlt,
    FaUpload,
    FaCogs,
    FaChartBar,
    FaGlobe,
    FaPlane,
    FaMapMarkedAlt,
    FaDatabase,
    FaHistory,
    FaCalculator,
    FaClipboardList,
    FaChartLine
} from 'react-icons/fa';
import clsx from 'clsx';
import { ingestData, resetDatabase } from '../../api';
import { FaTrashRestore } from 'react-icons/fa';
import { SystemStatus } from './SystemStatus';

interface SidebarProps {
    currentView: string;
    onSelect: (view: string) => void;
}

/**
 * Componente de Navegación: Barra Lateral Operativa.
 * 
 * Gestiona el árbol de navegación de la aplicación y las acciones de 
 * mantenimiento global de la persistencia (DuckDB). Es el punto de control
 * para la transición entre vistas de análisis y configuración.
 * 
 * Atributos Técnicos:
 * - Menú Jerárquico: Soporta anidamiento de primer nivel para agrupar herramientas (ej: ATC).
 * - Control de Ingesta: Disparador de recarga masiva con bloqueo de estado.
 * - Sincronización de Vista: Callback 'onSelect' para actualizar el router interno.
 */
export const Sidebar = ({ currentView, onSelect }: SidebarProps) => {
    // expanded: Lista de IDs de menús padres que se encuentran desplegados
    const [expanded, setExpanded] = useState<string[]>(['dashboard']);

    // isIngesting: Estado de bloqueo global mientras el backend reconstruye los índices
    const [isIngesting, setIsIngesting] = useState(false);

    /**
     * Controlador de Recarga Masiva de Datos.
     * Realiza un truncado completo de la tabla de vuelos y re-procesa los archivos.
     */
    const handleIngest = async () => {
        if (confirm("ADVERTENCIA DE INTEGRIDAD: ¿Desea reconstruir completamente la base de datos? Se eliminarán los vuelos actuales y se re-indexarán los archivos válidos.")) {
            setIsIngesting(true);
            try {
                // Ingesta forzada: borra y reprocesa
                await ingestData(true);
                alert("Proceso de reconstrucción iniciado. El sistema actualizará los gráficos incrementalmente.");
            } catch (error) {
                alert("Fallo crítico en el motor de ingesta masiva.");
                console.error("Error en handleIngest:", error);
            } finally {
                setIsIngesting(false);
            }
        }
    };

    /**
     * Gestiona el estado de expansión de los acordeones del menú.
     * @param id - Identificador del menú.
     * @param hasChildren - Flag de si el menú es un contenedor.
     */
    const toggleExpand = (id: string, hasChildren: boolean) => {
        if (!hasChildren) return;
        setExpanded(prev =>
            prev.includes(id) ? prev.filter(item => item !== id) : [...prev, id]
        );
    };

    // DEFINICIÓN DEL MAPA DE NAVEGACIÓN: Estructura de menús e iconos
    const menuItems = [
        {
            id: 'dashboard',
            label: 'Tablero',
            icon: FaChartBar,
            children: [
                { id: 'flight-distribution', label: 'Distribución de Vuelos', icon: FaPlane }
            ]
        },
        { id: 'files', label: 'Gestión de Archivos', icon: FaFileAlt },
        { id: 'upload', label: 'Cargar Archivo', icon: FaUpload },
        { id: 'history', label: 'Historial Ingesta', icon: FaHistory },
        { id: 'regions', label: 'Gestión de Regiones', icon: FaGlobe },
        { id: 'airports', label: 'Gestión de Aeropuertos', icon: FaPlane },
        { id: 'region-airports', label: 'Asignación Regiones', icon: FaMapMarkedAlt },
        {
            id: 'atc-capacity',
            label: 'Capacidad ATC',
            icon: FaCalculator,
            children: [
                { id: 'sector-config', label: 'Configuración Sectores', icon: FaCogs },
                { id: 'capacity-report', label: 'Reporte de Capacidad', icon: FaClipboardList }
            ]
        },
        { id: 'predictive', label: 'Predictiva AI', icon: FaChartLine },
        { id: 'config', label: 'Configuración', icon: FaCogs },
    ];

    /**
     * Función recursiva para renderizar cada elemento del menú.
     * Soporta anidamiento y resaltado automático de la vista activa.
     */
    const renderMenuItem = (item: any, depth = 0) => {
        const Icon = item.icon;
        const hasChildren = item.children && item.children.length > 0;
        const isExpanded = expanded.includes(item.id);
        const isActive = currentView === item.id;
        // Si un hijo está activo pero el menú está colapsado, mantenemos el padre con estilo activo
        const isChildActive = hasChildren && item.children.some((child: any) => child.id === currentView);

        return (
            <li key={item.id}>
                <div
                    className={clsx(
                        "w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-300 cursor-pointer",
                        isActive || (isChildActive && !isExpanded)
                            ? "bg-white/20 text-white shadow-lg translate-x-1 font-semibold"
                            : "text-white/70 hover:bg-white/10 hover:text-white hover:translate-x-1",
                        depth > 0 && "ml-4 border-l border-white/20 rounded-l-none"
                    )}
                    onClick={() => {
                        if (hasChildren) {
                            toggleExpand(item.id, true);
                        } else {
                            onSelect(item.id);
                        }
                    }}
                >
                    <div className="flex items-center gap-4">
                        <Icon className={clsx("w-5 h-5", (isActive || isChildActive) ? "text-white" : "text-white/70")} />
                        <span>{item.label}</span>
                    </div>
                    {hasChildren && (
                        <span className="text-xs opacity-70 transform transition-transform duration-200" style={{ transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)' }}>
                            ▼
                        </span>
                    )}
                </div>

                {/* RENDERIZADO DE SUBMENÚS */}
                {hasChildren && isExpanded && (
                    <ul className="mt-1 space-y-1">
                        {item.children.map((child: any) => renderMenuItem(child, depth + 1))}
                    </ul>
                )}
            </li>
        );
    };

    return (
        <aside className="fixed left-0 top-0 h-screen w-72 bg-gradient-to-br from-primary to-primary-dark text-white shadow-2xl z-50 overflow-y-auto">
            {/* LOGO Y TÍTULO */}
            <div className="p-6 border-b border-white/10">
                <h2 className="text-2xl font-bold tracking-tight">CEA Data</h2>
                <p className="text-xs text-white/50 mt-1">Plataforma de Análisis Aeronáutico</p>
            </div>

            {/* NAVEGACIÓN PRINCIPAL */}
            <nav className="p-4">
                <ul className="space-y-2">
                    {menuItems.map(item => renderMenuItem(item, 0))}
                </ul>
            </nav>

            {/* SECCIÓN INFERIOR: ACCIONES DE MANTENIMIENTO */}
            <div className="absolute bottom-0 w-full bg-black/20">

                {/* BOTÓN: RECARGA DE DATOS (INGESTIÓN) */}
                <div
                    onClick={!isIngesting ? handleIngest : undefined}
                    className={clsx(
                        "px-6 py-4 border-t border-white/10 cursor-pointer transition-colors flex items-center gap-3 group",
                        isIngesting ? "opacity-75 cursor-wait" : "hover:bg-white/5"
                    )}
                >
                    <div className={clsx(
                        "w-8 h-8 rounded-full flex items-center justify-center border transition-all",
                        isIngesting
                            ? "bg-amber-500/20 border-amber-500/50"
                            : "bg-blue-500/20 border-blue-500/50 group-hover:bg-blue-500/30"
                    )}>
                        <FaDatabase className={clsx(
                            "w-3.5 h-3.5 transition-colors",
                            isIngesting ? "text-amber-400 animate-spin" : "text-blue-400"
                        )} />
                    </div>
                    <div>
                        <p className="text-sm font-medium text-white/90">Recargar Datos</p>
                        <p className={clsx("text-xs", isIngesting ? "text-amber-400" : "text-blue-400")}>
                            {isIngesting ? 'Procesando...' : 'Actualización masiva'}
                        </p>
                    </div>
                </div>

                {/* BOTÓN: LIMPIEZA TOTAL DE BASE DE DATOS */}
                <div
                    onClick={async () => {
                        if (confirm("PELIGRO: ¿Desea LIMPIAR COMPLETAMENTE la base de datos? Se eliminarán todos los vuelos procesados, históricos de ingestión y caches.")) {
                            try {
                                await resetDatabase();
                                alert("Base de datos reiniciada. Las tablas han sido recreadas.");
                                window.location.reload(); // Recargar para limpiar estados de UI
                            } catch (e) {
                                alert("Error crítico al reiniciar BD.");
                                console.error(e);
                            }
                        }
                    }}
                    className="px-6 py-4 border-t border-white/10 cursor-pointer transition-colors flex items-center gap-3 group hover:bg-white/5"
                >
                    <div className="w-8 h-8 rounded-full flex items-center justify-center border bg-red-500/20 border-red-500/50 group-hover:bg-red-500/30 transition-all">
                        <FaTrashRestore className="w-3.5 h-3.5 text-red-400" />
                    </div>
                    <div>
                        <p className="text-sm font-medium text-white/90">Limpiar BD</p>
                        <p className="text-xs text-red-400">Truncar y Recrear Tablas</p>
                    </div>
                </div>

                {/* INDICADOR DE ESTADO DEL SISTEMA (Consumo de RAM/CPU/DB) */}
                <SystemStatus />
            </div>
        </aside>
    );
};
