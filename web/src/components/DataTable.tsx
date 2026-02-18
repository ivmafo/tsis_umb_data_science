import React, { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface DataTableProps {
    data: any[];
    title?: string;
}

/**
 * Componente DataTable.
 * Tabla genérica con paginación automática y detección dinámica de columnas.
 * Ideal para mostrar muestras de datos crudos (vuelos, logs, etc.).
 */
interface DataTableProps {
    /** Conjunto de datos crudos (Array de objetos con llaves dinámicas) */
    data: any[];
    /** Título opcional para contextualizar el origen de la muestra */
    title?: string;
}

/**
 * Componente de Infraestructura: Tabla de Datos Universitaria.
 * 
 * Este componente proporciona una interfaz agnóstica para la visualización 
 * de registros tabulares. Implementa detección automática de esquema (headers)
 * y paginación local eficiente para grandes volúmenes de muestreo.
 * 
 * Capacidades:
 * - Normalización de nombres de columnas (Snake to Upper Case).
 * - Paginación reactiva controlada por estado interno.
 * - Sincronización automática de punteros al cambiar el pool de datos.
 * 
 * @param props - Datos a renderizar y metadatos de título.
 */
export const DataTable: React.FC<DataTableProps> = ({ data, title = "Datos de Muestreo" }) => {
    // currentPage: Indice de navegación (1-based) para el visor de registros
    const [currentPage, setCurrentPage] = useState(1);

    // pageSize: Define el 'chunk' de visualización por vista técnica
    const pageSize = 10;

    // Efecto de limpieza: Resetea el puntero al cambiar el contexto de filtrado
    React.useEffect(() => {
        setCurrentPage(1);
    }, [data]);

    // Renderizado preventivo si no hay registros activos
    if (!data || data.length === 0) {
        return (
            <div className="mt-8 p-8 text-center bg-slate-50 rounded-lg border border-dashed border-slate-300 text-slate-500 italic">
                No se detectaron registros para los criterios de búsqueda actuales.
            </div>
        );
    }

    // Cálculos de segmentación de ventana (Windowing)
    const totalPages = Math.ceil(data.length / pageSize);
    const startIndex = (currentPage - 1) * pageSize;
    const currentData = data.slice(startIndex, startIndex + pageSize);

    // Detección automática de Cabeceras basada en las llaves del primer objeto
    const headers = Object.keys(data[0]);

    return (
        <div className="mt-8 animate-in fade-in duration-500">
            <h3 className="text-sm font-bold text-slate-700 mb-4 flex items-center gap-2 uppercase tracking-tighter">
                <span className="text-indigo-500">📊</span> {title}
                <span className="text-[10px] font-medium text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-100">
                    {data.length} registros totales
                </span>
            </h3>

            <div className="overflow-x-auto rounded-xl border border-slate-200 shadow-sm bg-white">
                <table className="w-full text-sm text-left text-slate-600">
                    <thead className="text-[11px] text-slate-500 uppercase bg-slate-50 border-b border-slate-200 font-bold tracking-widest">
                        <tr>
                            {headers.map((header) => (
                                <th key={header} className="px-6 py-4">
                                    {header.replace(/_/g, ' ')}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {currentData.map((row, rowIndex) => (
                            <tr key={rowIndex} className="hover:bg-indigo-50/30 transition-colors">
                                {headers.map((header) => (
                                    <td key={`${rowIndex}-${header}`} className="px-6 py-3 font-medium text-slate-700">
                                        {row[header]?.toString() || '-'}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Controles de Navegación de Página */}
            {totalPages > 1 && (
                <div className="flex items-center justify-between mt-4 px-2">
                    <div className="text-[12px] text-slate-400 font-medium">
                        Mostrando bloque {startIndex + 1} a {Math.min(startIndex + pageSize, data.length)}
                    </div>
                    <div className="flex items-center gap-4 bg-white p-1 rounded-lg border border-slate-100 shadow-sm">
                        <button
                            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                            disabled={currentPage === 1}
                            className="p-1.5 text-slate-500 hover:text-indigo-600 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                        >
                            <ChevronLeft size={18} />
                        </button>
                        <span className="text-xs font-bold text-indigo-700 min-w-[80px] text-center">
                            {currentPage} / {totalPages}
                        </span>
                        <button
                            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                            disabled={currentPage === totalPages}
                            className="p-1.5 text-slate-500 hover:text-indigo-600 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                        >
                            <ChevronRight size={18} />
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};
