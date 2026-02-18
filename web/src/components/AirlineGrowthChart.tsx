import React, { useEffect, useState } from 'react';
import ReactApexChart from 'react-apexcharts';
import { getAirlineGrowthForecast, type PredictiveFilters } from '../api';
import type { ApexOptions } from 'apexcharts';
import { MethodologySection } from './MethodologySection';
import { DataTable } from './DataTable';

interface Props {
    /** Filtros multidimensionales (Sector, Aeropuerto, Fechas) */
    filters?: PredictiveFilters;
}

/**
 * Visualización Proyectiva del Crecimiento de Aerolíneas.
 * 
 * Este componente analiza la inercia del mercado aéreo mediante regresión lineal.
 * Permite identificar qué operadores están liderando la expansión del tráfico
 * en un sector o ruta específica.
 * 
 * @param props - Filtros operativos para el análisis de crecimiento.
 */
const AirlineGrowthChart: React.FC<Props> = ({ filters = {} }) => {
    // series: Almacena la tasa de crecimiento (vuelos/tiempo) para cada aerolínea
    const [series, setSeries] = useState<any[]>([]);

    // options: Configuración de ApexCharts con colores condicionales (Escala Semafórica)
    const [options, setOptions] = useState<ApexOptions>({});

    // history: Registros crudos unificados para alimentar la tabla de datos inferior
    const [history, setHistory] = useState<any[]>([]);

    // metrics: KIs de negocio (Top growth, growing/declining counts)
    const [metrics, setMetrics] = useState<any>(null);

    // loading: Control de carga mientras el motor de IA calcula las pendientes
    const [loading, setLoading] = useState(true);

    const [error, setError] = useState<string | null>(null);

    // Actualiza el análisis cuando el usuario cambia el contexto operativo
    useEffect(() => {
        fetchData();
    }, [filters]);

    /**
     * Consume el endpoint predictivo de crecimiento de aerolíneas.
     * Proyecta la tendencia a 12 meses vista basándose en la ventana de datos actual.
     */
    const fetchData = async () => {
        try {
            setLoading(true);
            // Llama a /predictive/airline-growth con horizonte de 12 meses
            const data = await getAirlineGrowthForecast(12, filters);

            const newMetrics = data.metrics || {};
            if (data.executive_report) newMetrics.executive_report = data.executive_report;
            if (data.description) newMetrics.description = data.description;

            setMetrics(newMetrics);

            // Validación de integridad de la respuesta
            let airlinesData: any[] = [];
            let desc = "Datos mensuales del último año";
            let isSeas = false;

            if (data && Array.isArray(data.results)) {
                airlinesData = data.results;
                desc = data.description || desc;
                isSeas = data.seasonal || false;
            } else if (Array.isArray(data)) {
                airlinesData = data;
            } else {
                setError('Error Interno: El formato de datos de crecimiento es incompatible.');
                setLoading(false);
                return;
            }

            if (airlinesData.length === 0) {
                setError('No se detectaron tendencias para los filtros actuales.');
                setLoading(false);
                return;
            }

            // Normalización del historial multibanda para la tabla
            const allHistory = airlinesData.flatMap((item: any) =>
                (item.history || []).map((h: any) => ({
                    Aerolínea: item.airline,
                    Periodo: h.label,
                    Vuelos: h.value
                }))
            );
            setHistory(allHistory);

            const categories = airlinesData.map((item: any) => item.airline);
            const growthRates = airlinesData.map((item: any) => item.growth_rate);

            setSeries([{
                name: isSeas ? 'Pendiente Anual (Vuelos/Año)' : 'Pendiente Mensual (Vuelos/Mes)',
                data: growthRates
            }]);

            // Configuración estética avanzada para reporte técnico
            setOptions({
                chart: {
                    type: 'bar',
                    height: 350,
                    fontFamily: 'Inter, sans-serif',
                    toolbar: { show: true }
                },
                plotOptions: {
                    bar: {
                        borderRadius: 4,
                        colors: {
                            ranges: [{
                                from: -1000, to: 0,
                                color: '#fca5a5' // Rojo pastel para decrecimiento
                            }, {
                                from: 0.1, to: 1000,
                                color: '#86efac' // Verde pastel para crecimiento
                            }]
                        },
                        columnWidth: '55%',
                    }
                },
                dataLabels: { enabled: false },
                yaxis: {
                    title: { text: isSeas ? 'Delta Vuelos/Año' : 'Delta Vuelos/Mes', style: { color: '#64748b' } },
                    labels: { formatter: (v) => v.toFixed(1) }
                },
                xaxis: {
                    categories: categories,
                    labels: {
                        rotate: -45,
                        style: { colors: '#64748b' }
                    }
                },
                title: {
                    text: isSeas ? `Dinámica Interanual por Operador` : `Dinámica Mensual por Operador`,
                    align: 'left',
                    style: { fontSize: '18px', color: '#1e293b' }
                },
                tooltip: {
                    theme: 'light',
                    y: {
                        formatter: (val) => val.toFixed(2) + (isSeas ? ' vuelos/idp' : ' vuelos/mes')
                    }
                }
            });

            setLoading(false);
        } catch (err: any) {
            setError(`Fallo en el motor de tendencias: ${err.message}`);
            setLoading(false);
        }
    };

    if (loading) return <div className="p-4 text-center">Analizando Tendencias de Crecimiento...</div>;
    if (error) return <div className="p-4 text-center text-red-500">{error}</div>;

    return (
        <div className="bg-white p-4 rounded shadow mb-4">
            <ReactApexChart options={options} series={series} type="bar" height={350} />

            {/* Tarjetas informativas con hallazgos clave del mercado */}
            {metrics && (
                <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="bg-emerald-50 p-4 rounded-lg border border-emerald-100 text-center">
                        <p className="text-xs text-emerald-800 font-bold uppercase">Aerolínea Líder</p>
                        <p className="text-lg font-bold text-slate-800 truncate">{metrics.top_airline}</p>
                        <p className="text-xs text-emerald-600">+{metrics.top_growth_rate} vuelos/mes</p>
                    </div>
                    <div className="bg-blue-50 p-4 rounded-lg border border-blue-100 text-center">
                        <p className="text-xs text-blue-800 font-bold uppercase">Dinámica de Mercado</p>
                        <p className="text-lg font-bold text-slate-800">{metrics.growing_count} aerolíneas creciendo</p>
                        <p className="text-xs text-blue-600">vs {metrics.declining_count} en declive</p>
                    </div>
                    <div className="bg-slate-50 p-4 rounded-lg border border-slate-100 text-center">
                        <p className="text-xs text-slate-500 font-bold uppercase">Historial Analizado</p>
                        <p className="text-lg font-bold text-slate-800">{metrics.total_data_points}</p>
                        <p className="text-xs text-slate-500">Muestras de volumen registradas</p>
                    </div>
                </div>
            )}
            ...

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
