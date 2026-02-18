import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LabelList } from 'recharts';
import { api } from '../api';

import { FileText, FileSpreadsheet } from 'lucide-react';

interface FlightsTimeChartProps {
    /** Filtros globales (Temporalidad y Segmentación) */
    filters: any;
    /** Habilita los botones de descarga de series temporales */
    allowExport?: boolean;
}

/**
 * Visualización Evolutiva: Conteo Mensual de Operaciones.
 * 
 * Este componente renderiza una serie de tiempo de alta densidad que permite
 * visualizar la evolución del tráfico mes a mes. Es la herramienta principal
 * para detectar estacionalidad histórica y picos de demanda cíclicos.
 * 
 * Atributos Técnicos:
 * - Cálculo de ancho dinámico basado en el volumen de periodos (Scroll Horizontal).
 * - Agregación forzada por 'month' en el payload de exportación.
 * - Tooltips enriquecidos con métricas de volumen bruto.
 * 
 * @param props - Filtros operativos y permisos de exportación.
 */
export const FlightsTimeChart = ({ filters, allowExport = true }: FlightsTimeChartProps) => {
    // data: Colección de puntos temporales [{ name: 'YYYY-MM', value: N }]
    const [data, setData] = useState<any[]>([]);

    // loading: Feedback de sincronización con DuckDB
    const [loading, setLoading] = useState(false);

    const [empty, setEmpty] = useState(false);

    const [exporting, setExporting] = useState(false);

    /**
     * Motor de exportación de series temporales.
     * @param type - Formato de documento ('pdf' | 'excel').
     */
    const handleExport = async (type: 'pdf' | 'excel') => {
        if (exporting) return;
        setExporting(true);
        try {
            const endpoint = type === 'pdf' ? '/reports/time/pdf' : '/reports/time/excel';
            const filename = `rep_tiempo_mensual.${type === 'pdf' ? 'pdf' : 'xlsx'}`;

            // Inyectamos explícitamente la granularidad mensual para el motor de reportes
            const payload = { ...filters, groupBy: 'month' };

            const response = await api.post(endpoint, payload, { responseType: 'blob' });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.parentNode?.removeChild(link);
        } catch (error) {
            console.error("Fallo crítico en exportación temporal:", error);
        } finally {
            setExporting(false);
        }
    };

    /**
     * Sincronizador de serie de tiempo con el bus de filtros.
     */
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setEmpty(false);
            try {
                // El endpoint /stats/flights-over-time retorna agregación mensual por defecto
                const response = await api.post('/stats/flights-over-time', filters);

                if (response.data && response.data.length > 0) {
                    setData(response.data);
                } else {
                    setEmpty(true);
                    setData([]);
                }
            } catch (error) {
                console.error("Fallo en recuperación de serie temporal:", error);
                setEmpty(true);
            } finally {
                setLoading(false);
            }
        };

        const t = setTimeout(fetchData, 500);
        return () => clearTimeout(t);
    }, [filters]);

    if (loading) return (
        <div className="h-[350px] flex justify-center items-center text-slate-400 gap-2">
            <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            Cargando...
        </div>
    );

    if (empty) return (
        <div className="h-[350px] flex justify-center items-center text-slate-400 bg-slate-50 rounded-xl border-dashed border-2 border-slate-200">
            No hay datos para el periodo seleccionado.
        </div>
    );

    // Dynamic width: Ensure each bar has enough space (e.g., 60px)
    // If total width < container, use 100%
    const minBarWidth = 70;
    const calculateWidth = () => Math.max(data.length * minBarWidth, 1000);

    return (
        <div className="w-full bg-white p-4 rounded-xl overflow-hidden relative">
            {allowExport && (
                <div className="absolute top-2 right-2 flex gap-2 z-10">
                    <button onClick={() => handleExport('pdf')} disabled={exporting} className="p-1.5 text-white bg-rose-500 rounded hover:bg-rose-600 disabled:opacity-50" title="PDF">
                        <FileText className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleExport('excel')} disabled={exporting} className="p-1.5 text-white bg-emerald-600 rounded hover:bg-emerald-700 disabled:opacity-50" title="Excel">
                        <FileSpreadsheet className="w-4 h-4" />
                    </button>
                </div>
            )}
            <div className="overflow-x-auto pb-4">
                <div style={{ width: `${calculateWidth()}px`, height: 400, minWidth: '100%' }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                            data={data}
                            margin={{
                                top: 20,
                                right: 30,
                                left: 20,
                                bottom: 80,
                            }}
                        >
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                            <XAxis
                                dataKey="name"
                                angle={0}
                                textAnchor="end"
                                height={80}
                                tick={{ fill: '#475569', fontSize: 13, fontWeight: 500 }}
                                interval={0}
                            />
                            <YAxis
                                tick={{ fill: '#64748b', fontSize: 12 }}
                                axisLine={false}
                                tickLine={false}
                            />
                            <Tooltip
                                cursor={{ fill: '#f8fafc' }}
                                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                            />
                            <Bar dataKey="value" name="Vuelos" fill="#6366f1" radius={[4, 4, 0, 0]} barSize={40}>
                                <LabelList dataKey="value" position="top" fill="#334155" fontSize={12} formatter={(val: any) => val} />
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
            <p className="text-center text-xs text-slate-400 mt-2">
                Desliza horizontalmente para ver el historial completo
            </p>
        </div>
    );
};
