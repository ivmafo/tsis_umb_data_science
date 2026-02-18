import React, { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface DataTableProps {
    data: any[];
    title?: string;
}

export const DataTable: React.FC<DataTableProps> = ({ data, title = "Datos de Muestreo" }) => {
    const [currentPage, setCurrentPage] = useState(1);
    const pageSize = 10;

    // Reset pagination when data changes
    React.useEffect(() => {
        setCurrentPage(1);
    }, [data]);

    if (!data || data.length === 0) {
        return (
            <div className="mt-8 p-8 text-center bg-slate-50 rounded-lg border border-dashed border-slate-300 text-slate-500">
                No hay datos de muestreo disponibles para mostrar.
            </div>
        );
    }

    const totalPages = Math.ceil(data.length / pageSize);
    const startIndex = (currentPage - 1) * pageSize;
    const currentData = data.slice(startIndex, startIndex + pageSize);

    // Get headers from first object (robustness check: assumption consistent keys)
    const headers = Object.keys(data[0]);

    return (
        <div className="mt-8">
            <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
                📊 {title}
                <span className="text-xs font-normal text-slate-500 bg-slate-100 px-2 py-1 rounded-full">
                    {data.length} registros
                </span>
            </h3>

            <div className="overflow-x-auto rounded-lg border border-slate-200 shadow-sm">
                <table className="w-full text-sm text-left text-slate-600">
                    <thead className="text-xs text-get-slate-700 uppercase bg-slate-50 border-b border-slate-200">
                        <tr>
                            {headers.map((header) => (
                                <th key={header} className="px-6 py-3 font-semibold text-slate-700">
                                    {header.replace(/_/g, ' ').toUpperCase()}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {currentData.map((row, rowIndex) => (
                            <tr key={rowIndex} className="bg-white border-b border-slate-100 hover:bg-slate-50">
                                {headers.map((header) => (
                                    <td key={`${rowIndex}-${header}`} className="px-6 py-4">
                                        {row[header]?.toString() || '-'}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="flex items-center justify-between mt-4 px-2">
                    <div className="text-sm text-slate-500">
                        Mostrando {startIndex + 1} a {Math.min(startIndex + pageSize, data.length)} de {data.length}
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                            disabled={currentPage === 1}
                            className="p-2 border border-slate-300 rounded-md hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <ChevronLeft size={16} />
                        </button>
                        <span className="text-sm font-medium text-slate-700">
                            Página {currentPage} de {totalPages}
                        </span>
                        <button
                            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                            disabled={currentPage === totalPages}
                            className="p-2 border border-slate-300 rounded-md hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <ChevronRight size={16} />
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};
