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

export const Sidebar = ({ currentView, onSelect }: SidebarProps) => {
    const [expanded, setExpanded] = useState<string[]>(['dashboard']);
    const [isIngesting, setIsIngesting] = useState(false);

    const handleIngest = async () => {
        if (confirm("¿Estás seguro de que quieres borrar y recargar todos los datos? Esta acción no se puede deshacer.")) {
            setIsIngesting(true);
            try {
                await ingestData(true);
                alert("Proceso de ingestión iniciado. Los datos se actualizarán en breve.");
            } catch (error) {
                alert("Error al iniciar la ingestión.");
                console.error(error);
            } finally {
                setIsIngesting(false);
            }
        }
    };

    const toggleExpand = (id: string, hasChildren: boolean) => {
        if (!hasChildren) return;
        setExpanded(prev =>
            prev.includes(id) ? prev.filter(item => item !== id) : [...prev, id]
        );
    };

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

    const renderMenuItem = (item: any, depth = 0) => {
        const Icon = item.icon;
        const hasChildren = item.children && item.children.length > 0;
        const isExpanded = expanded.includes(item.id);
        const isActive = currentView === item.id;
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
            <div className="p-6 border-b border-white/10">
                <h2 className="text-2xl font-bold tracking-tight">CEA Data</h2>
                <p className="text-xs text-white/50 mt-1">Sistema de Gestión</p>
            </div>

            <nav className="p-4">
                <ul className="space-y-2">
                    {menuItems.map(item => renderMenuItem(item, 0))}
                </ul>
            </nav>

            <div className="absolute bottom-0 w-full bg-black/20">
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
                            {isIngesting ? 'Procesando...' : 'Volcado manual'}
                        </p>
                    </div>
                </div>

                <div
                    onClick={async () => {
                        if (confirm("ATENCIÓN: ¿Seguro que desea LIMPIAR toda la base de datos? Esto eliminará registros de vuelos y control de archivos.")) {
                            try {
                                await resetDatabase();
                                alert("Base de datos reiniciada correctamente. (Tablas truncadas y recreadas)");
                            } catch (e) {
                                alert("Error al reiniciar BD.");
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
                        <p className="text-xs text-red-400">Truncate & Recreate</p>
                    </div>
                </div>

                <SystemStatus />
            </div>
        </aside>
    );
};
