import React, { useEffect, useState } from 'react';
import ReactApexChart from 'react-apexcharts';
import { getDailyDemandForecast, type PredictiveFilters } from '../api';
import type { ApexOptions } from 'apexcharts';
import { MethodologySection } from './MethodologySection';
import { DataTable } from './DataTable';

interface Props {
    filters?: PredictiveFilters;
}

const DailyDemandChart: React.FC<Props> = ({ filters = {} }) => {
    const [series, setSeries] = useState<any[]>([]);
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
            const data = await getDailyDemandForecast(30, filters);

            if (data.error) {
                setError(data.error);
                setLoading(false);
                return;
            }

            // Prepare metrics object
            const newMetrics = data.metrics || {};

            // Merge root-level properties into metrics
            if (data.description) newMetrics.description = data.description;
            if (data.explanation_steps) newMetrics.explanation_steps = data.explanation_steps;
            if (data.executive_report) newMetrics.executive_report = data.executive_report;
            if (data.accuracy_metrics) newMetrics.accuracy_metrics = data.accuracy_metrics;

            setMetrics(newMetrics);

            if (data.seasonal) {
                // SEASONAL MODE
                // Flatten and Format for Table
                const formattedHistory = data.history.flatMap((h: any) =>
                    h.data.map((d: any) => ({
                        Fecha: `${h.name}-${d.x}`, // e.g. 2023-12-01
                        Vuelos: d.y,
                        Temporada: h.name
                    }))
                );
                setHistory(formattedHistory);

                const seasonalSeries = data.history.map((h: any) => ({
                    name: h.name,
                    type: 'line',
                    data: h.data.map((d: any) => ({ x: d.x, y: d.y }))
                }));

                const forecastData = data.forecast.map((d: any) => ({
                    x: d.date.substring(5), // Extract MM-DD
                    y: d.value
                }));

                seasonalSeries.push({
                    name: 'Predicción (Estacional)',
                    type: 'line',
                    data: forecastData,
                    dashArray: 5
                });

                setSeries(seasonalSeries);
            } else {
                // STANDARD MODE
                setHistory(data.history || []);

                // Prepare Data
                const historyData = data.history.map((item: any) => ({
                    x: new Date(item.date).getTime(),
                    y: item.value
                }));

                const forecastData = data.forecast.map((item: any) => ({
                    x: new Date(item.date).getTime(),
                    y: item.value
                }));

                // Confidence Interval (Range Area)
                const ciData = data.forecast.map((item: any) => ({
                    x: new Date(item.date).getTime(),
                    y: [item.lower, item.upper]
                }));

                setSeries([
                    {
                        name: 'History',
                        type: 'line',
                        data: historyData
                    },
                    {
                        name: 'Forecast',
                        type: 'line',
                        data: forecastData
                    },
                    {
                        name: 'Confidence Interval',
                        type: 'rangeArea',
                        data: ciData
                    }
                ]);
            }
            setLoading(false);
        } catch (err: any) {
            console.error(err);
            setError(`Failed to load: ${err.message || 'Unknown error'}`);
            setLoading(false);
        }
    };

    const options: ApexOptions = {
        chart: {
            height: 350,
            type: 'line',
            toolbar: { show: true },
            zoom: { enabled: true },
            fontFamily: 'Inter, sans-serif'
        },
        stroke: {
            curve: 'smooth',
            width: 2,
            dashArray: filters.start_date ? undefined : [0, 5, 0] // Dynamic dash array
        },
        // fill: { // removed fixed fill to allow auto colors for many lines
        //     type: ['solid', 'solid', 'solid'],
        //     opacity: [1, 1, 0.3]
        // },
        // colors: ['#008FFB', '#00E396', '#00E396'], // let apex choose colors for seasonal
        title: {
            text: filters.start_date ? 'Comparación Estacional (Histórico vs Predicción)' : 'Predicción de Demanda Diaria (Próximos 30 Días)',
            align: 'left',
            style: { fontSize: '16px', fontWeight: 'bold' }
        },
        xaxis: {
            type: filters.start_date ? 'category' : 'datetime', // Use category for MM-DD
            tooltip: { enabled: true },
            labels: filters.start_date ? undefined : { datetimeFormatter: { year: 'yyyy', month: 'MMM \'yy', day: 'dd MMM', hour: 'HH:mm' } }
        },
        yaxis: {
            title: { text: 'Cantidad de Vuelos' },
            min: 0
        },
        tooltip: {
            shared: true,
            intersect: false,
            // x: { format: 'dd MMM yyyy' }, // format depends on mode
            y: {
                formatter: (val) => val ? val.toFixed(0) : ''
            }
        },
        legend: {
            position: 'top',
        }
    };

    if (loading) return <div className="p-4 text-center">Cargando Modelo de Predicción...</div>;
    if (error) return <div className="p-4 text-center text-red-500">{error}</div>;

    // Translation for Series Names
    const translatedSeries = series.map(s => ({
        ...s,
        name: s.name === 'History' ? 'Histórico' :
            s.name === 'Forecast' ? 'Predicción' :
                s.name === 'Confidence Interval' ? 'Intervalo de Confianza' : s.name
    }));

    return (
        <div className="bg-white p-4 rounded shadow mb-4">
            <ReactApexChart options={options} series={translatedSeries} type="line" height={350} />

            {metrics?.explanation_steps && (
                <div className="mt-6 bg-slate-50 p-4 rounded-lg border border-slate-200">
                    <h4 className="font-bold text-slate-700 mb-3 flex items-center gap-2">
                        <span className="bg-indigo-600 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">i</span>
                        Cómo se calculó esta predicción
                    </h4>
                    <div className="grid gap-3 md:grid-cols-2">
                        {metrics.explanation_steps.map((step: any, idx: number) => (
                            <div key={idx} className="bg-white p-3 rounded border border-slate-100 shadow-sm">
                                <p className="text-xs font-bold text-indigo-600 uppercase mb-1">{step.step}</p>
                                <p className="text-sm text-slate-700">{step.detail}</p>
                            </div>
                        ))}
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
                title={filters.start_date ? "Análisis de Demanda Estacional" : "Predicción de Demanda Diaria"}
                algorithm={filters.start_date ? "Descomposición de Tendencia Estacional (Loess-based proxy)" : "Random Forest Regressor (Ensamble de Árboles de Decisión)"}
                variables={['Fecha', 'Día de la semana', 'Mes', 'Tendencia Anual', 'Estacionalidad Semanal']}
                filters={`Sector: ${filters.sector_id || 'Todos'}, Aeropuerto: ${filters.airport || 'Todos'}, Nivel: ${filters.min_level || 0}-${filters.max_level || 'Max'}`}
                dataVolume={filters.start_date ? "Muestra histórica completa del periodo seleccionado en años anteriores" : "Entrenamiento con ventana móvil de historial reciente"}
                explanation={error || (metrics?.description || "Calculando explicación...")}
            />

            <DataTable data={history} title="Datos Históricos Utilizados (Muestreo)" />
        </div>
    );
};

export default DailyDemandChart;
