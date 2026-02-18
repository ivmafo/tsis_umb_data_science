import { useState, useEffect } from 'react';
import { api } from '../api';
import { FaCheckCircle, FaExclamationCircle, FaSpinner } from 'react-icons/fa';

interface HistoryItem {
    id: number;
    file_name: string;
    processed_at: string;
    status: string;
    row_count: number | null;
    error_message: string | null;
}

export const HistoryView = () => {
    const [history, setHistory] = useState<HistoryItem[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchHistory = async () => {
        try {
            const res = await api.get('/etl/history');
            setHistory(res.data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHistory();
        const interval = setInterval(fetchHistory, 5000); // Poll every 5s
        return () => clearInterval(interval);
    }, []);

    if (loading && history.length === 0) {
        return <div className="p-8 text-center text-slate-500">Cargando historial...</div>;
    }

    return (
        <div className="space-y-6">
            <header className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-slate-800">Historial de Procesamiento</h2>
                    <p className="text-slate-500">Registro de archivos ingestados y su estado</p>
                </div>
                <button
                    onClick={fetchHistory}
                    className="px-4 py-2 text-sm text-slate-600 hover:bg-white bg-white/50 rounded-lg border border-slate-200 transition-colors"
                >
                    Actualizar
                </button>
            </header>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                <table className="w-full text-sm text-left">
                    <thead className="bg-slate-50 text-slate-500 font-medium border-b border-slate-200">
                        <tr>
                            <th className="px-6 py-4">Archivo</th>
                            <th className="px-6 py-4">Fecha Proceso</th>
                            <th className="px-6 py-4">Estado</th>
                            <th className="px-6 py-4 text-right">Registros</th>
                            <th className="px-6 py-4">Detalles</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {history.map((item) => (
                            <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                                <td className="px-6 py-4 font-medium text-slate-700">{item.file_name}</td>
                                <td className="px-6 py-4 text-slate-500">
                                    {new Date(item.processed_at).toLocaleString()}
                                </td>
                                <td className="px-6 py-4">
                                    <div className="flex items-center gap-2">
                                        {item.status === 'COMPLETED' && <FaCheckCircle className="text-emerald-500" />}
                                        {item.status === 'ERROR' && <FaExclamationCircle className="text-rose-500" />}
                                        {item.status === 'PROCESSING' && <FaSpinner className="text-blue-500 animate-spin" />}
                                        <span className={
                                            item.status === 'COMPLETED' ? 'text-emerald-700' :
                                                item.status === 'ERROR' ? 'text-rose-700' : 'text-blue-700'
                                        }>
                                            {item.status}
                                        </span>
                                    </div>
                                </td>
                                <td className="px-6 py-4 text-right font-mono text-slate-600">
                                    {item.row_count?.toLocaleString() || '-'}
                                </td>
                                <td className="px-6 py-4 text-slate-500 max-w-xs truncate" title={item.error_message || ''}>
                                    {item.error_message || '-'}
                                </td>
                            </tr>
                        ))}
                        {history.length === 0 && (
                            <tr>
                                <td colSpan={5} className="px-6 py-12 text-center text-slate-400">
                                    No hay registros de procesamiento aún.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};
