import React, { useEffect, useState } from 'react';
import ReactApexChart from 'react-apexcharts';
import { getAirlineGrowthForecast, type PredictiveFilters } from '../api';
import type { ApexOptions } from 'apexcharts';
import { MethodologySection } from './MethodologySection';
import { DataTable } from './DataTable';

interface Props {
    filters?: PredictiveFilters;
}

const AirlineGrowthChart: React.FC<Props> = ({ filters = {} }) => {
    const [series, setSeries] = useState<any[]>([]);
    const [options, setOptions] = useState<ApexOptions>({});
    const [history, setHistory] = useState<any[]>([]);
    const [metrics, setMetrics] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchData();
    }, [filters]);

    const fetchData = async () => {
        try {
            setLoading(true);
            const data = await getAirlineGrowthForecast(12, filters);

            // Consolidate metrics
            const newMetrics = data.metrics || {};
            if (data.executive_report) newMetrics.executive_report = data.executive_report;
            if (data.description) newMetrics.description = data.description;

            setMetrics(newMetrics);

            // Handle new response structure (wrapper object)
            let airlinesData: any[] = [];
            let desc = "Datos mensuales del último año";
            let isSeas = false;

            if (data && Array.isArray(data.results)) {
                airlinesData = data.results;
                desc = data.description || desc;
                isSeas = data.seasonal || false;
            } else if (Array.isArray(data)) {
                // Fallback for old API if any
                airlinesData = data;
            } else {
                setError('Invalid data format.');
                setLoading(false);
                return;
            }

            if (airlinesData.length === 0) {
                setError('No data found for the selected criteria.');
                setLoading(false);
                return;
            }

            // Flatten history from all airlines for the table
            const allHistory = airlinesData.flatMap((item: any) =>
                (item.history || []).map((h: any) => ({
                    Aerolínea: item.airline,
                    Periodo: h.label, // Use generic label (Month or Year)
                    Vuelos: h.value
                }))
            );
            setHistory(allHistory);

            // Prepare Data for Bar Chart
            const categories = airlinesData.map((item: any) => item.airline);
            const growthRates = airlinesData.map((item: any) => item.growth_rate);

            setSeries([{
                name: isSeas ? 'Tasa de Crecimiento Anual (Vuelos/Año)' : 'Tasa de Crecimiento Mensual (Vuelos/Mes)',
                data: growthRates
            }]);

            setOptions({
                chart: {
                    type: 'bar',
                    height: 350,
                    fontFamily: 'Inter, sans-serif'
                },
                plotOptions: {
                    bar: {
                        colors: {
                            ranges: [{
                                from: -1000,
                                to: 0,
                                color: '#FF4560'
                            }, {
                                from: 0,
                                to: 1000,
                                color: '#00E396'
                            }]
                        },
                        columnWidth: '50%',
                    }
                },
                dataLabels: {
                    enabled: false,
                },
                yaxis: {
                    title: {
                        text: isSeas ? 'Crecimiento (Vuelos/Año)' : 'Crecimiento (Vuelos/Mes)',
                    },
                },
                xaxis: {
                    categories: categories,
                    labels: {
                        rotate: -45
                    }
                },
                title: {
                    text: isSeas ? 'Tendencia Crecimiento Estacional (Interanual)' : 'Tendencias de Crecimiento de Aerolíneas (Último Año)',
                    align: 'left',
                    style: { fontSize: '16px', fontWeight: 'bold' }
                },
                tooltip: {
                    y: {
                        formatter: (val) => val.toFixed(2) + (isSeas ? ' vuelos/año' : ' vuelos/mes')
                    }
                }
            });

            setLoading(false);
        } catch (err: any) {
            console.error(err);
            setError(`Failed to load: ${err.message || 'Unknown error'}`);
            setLoading(false);
        }
    };

    if (loading) return <div className="p-4 text-center">Analizando Crecimiento...</div>;
    if (error) return <div className="p-4 text-center text-red-500">{error}</div>;

    return (
        <div className="bg-white p-4 rounded shadow mb-4">
            <ReactApexChart options={options} series={series} type="bar" height={350} />

            {metrics && (
                <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="bg-emerald-50 p-4 rounded-lg border border-emerald-100 text-center">
                        <p className="text-xs text-emerald-800 font-bold uppercase">Aerolínea Líder</p>
                        <p className="text-lg font-bold text-slate-800 truncate">{metrics.top_airline}</p>
                        <p className="text-xs text-emerald-600">+{metrics.top_growth_rate} vuelos/mes</p>
                    </div>
                    <div className="bg-blue-50 p-4 rounded-lg border border-blue-100 text-center">
                        <p className="text-xs text-blue-800 font-bold uppercase">Mercado</p>
                        <p className="text-lg font-bold text-slate-800">{metrics.growing_count} aerolíneas en crecimiento</p>
                        <p className="text-xs text-blue-600">vs {metrics.declining_count} en declive</p>
                    </div>
                    <div className="bg-slate-50 p-4 rounded-lg border border-slate-100 text-center">
                        <p className="text-xs text-slate-500 font-bold uppercase">Muestra</p>
                        <p className="text-lg font-bold text-slate-800">{metrics.total_data_points}</p>
                        <p className="text-xs text-slate-500">Puntos de datos analizados</p>
                    </div>
                </div>
            )}

            {metrics?.executive_report && (
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

            <MethodologySection
                title={filters.start_date ? "Análisis de Crecimiento Estacional" : "Crecimiento de Aerolíneas"}
                algorithm="Regresión Lineal Simple (Tendencia)"
                variables={['Tiempo (Año/Mes)', 'Volumen de Vuelos', 'Tasa de Crecimiento (Pendiente)']}
                filters={`Sector: ${filters.sector_id || 'Todos'}, Ruta: ${filters.route || 'Todas'}`}
                dataVolume={filters.start_date ? "Muestra histórica anual del periodo seleccionado" : "Historial mensual completo del último año"}
                explanation={error || (metrics?.description || "Calculando...")}
            />

            <DataTable data={history} title="Datos Históricos por Aerolínea (Último Año)" />
        </div>
    );
};

export default AirlineGrowthChart;
