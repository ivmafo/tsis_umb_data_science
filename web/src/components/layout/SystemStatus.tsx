import { useState, useEffect } from 'react';
import { api } from '../../api';
import { FaCheckCircle, FaSpinner } from 'react-icons/fa';

export const SystemStatus = () => {
    const [status, setStatus] = useState<{ is_running: boolean; current_file?: string }>({ is_running: false });

    useEffect(() => {
        const checkStatus = async () => {
            try {
                const res = await api.get('/etl/status');
                setStatus(res.data);
            } catch (e) {
                console.error("Status check failed", e);
            }
        };

        checkStatus();
        const interval = setInterval(checkStatus, 3000);
        return () => clearInterval(interval);
    }, []);

    if (!status.is_running) {
        return (
            <div className="px-6 py-4 border-t border-white/10 transition-colors">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center border border-emerald-500/50">
                        <FaCheckCircle className="text-emerald-400" />
                    </div>
                    <div>
                        <p className="text-sm font-medium text-white/90">Estado del Sistema</p>
                        <p className="text-xs text-emerald-400">Operativo</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="px-6 py-4 border-t border-white/10 bg-blue-900/30 transition-colors animate-pulse">
            <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center border border-blue-500/50">
                    <FaSpinner className="text-blue-400 animate-spin" />
                </div>
                <div className="overflow-hidden">
                    <p className="text-sm font-medium text-white/90">Procesando...</p>
                    <p className="text-xs text-blue-300 truncate w-40" title={status.current_file}>
                        {status.current_file || 'Iniciando...'}
                    </p>
                </div>
            </div>
        </div>
    );
};
