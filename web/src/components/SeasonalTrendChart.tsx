import React, { useEffect, useState } from 'react';
import ReactApexChart from 'react-apexcharts';
import { type PredictiveFilters, getSeasonalTrendForecast } from '../api';
import type { ApexOptions } from 'apexcharts';
import { MethodologySection } from './MethodologySection';

interface Props {
    /** 
     * Filtros de predicción opcionales. 
     * Requiere start_date y end_date para disparar el cálculo de Fourier.
     */
    filters?: PredictiveFilters;
}

/**
 * Componente de visualización de Tendencia Estacional de Largo Plazo.
 * 
 * Utiliza una descomposición de series temporales basada en:
 * 1. Tendencia Secular: Crecimiento o decrecimiento estructural del tráfico.
 * 2. Estacionalidad Anual: Ciclos recurrentes por meses/estaciones.
 * 3. Estacionalidad Semanal: Patrones por día de la semana.
 * 
 * Emplea un gráfico de tipo 'rangeArea' de ApexCharts para mostrar bandas de confianza.
 * 
 * @param props - Filtros aplicados para el análisis estacional.
 */
const SeasonalTrendChart: React.FC<Props> = ({ filters = {} }) => {
    // series: Contiene la línea histórica, la predicción y el área de confianza
    const [series, setSeries] = useState<any[]>([]);

    // metrics: Objeto con estadísticas de bondad de ajuste (R2, RMSE) e historia
    const [metrics, setMetrics] = useState<any>(null);

    // loading: Estado de espera mientras el backend procesa las transformadas de Fourier
    const [loading, setLoading] = useState(false);

    const [error, setError] = useState<string | null>(null);

    // Reacciona exclusivamente a cambios en el rango de fechas de análisis
    useEffect(() => {
        if (filters.start_date && filters.end_date) {
            fetchData();
        }
    }, [filters]);

    /**
     * Obtiene y procesa la proyección estacional.
     * Transforma las fechas ISO string a Timestamps (getTime()) para compatibilidad con ejes datetime.
     */
    const fetchData = async () => {
        try {
            setLoading(true);
            setError(null);

            // Fetch desde el endpoint /predictive/seasonal-trend
            const data = await getSeasonalTrendForecast(filters);

            if (data.error) {
                setError(data.error);
                setLoading(false);
                return;
            }

            // Metadatos explicativos sobre el funcionamiento del modelo híbrido
            const newMetrics = data.metrics || {};
            if (data.description) newMetrics.description = data.description;
            if (data.explanation_steps) newMetrics.explanation_steps = data.explanation_steps;
            if (data.executive_report) newMetrics.executive_report = data.executive_report;

            setMetrics(newMetrics);

            // Estructuración de series para ApexCharts
            const historyData = data.history.map((d: any) => ({
                x: new Date(d.date).getTime(),
                y: d.value
            }));

            const forecastData = data.forecast.map((d: any) => ({
                x: new Date(d.date).getTime(),
                y: d.value
            }));

            // La serie de área requiere un array [mínimo, máximo] para el valor Y
            const confidenceData = data.forecast.map((d: any) => ({
                x: new Date(d.date).getTime(),
                y: [d.lower, d.upper]
            }));

            setSeries([
                {
                    name: 'Histórico (Tendencia)',
                    type: 'line',
                    data: historyData
                },
                {
                    name: 'Predicción Estacional',
                    type: 'line',
                    data: forecastData
                },
                {
                    name: 'Intervalo de Confianza (95%)',
                    type: 'rangeArea',
                    data: confidenceData
                }
            ]);

            setLoading(false);
        } catch (err: any) {
            setError(`Fallo técnico en la descomposición: ${err.message}`);
            setLoading(false);
        }
    };

    // Configuración visual del gráfico ApexCharts
    const options: ApexOptions = {
        chart: {
            height: 400,
            type: 'line',
            toolbar: { show: true },
            zoom: { enabled: true },
            fontFamily: 'Inter, sans-serif'
        },
        stroke: {
            curve: 'smooth',
            width: [2, 3, 0], // Diferentes grosores para historia, predicción y área
            dashArray: [0, 5, 0] // Estilo punteado para la predicción
        },
        colors: ['#64748b', '#4f46e5', '#a5b4fc'],
        fill: {
            type: ['solid', 'solid', 'solid'],
            opacity: [1, 1, 0.4] // Opacidad reducida para la banda de confianza
        },
        dataLabels: { enabled: false },
        title: {
            text: 'Predicción de Demanda Estacional (Fourier + Tendencia)',
            align: 'left',
            style: { fontSize: '18px', fontWeight: 'bold', color: '#1e293b' }
        },
        xaxis: {
            type: 'datetime',
            tooltip: { enabled: true }
        },
        yaxis: {
            title: { text: 'Volumen de Vuelos' },
            min: 0
        },
        tooltip: {
            shared: true,
            intersect: false,
            x: { format: 'dd MMM yyyy' }
        },
        legend: {
            position: 'top',
            horizontalAlign: 'right'
        }
    };

    if (!filters.start_date || !filters.end_date) {
        return (
            <div className="p-8 text-center bg-slate-50 rounded-lg border border-slate-200">
                <p className="text-slate-500 font-medium">Seleccione un rango de fechas ("Fecha Desde" y "Fecha Hasta") para activar el análisis estacional.</p>
            </div>
        );
    }

    if (loading) return <div className="p-12 text-center text-indigo-600 font-medium animate-pulse">Calculando descomposición estacional (Fourier)...</div>;
    if (error) return <div className="p-4 text-center text-red-500 bg-red-50 rounded border border-red-200">{error}</div>;

    return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <ReactApexChart options={options} series={series} type="rangeArea" height={400} />

            {metrics?.explanation_steps && (
                <div className="mt-6 bg-slate-50 p-4 rounded-lg border border-slate-200 mb-6">
                    <h4 className="font-bold text-slate-700 mb-3 flex items-center gap-2">
                        <span className="bg-purple-600 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">i</span>
                        Descomposición del Modelo Estacional
                    </h4>
                    <div className="grid gap-3 md:grid-cols-3">
                        {metrics.explanation_steps.map((step: any, idx: number) => (
                            <div key={idx} className="bg-white p-3 rounded border border-slate-100 shadow-sm">
                                <p className="text-xs font-bold text-purple-600 uppercase mb-1">{step.step}</p>
                                <p className="text-sm text-slate-700">{step.detail}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {metrics?.executive_report && (
                <div className="mt-8 bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm mb-6">
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
                title="Tendencia Estacional (Largo Plazo)"
                algorithm="Descomposición de Series de Fourier (Estacionalidad + Tendencia)"
                variables={['Tendencia Secular (Años)', 'Ciclos Anuales', 'Ciclos Semanales']}
                filters={`Sector: ${filters.sector_id || 'Todos'}, Ruta: ${filters.route || 'Todas'}`}
                dataVolume={metrics?.years_history ? `${metrics.years_history} años de historia analizada` : "Conjunto de datos históricos completo"}
                explanation={error || (metrics?.description || "Calculando...")}
            />

            {/* Metrics Legend */}
            {metrics && (
                <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-slate-50 p-3 rounded border border-slate-200 text-center">
                        <p className="text-xs text-slate-500 uppercase font-bold">Fiabilidad (R²)</p>
                        <p className="text-xl font-bold text-indigo-600">{metrics.r2}</p>
                    </div>
                    <div className="bg-slate-50 p-3 rounded border border-slate-200 text-center">
                        <p className="text-xs text-slate-500 uppercase font-bold">Error (RMSE)</p>
                        <p className="text-xl font-bold text-slate-700">+/- {metrics.rmse}</p>
                    </div>
                    <div className="bg-slate-50 p-3 rounded border border-slate-200 text-center">
                        <p className="text-xs text-slate-500 uppercase font-bold">Historia</p>
                        <p className="text-xl font-bold text-slate-700">{metrics.years_history} Años</p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SeasonalTrendChart;
