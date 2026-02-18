import React, { useEffect, useState } from 'react';
import ReactApexChart from 'react-apexcharts';
import { getDailyDemandForecast, type PredictiveFilters } from '../api';
import type { ApexOptions } from 'apexcharts';
import { MethodologySection } from './MethodologySection';
import { DataTable } from './DataTable';

interface Props {
    /** Filtros de predicción aplicados desde el dashboard (Sector, Ruta, Aeropuerto) */
    filters?: PredictiveFilters;
}

/**
 * Visualización de Demanda de Vuelo Diaria (Serie Temporal).
 * 
 * Este componente muestra la proyección del volumen de vuelos a 30 días vista.
 * Soporta dos comportamientos distintos basados en los filtros de fecha:
 * 1. Flujo Continuo: Serie temporal real + predicción IA + banda de confianza.
 * 2. Comparativa Estacional: Superposición de líneas por temporada/año.
 * 
 * @param props - Propiedades con los filtros de búsqueda.
 */
const DailyDemandChart: React.FC<Props> = ({ filters = {} }) => {
    // series: Almacena las líneas de datos para el gráfico ApexCharts
    const [series, setSeries] = useState<any[]>([]);

    // history: Datos históricos normalizados para la tabla de visualización
    const [history, setHistory] = useState<any[]>([]);

    // metrics: Metadatos del modelo (Accuracy, RMSFE, R2) y reportes narrativos
    const [metrics, setMetrics] = useState<any>(null);

    // loading: Bloqueo de UI mientras se ejecuta la inferencia en el backend
    const [loading, setLoading] = useState(true);

    const [error, setError] = useState<string | null>(null);

    // Dispara la consulta cada vez que el contexto operacional es modificado
    useEffect(() => {
        fetchData();
    }, [filters]);

    /**
     * Consume el servicio de predicción de demanda diaria.
     * Mapea el objeto JSON complejo a estructuras de datos para series y tablas.
     */
    const fetchData = async () => {
        try {
            setLoading(true);
            // Llama a /predictive/daily-demand con un horizonte de 30 muestras
            const data = await getDailyDemandForecast(30, filters);

            if (data.error) {
                setError(data.error);
                setLoading(false);
                return;
            }

            const newMetrics = data.metrics || {};
            if (data.description) newMetrics.description = data.description;
            if (data.explanation_steps) newMetrics.explanation_steps = data.explanation_steps;
            if (data.executive_report) newMetrics.executive_report = data.executive_report;
            if (data.accuracy_metrics) newMetrics.accuracy_metrics = data.accuracy_metrics;

            setMetrics(newMetrics);

            // Bifurcación de lógica según el tipo de respuesta (Estacional o Continua)
            if (data.seasonal) {
                // LOGICA ESTACIONAL: Alinea datos por MM-DD para comparación interanual
                const formattedHistory = data.history.flatMap((h: any) =>
                    h.data.map((d: any) => ({
                        Fecha: `${h.name}-${d.x}`,
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
                    x: d.date.substring(5),
                    y: d.value
                }));

                seasonalSeries.push({
                    name: 'Predicción Estimada',
                    type: 'line',
                    data: forecastData,
                    dashArray: 5
                });

                setSeries(seasonalSeries);
            } else {
                // LOGICA CONTINUA: Utiliza timestamps para un eje temporal real (X-axis: datetime)
                setHistory(data.history || []);

                const historyData = data.history.map((item: any) => ({
                    x: new Date(item.date).getTime(),
                    y: item.value
                }));

                const forecastData = data.forecast.map((item: any) => ({
                    x: new Date(item.date).getTime(),
                    y: item.value
                }));

                const ciData = data.forecast.map((item: any) => ({
                    x: new Date(item.date).getTime(),
                    y: [item.lower, item.upper]
                }));

                setSeries([
                    { name: 'History', type: 'line', data: historyData },
                    { name: 'Forecast', type: 'line', data: forecastData },
                    { name: 'Confidence Interval', type: 'rangeArea', data: ciData }
                ]);
            }
            setLoading(false);
        } catch (err: any) {
            setError(`Error técnico en el motor de demanda: ${err.message}`);
            setLoading(false);
        }
    };

    /**
     * Configuración del gráfico ApexCharts.
     */
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
            // Estilo de línea dinámico según el modo de filtros
            dashArray: filters.start_date ? undefined : [0, 5, 0]
        },
        title: {
            text: filters.start_date ? 'Comparación Estacional (Histórico vs Predicción)' : 'Predicción de Demanda Diaria (Próximos 30 Días)',
            align: 'left',
            style: { fontSize: '16px', fontWeight: 'bold' }
        },
        xaxis: {
            type: filters.start_date ? 'category' : 'datetime', // Categorías para MM-DD, Datetime para flujo continuo
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

    /**
     * Traducción dinámica de nombres de series para la leyenda.
     */
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
