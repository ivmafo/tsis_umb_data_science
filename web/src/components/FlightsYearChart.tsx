import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LabelList } from 'recharts';
import { api } from '../api';

import { FileText, FileSpreadsheet } from 'lucide-react';

interface FlightsYearChartProps {
    /** Filtros globales del dashboard (fechas, aeropuertos, empresas) */
    filters: any;
    /** Habilita la exportación a formatos PDF/Excel */
    allowExport?: boolean;
}

/**
 * Visualización Histórica: Evolución Anual de Vuelos.
 * 
 * Componente que renderiza un gráfico de barras comparativo para visualizar 
 * el volumen total de vuelos procesados agrupado por año calendario.
 * 
 * Aspectos técnicos:
 * - Utiliza Recharts para el renderizado SVG.
 * - Soporta scroll horizontal dinámico si hay demasiados años en la serie.
 * - Implementa exportación delegada a endpoints de infraestructura.
 * 
 * @param props - Configuración de filtros y permisos de exportación.
 */
export const FlightsYearChart = ({ filters, allowExport = true }: FlightsYearChartProps) => {
    // data: Array de objetos { name: string (Año), value: number (Vuelos) }
    const [data, setData] = useState<any[]>([]);

    // loading: Control de feedback visual durante la carga (Spinner)
    const [loading, setLoading] = useState(false);

    // empty: Flag para renderizado alternativo si no hay resultados
    const [empty, setEmpty] = useState(false);

    // exporting: Bloqueo de botones durante la generación de reportes binarios
    const [exporting, setExporting] = useState(false);

    /**
     * Gestiona la solicitud de reportes anuales.
     * Envía los filtros actuales y fuerza la descarga del archivo generado.
     */
    const handleExport = async (type: 'pdf' | 'excel') => {
        if (exporting) return;
        setExporting(true);
        try {
            const endpoint = type === 'pdf' ? '/reports/time/pdf' : '/reports/time/excel';
            const filename = `reporte_tiempo_anual.${type === 'pdf' ? 'pdf' : 'xlsx'}`;
            const payload = { ...filters, groupBy: 'year' };

            const response = await api.post(endpoint, payload, { responseType: 'blob' });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.parentNode?.removeChild(link);
        } catch (error) {
            console.error("Fallo en exportación anual:", error);
            alert("Error al generar el documento.");
        } finally {
            setExporting(false);
        }
    };

    // Efecto para sincronizar el gráfico con los filtros cada 500ms (Debounce)
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setEmpty(false);
            try {
                // Inyecta 'year' como parámetro de agrupación para el backend DuckDB
                const response = await api.post('/stats/flights-over-time', { ...filters, groupBy: 'year' });

                if (response.data && response.data.length > 0) {
                    setData(response.data);
                } else {
                    setEmpty(true);
                    setData([]);
                }
            } catch (error) {
                console.error("Error al obtener estadísticas anuales:", error);
                setEmpty(true);
            } finally {
                setLoading(false);
            }
        };

        const t = setTimeout(fetchData, 500);
        return () => clearTimeout(t);
    }, [filters]);

    if (loading) return (
        <div className="h-[400px] flex justify-center items-center text-slate-400 gap-2">
            <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            Cargando...
        </div>
    );

    if (empty) return (
        <div className="h-[400px] flex justify-center items-center text-slate-400 bg-slate-50 rounded-xl border-dashed border-2 border-slate-200">
            No hay datos anuales para la selección.
        </div>
    );

    // Dynamic width for years - Bars can be much wider
    const minBarWidth = 150;
    const calculateWidth = () => Math.max(data.length * minBarWidth, 500); // reduced min container 

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
                                bottom: 40,
                            }}
                        >
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                            <XAxis
                                dataKey="name"
                                angle={0}
                                textAnchor="middle"
                                height={40}
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
                            <Bar dataKey="value" name="Vuelos" fill="#8b5cf6" radius={[4, 4, 0, 0]} barSize={60}>
                                <LabelList dataKey="value" position="top" fill="#334155" fontSize={12} formatter={(val: any) => val} />
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};
