import { useEffect, useState } from 'react';
import Chart from 'react-apexcharts';
import { api } from '../api';
import { FileText, FileSpreadsheet } from 'lucide-react';

interface FlightsTreemapProps {
    /** Filtros operativos (Sector, Fechas, Empresas, etc.) */
    filters: any;
    /** Control de visibilidad para los botones de exportación masiva */
    allowExport?: boolean;
}

/**
 * Visualización por Origen: Mapa de Árbol y Rankings de Tráfico.
 * 
 * Este componente es una herramienta de diagnóstico rápido para identificar
 * hubs de origen con mayor presión operativa. Combina un gráfico Treemap
 * dinámico con tablas de clasificación (Top 10 / Bottom 10).
 * 
 * Funcionalidades clave:
 * - Colorización distribuida para máxima distinción entre aeródromos.
 * - Cálculo automático de rankings tras cada actualización de filtros.
 * - Exportación de reportes de origen en formatos estándares.
 * 
 * @param props - Filtros y flags de permisos.
 */
export const FlightsTreemap = ({ filters, allowExport = true }: FlightsTreemapProps) => {
    // series: Datos formateados para el motor ApexCharts [ { data: [{ x, y }] } ]
    const [series, setSeries] = useState<any[]>([]);

    // top10: Los 10 aeropuertos con mayor volumen para la tabla de líderes
    const [top10, setTop10] = useState<any[]>([]);

    // bottom10: Los 10 aeropuertos con menor volumen (excluyendo actividad nula)
    const [bottom10, setBottom10] = useState<any[]>([]);

    // loading: Estado de bloqueo durante la sincronización con DuckDB
    const [loading, setLoading] = useState(false);

    const [empty, setEmpty] = useState(false);

    const [exporting, setExporting] = useState(false);

    /**
     * Orquestador de obtención de datos.
     * Transforma el estado reactivo del frontend en un payload compatible con el backend.
     */
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setEmpty(false);
            try {
                // Mapeo exhaustivo de filtros para la consulta SQL predictiva/estadística
                const payload = {
                    start_date: filters.startDate || null,
                    end_date: filters.endDate || null,
                    min_level: filters.minLevel || null,
                    max_level: filters.maxLevel || null,
                    origins: filters.selectedOrigins?.map((o: any) => o.value?.icao_code || o.value) || [],
                    destinations: filters.selectedDestinations?.map((d: any) => d.value?.icao_code || d.value) || [],
                    matriculas: filters.selectedMetricula?.map((m: any) => m.value) || [],
                    tipo_aeronave: filters.selectedTipoAeronave?.map((t: any) => t.value) || [],
                    empresa: filters.selectedEmpresa?.map((e: any) => e.value) || [],
                    tipo_vuelo: filters.selectedTipoVuelo?.map((t: any) => t.value) || [],
                    callsign: filters.selectedCallsign?.map((c: any) => c.value) || [],
                };

                const response = await api.post('/stats/flights-by-origin', payload);

                if (response.data && response.data.length > 0) {
                    // Ordenamiento descendente para cálculo de cuantiles y tablas
                    const sortedData = [...response.data].sort((a: any, b: any) => b.value - a.value);

                    const formattedData = sortedData.map((item: any) => ({
                        x: item.name,
                        y: item.value
                    }));

                    setSeries([{ data: formattedData }]);
                    setTop10(sortedData.slice(0, 10));

                    // Filtrado de ruido (ceros) para el ranking inferior
                    const nonZero = sortedData.filter((d: any) => d.value > 0);
                    setBottom10(nonZero.slice(-10));
                } else {
                    setEmpty(true);
                    setSeries([]);
                    setTop10([]);
                    setBottom10([]);
                }
            } catch (error) {
                console.error("Fallo al sincronizar orígenes:", error);
                setEmpty(true);
            } finally {
                setLoading(false);
            }
        };

        const t = setTimeout(fetchData, 500);
        return () => clearTimeout(t);
    }, [filters]);

    /**
     * Motor de exportación de reportes de tráfico de origen.
     * @param type - Formato de archivo (pdf/excel).
     */
    const handleExport = async (type: 'pdf' | 'excel') => {
        if (exporting) return;
        setExporting(true);
        try {
            const payload = {
                start_date: filters.startDate || null,
                end_date: filters.endDate || null,
                min_level: filters.minLevel || null,
                max_level: filters.maxLevel || null,
                origins: filters.selectedOrigins?.map((o: any) => o.value?.icao_code || o.value) || [],
                destinations: filters.selectedDestinations?.map((d: any) => d.value?.icao_code || d.value) || [],
                matriculas: filters.selectedMetricula?.map((m: any) => m.value) || [],
                tipo_aeronave: filters.selectedTipoAeronave?.map((t: any) => t.value) || [],
                empresa: filters.selectedEmpresa?.map((e: any) => e.value) || [],
                tipo_vuelo: filters.selectedTipoVuelo?.map((t: any) => t.value) || [],
                callsign: filters.selectedCallsign?.map((c: any) => c.value) || [],
            };

            const endpoint = type === 'pdf' ? '/reports/origin/pdf' : '/reports/origin/excel';
            const filename = `rep_origen_${new Date().toISOString().slice(0, 10)}.${type === 'pdf' ? 'pdf' : 'xlsx'}`;

            const response = await api.post(endpoint, payload, { responseType: 'blob' });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.parentNode?.removeChild(link);
        } catch (error: any) {
            console.error("Fallo al exportar reporte de origen:", error);
        } finally {
            setExporting(false);
        }
    };

    // CONFIGURACIÓN VISUAL DEL TREEMAP (ApexCharts)
    const options: any = {
        legend: {
            show: false
        },
        chart: {
            height: 500,
            type: 'treemap',
            toolbar: {
                show: true
            },
            fontFamily: 'Inter, sans-serif',
            animations: {
                enabled: true
            }
        },
        title: {
            text: undefined
        },
        // Paleta de colores vibrantes para distinguir aeropuertos
        colors: [
            '#3b82f6', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308',
            '#22c55e', '#06b6d4', '#6366f1', '#d946ef', '#ef4444', '#14b8a6',
            '#64748b', '#a855f7', '#d946ef', '#f43f5e'
        ],
        plotOptions: {
            treemap: {
                distributed: true,
                enableShades: true,
                shadeIntensity: 0.5,
                reverseNegativeShade: true,
                useFillColorAsStroke: false
            }
        },
        dataLabels: {
            enabled: true,
            style: {
                fontSize: '12px',
                fontWeight: 'bold',
                colors: ['#ffffff']
            },
            formatter: function (text: string, op: any) {
                return [text, op.value]; // Muestra Nombre y Cantidad dentro del cuadro
            },
            offsetY: -4
        },
        tooltip: {
            enabled: true,
            theme: 'light',
            y: {
                formatter: function (value: number) {
                    return value + " Vuelos";
                }
            }
        }
    };

    // RENDERIZADO CONDICIONAL: Estados de Carga y Vacío
    if (loading) return (
        <div className="h-96 flex justify-center items-center text-slate-400 gap-2">
            <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            Cargando estadísticas de origen...
        </div>
    );

    if (empty) return (
        <div className="h-96 flex justify-center items-center text-slate-400 bg-slate-50 rounded-xl border-dashed border-2 border-slate-200">
            No se encontraron vuelos para los filtros seleccionados.
        </div>
    );

    return (
        <div className="w-full bg-white p-2 rounded-xl">
            {/* BOTONES DE EXPORTACIÓN RÁPIDA */}
            {allowExport && (
                <div className="flex justify-end gap-2 mb-2">
                    <button
                        onClick={() => handleExport('pdf')}
                        disabled={exporting}
                        className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-white bg-rose-500 rounded hover:bg-rose-600 transition-colors disabled:opacity-50"
                        title="Descargar PDF"
                    >
                        <FileText className="w-3.5 h-3.5" />
                        PDF
                    </button>
                    <button
                        onClick={() => handleExport('excel')}
                        disabled={exporting}
                        className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-white bg-emerald-600 rounded hover:bg-emerald-700 transition-colors disabled:opacity-50"
                        title="Descargar Excel"
                    >
                        <FileSpreadsheet className="w-3.5 h-3.5" />
                        Excel
                    </button>
                </div>
            )}

            {/* ÁREA DEL GRÁFICO */}
            <div className="h-[520px] mb-6">
                <Chart
                    options={options}
                    series={series}
                    type="treemap"
                    height={500}
                />
            </div>

            {/* SECCIÓN DE RANKINGS (TABLAS DETALLADAS) */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* TABLA: TOP 10 (MAYOR DEMANDA) */}
                <div className="overflow-hidden rounded-lg border border-slate-200 shadow-sm">
                    <div className="bg-slate-50 px-4 py-3 border-b border-slate-200">
                        <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                            <span className="w-2 h-2 bg-indigo-500 rounded-full"></span>
                            Top 10 Orígenes (Más frecuentes)
                        </h3>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-slate-200">
                            <thead className="bg-white">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider w-16">#</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Aeropuerto</th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Vuelos</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-slate-200">
                                {top10.map((item, index) => (
                                    <tr key={item.name + 'top'} className="hover:bg-slate-50 transition-colors">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{index + 1}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">{item.name}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-mono font-semibold text-indigo-600">{item.value.toLocaleString()}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* TABLA: BOTTOM 10 (MENOR DEMANDA) */}
                {bottom10.length > 0 && (
                    <div className="overflow-hidden rounded-lg border border-slate-200 shadow-sm">
                        <div className="bg-slate-50 px-4 py-3 border-b border-slate-200">
                            <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                                <span className="w-2 h-2 bg-rose-500 rounded-full"></span>
                                Bottom 10 Orígenes (Menos frecuentes)
                            </h3>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-slate-200">
                                <thead className="bg-white">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider w-16">#</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Aeropuerto</th>
                                        <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Vuelos</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-slate-200">
                                    {bottom10.map((item, index) => (
                                        <tr key={item.name + 'bottom'} className="hover:bg-slate-50 transition-colors">
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{series[0]?.data.length - 10 + index + 1}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">{item.name}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-mono font-semibold text-rose-500">{item.value.toLocaleString()}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
