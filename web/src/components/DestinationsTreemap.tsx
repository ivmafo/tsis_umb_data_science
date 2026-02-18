import { useEffect, useState } from 'react';
import Chart from 'react-apexcharts';
import { api } from '../api';
import { FileText, FileSpreadsheet } from 'lucide-react';

interface DestinationsTreemapProps {
    /** Filtros globales (Contexto de tiempo, aeropuerto y empresa) */
    filters: any;
    /** Habilita los controles de descarga de reportes */
    allowExport?: boolean;
}

/**
 * Visualización por Destino: Mapa de Árbol Jerárquico.
 * 
 * Este componente analiza la terminalización de las rutas aéreas, permitiendo
 * identificar los destinos con mayor flujo entrante. Complementa el análisis
 * de origen para proporcionar una visión bidireccional de la red ATC.
 * 
 * Características:
 * - Clasificación automática de Top 10 destinos preferentes.
 * - Desglose de los 10 destinos con menor frecuencia operativa.
 * - Animaciones suaves para transiciones de filtrado.
 * 
 * @param props - Filtros operativos y permisos.
 */
export const DestinationsTreemap = ({ filters, allowExport = true }: DestinationsTreemapProps) => {
    // series: [{ data: [{ x: 'Destino', y: Cantidad }] }]
    const [series, setSeries] = useState<any[]>([]);

    // topData: Ranking de los 10 destinos líderes
    const [topData, setTopData] = useState<any[]>([]);

    // bottomData: Ranking de los 10 destinos con menor tráfico activo
    const [bottomData, setBottomData] = useState<any[]>([]);

    // loading: Feedback visual durante la ejecución de la consulta DuckDB
    const [loading, setLoading] = useState(false);

    const [empty, setEmpty] = useState(false);

    const [exporting, setExporting] = useState(false);

    /**
     * Sincronizador de datos con el bus de filtros del Dashboard.
     * Implementa un debounce técnico para optimizar la carga del servidor.
     */
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setEmpty(false);
            try {
                // Estandarización del payload para el endpoint de destinos
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

                const response = await api.post('/stats/flights-by-destination', payload);

                if (response.data && response.data.length > 0) {
                    // Mapeo específico para el esquema de datos de Treemap
                    const formattedData = response.data.map((item: any) => ({
                        x: item.name,
                        y: item.value
                    }));

                    setSeries([{ data: formattedData }]);

                    // Segmentación de rankings para visualización tabular
                    setTopData(response.data.slice(0, 10));
                    setBottomData(response.data.slice(-10));
                } else {
                    setEmpty(true);
                    setSeries([]);
                    setTopData([]);
                    setBottomData([]);
                }
            } catch (error) {
                console.error("Fallo técnico en carga de destinos:", error);
                setEmpty(true);
            } finally {
                setLoading(false);
            }
        };

        const t = setTimeout(fetchData, 500);
        return () => clearTimeout(t);
    }, [filters]);

    /**
     * Motor de reporte de destinos.
     * @param type - Formato de documento solicitado.
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

            const endpoint = type === 'pdf' ? '/reports/destination/pdf' : '/reports/destination/excel';
            const filename = `rep_destino_${new Date().toISOString().slice(0, 10)}.${type === 'pdf' ? 'pdf' : 'xlsx'}`;

            const response = await api.post(endpoint, payload, { responseType: 'blob' });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.parentNode?.removeChild(link);
        } catch (error: any) {
            console.error("Fallo en generación de reporte de destino:", error);
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
                show: false
            },
            fontFamily: 'Inter, sans-serif',
            animations: {
                enabled: true,
                easing: 'easeinout',
                speed: 800,
                animateGradually: {
                    enabled: true,
                    delay: 150
                },
                dynamicAnimation: {
                    enabled: true,
                    speed: 350
                }
            }
        },
        title: {
            text: undefined
        },
        // PALETA: Colores verdosos y cianes para diferenciar visualmente del treemap de origen
        colors: [
            '#10b981', '#34d399', '#f43f5e', '#f97316', '#eab308', '#8b5cf6',
            '#3b82f6', '#06b6d4', '#6366f1', '#d946ef', '#ef4444', '#14b8a6',
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
                fontSize: '14px',
                fontWeight: 'bold',
                colors: ['#ffffff']
            },
            formatter: function (text: string, op: any) {
                return [text, op.value];
            },
            offsetY: -4
        },
        tooltip: {
            enabled: true,
            theme: 'light',
            style: {
                fontSize: '14px',
                fontFamily: 'Inter, sans-serif',
            },
            x: {
                show: true,
            },
            y: {
                formatter: function (value: number) {
                    return value + " Vuelos";
                },
                title: {
                    formatter: function () {
                        return "";
                    }
                }
            },
            marker: {
                show: false,
            }
        },
        stroke: {
            show: true,
            width: 2,
            colors: ['#fff']
        }
    };

    if (loading) return (
        <div className="h-96 flex justify-center items-center text-slate-400 gap-2">
            <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            Cargando estadísticas de destino...
        </div>
    );

    if (empty) return (
        <div className="h-96 flex justify-center items-center text-slate-400 bg-slate-50 rounded-xl border-dashed border-2 border-slate-200">
            No se encontraron vuelos para los filtros aplicadores.
        </div>
    );

    return (
        <div className="w-full bg-white p-2 rounded-xl">
            {/* BOTONES DE ACCIÓN: EXPORTAR */}
            {allowExport && (
                <div className="flex justify-end gap-2 mb-2">
                    <button
                        onClick={() => handleExport('pdf')}
                        disabled={exporting}
                        className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-white bg-rose-500 rounded hover:bg-rose-600 transition-colors disabled:opacity-50"
                        title="Exportar a PDF"
                    >
                        <FileText className="w-3.5 h-3.5" />
                        PDF
                    </button>
                    <button
                        onClick={() => handleExport('excel')}
                        disabled={exporting}
                        className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-white bg-emerald-600 rounded hover:bg-emerald-700 transition-colors disabled:opacity-50"
                        title="Exportar a Excel"
                    >
                        <FileSpreadsheet className="w-3.5 h-3.5" />
                        Excel
                    </button>
                </div>
            )}
            {/* ÁREA DEL GRÁFICO PRINCIPAL */}
            <div className="h-[520px] mb-6">
                <Chart
                    options={options}
                    series={series}
                    type="treemap"
                    height={500}
                />
            </div>

            {/* SECCIÓN INFERIOR: RANKINGS EN TABLAS */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* TABLA: TOP 10 DESTINOS */}
                <div className="overflow-hidden rounded-lg border border-slate-200 shadow-sm">
                    <div className="bg-slate-50 px-4 py-3 border-b border-slate-200">
                        <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                            <span className="w-2 h-2 bg-emerald-500 rounded-full"></span>
                            Top 10 Destinos (Más frecuentes)
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
                                {topData.map((item, index) => (
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

                {/* TABLA: BOTTOM 10 DESTINOS */}
                {bottomData.length > 0 && (
                    <div className="overflow-hidden rounded-lg border border-slate-200 shadow-sm">
                        <div className="bg-slate-50 px-4 py-3 border-b border-slate-200">
                            <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                                <span className="w-2 h-2 bg-rose-500 rounded-full"></span>
                                Bottom 10 Destinos (Menos frecuentes)
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
                                    {bottomData.map((item, index) => (
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
