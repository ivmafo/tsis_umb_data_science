import { useEffect, useState } from 'react';
import ReactApexChart from 'react-apexcharts';
import { api, getPeakHoursForecast } from '../api';
import type { PredictiveFilters } from '../api';
import { MethodologySection } from './MethodologySection';
import { DataTable } from './DataTable';

import { FileText, FileSpreadsheet } from 'lucide-react';

interface PeakHoursHeatmapProps {
    filters: any;
    timeColumn?: string;
    allowExport?: boolean;
    color?: string;
    isPredictive?: boolean;
    aggregation?: 'avg' | 'sum';
}

interface Metrics {
    total_flights?: number;
    days_analyzed?: number;
    avg_daily_flights?: number;
    peak_info?: {
        day: string;
        hour: string;
        volume: number;
        intensity: string;
    };
    description?: string;
    executive_report?: any;
}

export const PeakHoursHeatmap = ({ filters, timeColumn = 'hora_salida', allowExport = true, color, isPredictive = false }: PeakHoursHeatmapProps) => {
    const [series, setSeries] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [empty, setEmpty] = useState(false);
    const [exporting, setExporting] = useState(false);
    const [metrics, setMetrics] = useState<Metrics | null>(null);
    const [history, setHistory] = useState<any[]>([]);
    const [description, setDescription] = useState<string>("");
    const [error, setError] = useState<string | null>(null);

    const handleExport = async (type: 'pdf' | 'excel') => {
        if (exporting) return;
        setExporting(true);
        try {
            const endpoint = type === 'pdf' ? '/reports/heatmap/pdf' : '/reports/heatmap/excel';
            const filename = `reporte_heatmap_${timeColumn}.${type === 'pdf' ? 'pdf' : 'xlsx'}`;
            const payload = { ...filters, timeColumn };

            const response = await api.post(endpoint, payload, { responseType: 'blob' });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.parentNode?.removeChild(link);
        } catch (error) {
            console.error(error);
            alert("Error al exportar.");
        } finally {
            setExporting(false);
        }
    };

    const [chartOptions, setChartOptions] = useState<any>({
        chart: {
            type: 'heatmap',
            toolbar: {
                show: true,
                tools: { download: true, selection: false, zoom: false, zoomin: false, zoomout: false, pan: false, reset: false }
            },
            fontFamily: 'Inter, sans-serif'
        },
        dataLabels: { enabled: false },
        colors: [color || '#008FFB'],
        xaxis: {
            categories: Array.from({ length: 24 }, (_, i) => i.toString().padStart(2, '0')),
            tooltip: { enabled: false },
            labels: { style: { fontSize: '12px' } }
        },
        plotOptions: {
            heatmap: {
                shadeIntensity: 0.5,
                radius: 2,
                useFillColorAsStroke: false,
                colorScale: {
                    ranges: [] // Will be populated dynamically
                }
            }
        },
        stroke: { width: 1, colors: ['#fff'] },
        title: { text: '' },
        tooltip: {
            y: { formatter: function (val: number) { return val + " vuelos" } }
        }
    });

    useEffect(() => {
        const fetchData = async () => {
            if (loading) return;
            setLoading(true);
            setEmpty(false);
            setError(null);
            try {
                if (isPredictive) {
                    // PREDICTIVE MODE (Original Logic)
                    const mappedFilters: PredictiveFilters = {
                        start_date: filters.start_date || filters.startDate,
                        end_date: filters.end_date || filters.endDate,
                        min_level: filters.min_level !== undefined ? filters.min_level : (filters.minLevel ? Number(filters.minLevel) : undefined),
                        max_level: filters.max_level !== undefined ? filters.max_level : (filters.maxLevel ? Number(filters.maxLevel) : undefined),
                        sector_id: filters.sector_id,
                        route: filters.route,
                        airport: filters.airport || (filters.selectedOrigins && filters.selectedOrigins.length > 0 ? filters.selectedOrigins[0].value?.icao_code : undefined),
                    };

                    const data = await getPeakHoursForecast(mappedFilters);

                    if (data && data.heatmap && data.heatmap.length > 0) {
                        const rawData = data.heatmap;
                        setHistory(data.history || []);

                        // Consolidate metrics (Predictive specific)
                        const newMetrics = data.metrics || {};
                        if (data.description) newMetrics.description = data.description;
                        if (data.executive_report) {
                            newMetrics.executive_report = data.executive_report;
                        }

                        setMetrics(newMetrics);
                        setDescription(data.description || "");
                        processHeatmapData(rawData);
                    } else {
                        setEmpty(true);
                        setSeries([]);
                    }
                } else {
                    // HISTORICAL MODE (Flight Distribution Logic - Uses Stats Endpoint)
                    // Construct Payload matching GetPeakHourStats requirements (clean keys)
                    const payload = {
                        start_date: filters.startDate || null,
                        end_date: filters.endDate || null,
                        min_level: filters.minLevel || null,
                        max_level: filters.maxLevel || null,
                        timeColumn: timeColumn, // Passed to backend to select hora_salida/llegada
                        origins: filters.selectedOrigins?.map((o: any) => o.value?.icao_code || o.value) || [],
                        destinations: filters.selectedDestinations?.map((d: any) => d.value?.icao_code || d.value) || [],
                        matriculas: filters.selectedMetricula?.map((m: any) => m.value) || [],
                        tipo_aeronave: filters.selectedTipoAeronave?.map((t: any) => t.value) || [],
                        empresa: filters.selectedEmpresa?.map((e: any) => e.value) || [],
                        tipo_vuelo: filters.selectedTipoVuelo?.map((t: any) => t.value) || [],
                        callsign: filters.selectedCallsign?.map((c: any) => c.value) || [],
                    };

                    const response = await api.post('/stats/flights-peak-hours', payload);

                    if (response.data && response.data.length > 0) {
                        // Backend returns [{day: 1, hour: 0, value: 10}, ...]
                        // We need to map this to the format expected by processHeatmapData or just call it if compatible
                        // The format is compatible! [{day, hour, value}] matches what we used before (dow -> day)
                        // Wait, previous logic used 'dow', 'hour', 'value'. Backend returns 'day', 'hour', 'value'.
                        const rawData = response.data.map((r: any) => ({
                            dow: r.day,
                            hour: r.hour,
                            value: r.value
                        }));

                        processHeatmapData(rawData);

                        // Calculate simple description for historical
                        const total = rawData.reduce((acc: number, curr: any) => acc + curr.value, 0);
                        setDescription(`Total de vuelos analizados: ${total}`);
                        setMetrics({ total_flights: total });

                    } else {
                        setEmpty(true);
                        setSeries([]);
                    }
                }
            } catch (error: any) {
                console.error("Error fetching heatmap data:", error);
                setError(error.message || "Error desconocido");
                setEmpty(true);
            } finally {
                setLoading(false);
            }
        };

        const processHeatmapData = (rawData: any[]) => {
            // Determine Max Value for Dynamic Scaling
            const values = rawData.map((d: any) => d.value);
            const maxVal = Math.max(...values, 10); // Minimum 10 avoid div/0
            const step = maxVal / 5;
            const r1 = Math.ceil(step * 1);
            const r2 = Math.ceil(step * 2);
            const r3 = Math.ceil(step * 3);
            const r4 = Math.ceil(step * 4);

            const safeRanges = [
                { from: 0, to: 0, color: '#f8fafc', name: '0' },
                { from: 1, to: r1, color: '#3b82f6', name: `1 - ${r1}` },
                { from: r1 + 1, to: r2, color: '#06b6d4', name: `${r1 + 1} - ${r2}` },
                { from: r2 + 1, to: r3, color: '#10b981', name: `${r2 + 1} - ${r3}` },
                { from: r3 + 1, to: r4, color: '#f59e0b', name: `${r3 + 1} - ${r4}` },
                { from: r4 + 1, to: 100000, color: '#ef4444', name: `> ${r4}` }
            ];

            setChartOptions((prev: any) => ({
                ...prev,
                colors: [color || '#008FFB'],
                plotOptions: {
                    heatmap: {
                        ...prev.plotOptions.heatmap,
                        colorScale: { ranges: safeRanges }
                    }
                }
            }));

            // Process Data for ApexCharts
            // Days ordered for display (Monday top to Sunday bottom or vice versa)
            // But usually rawData is 1=Mon...7=Sun.
            // We want standard ordering.

            // Re-map days to standard 1-7
            const standardDays = [
                { id: 1, name: 'Lun' }, { id: 2, name: 'Mar' }, { id: 3, name: 'Mié' },
                { id: 4, name: 'Jue' }, { id: 5, name: 'Vie' }, { id: 6, name: 'Sáb' }, { id: 7, name: 'Dom' }
            ];
            const finalSeries = standardDays.map(day => {
                const hourData = Array.from({ length: 24 }, (_, i) => {
                    const match = rawData.find((r: any) => r.dow === day.id && r.hour === i);
                    return { x: i.toString().padStart(2, '0'), y: match ? match.value : 0 };
                });
                return { name: day.name, data: hourData };
            });

            setSeries(finalSeries.reverse());
        };

        const t = setTimeout(fetchData, 500);
        return () => clearTimeout(t);
    }, [filters, color, isPredictive, timeColumn]);

    // Render loading/empty remains the same
    if (loading) return (
        <div className="h-[350px] flex justify-center items-center text-slate-400 gap-2">
            <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            Cargando...
        </div>
    );

    if (empty) return (
        <div className="h-[350px] flex justify-center items-center text-slate-400 bg-slate-50 rounded-xl border-dashed border-2 border-slate-200">
            {error ? error : "No hay datos suficientes para el mapa de calor."}
        </div>
    );

    return (
        <div className="w-full bg-white p-4 rounded-xl">
            {allowExport && (
                <div className="flex justify-end gap-2 mb-2">
                    <button onClick={() => handleExport('pdf')} disabled={exporting} className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-white bg-rose-500 rounded hover:bg-rose-600 disabled:opacity-50">
                        <FileText className="w-3 h-3" /> PDF
                    </button>
                    <button onClick={() => handleExport('excel')} disabled={exporting} className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-white bg-emerald-600 rounded hover:bg-emerald-700 disabled:opacity-50">
                        <FileSpreadsheet className="w-3 h-3" /> Excel
                    </button>
                </div>
            )}
            <ReactApexChart
                options={chartOptions}
                series={series}
                type="heatmap"
                height={350}
            />

            {/* Predictive Only: Peak Info Analysis */}
            {isPredictive && metrics?.peak_info && (
                <div className="mt-4 p-4 bg-orange-50 border border-orange-100 rounded-lg flex items-center justify-between">
                    <div>
                        <h4 className="text-sm font-bold text-orange-800 uppercase">Momento de Mayor Congestión</h4>
                        <p className="text-lg font-bold text-slate-800">
                            {metrics.peak_info.day} a las {metrics.peak_info.hour}
                        </p>
                    </div>
                    <div className="text-right">
                        <p className="text-xs text-slate-500 uppercase">Intensidad</p>
                        <span className={`px-2 py-1 rounded text-xs font-bold ${metrics.peak_info.intensity.includes("Muy Alta") ? "bg-red-100 text-red-700" : "bg-orange-100 text-orange-700"
                            }`}>
                            {metrics.peak_info.intensity}
                        </span>
                        <p className="text-xs text-slate-500 mt-1">{metrics.peak_info.volume} vuelos promedio</p>
                    </div>
                </div>
            )}

            {/* Predictive Only: Executive Report */}
            {isPredictive && metrics?.executive_report && (
                <div className="mt-8 bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
                    <div className="bg-slate-800 p-4 border-b border-slate-700">
                        <h3 className="text-lg font-bold text-white flex items-center gap-2">
                            <span className="text-emerald-400">★</span>
                            {metrics.executive_report.title}
                        </h3>
                    </div>
                    <div className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-2 prose prose-slate max-w-none">
                            <div className="whitespace-pre-line text-slate-700 text-sm leading-relaxed">
                                {metrics.executive_report.narrative.split('**').map((part: string, i: number) =>
                                    i % 2 === 1 ? <strong key={i} className="text-slate-900 font-bold">{part}</strong> : part
                                )}
                            </div>
                        </div>
                        <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 h-fit">
                            <h4 className="text-xs font-bold text-slate-500 uppercase mb-4 tracking-wider">Puntos Clave</h4>
                            <div className="space-y-4">
                                {metrics.executive_report.key_highlights.map((h: any, idx: number) => (
                                    <div key={idx}>
                                        <p className="text-xs text-slate-500">{h.label}</p>
                                        <p className="text-lg font-bold text-indigo-700">{h.value}</p>
                                        <p className="text-xs text-slate-400 italic">{h.insight}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Methodology: Only show full detail if predictive, otherwise simplify */}
            <MethodologySection
                title={isPredictive
                    ? (filters.start_date ? "Análisis de Picos (Estacional)" : "Picos de Hora y Mapa de Calor")
                    : "Distribución Horaria (Conteo de Vuelos)"}
                algorithm={isPredictive ? "Agregación de Frecuencia con Promedio Ponderado" : "Conteo Agregado"}
                variables={['Día de la semana', 'Hora del día', 'Volumen de vuelos']}
                filters="Sector, Aeropuerto, Ruta, Nivel"
                dataVolume={description || "Datos históricos"}
                explanation={error || (metrics?.description || "Calculando...")}
                visible={isPredictive} // Optional: hide completely if not predictive using a new prop in MethodologySection if available, or just keeping it simple
            />

            {/* Show sampling data only if predictive or explicitly requested (default hidden for historical/distribution view per user request) */}
            {isPredictive && <DataTable data={history} title="Datos de Muestreo (Vuelos por Hora)" />}
        </div>
    );
};
