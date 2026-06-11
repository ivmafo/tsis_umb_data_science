import React, { useEffect, useState } from 'react';
import ReactApexChart from 'react-apexcharts';
import { getSectorSaturationForecast } from '../api';
import type { ApexOptions } from 'apexcharts';
import { MethodologySection } from './MethodologySection';
import { DataTable } from './DataTable';

import { type PredictiveFilters } from '../api';

interface Props {
    /**
     * Filtros multidimensionales provenientes del panel lateral.
     * Incluye sector_id, fechas, niveles de vuelo y rutas.
     */
    filters: PredictiveFilters;
}

/**
 * Componente de visualización avanzada de Saturación de Sector ATC.
 * 
 * Este componente integra el modelo matemático de la Circular 006 (Capacidad)
 * con el motor de IA (Demanda Proyectada) para estimar el riesgo operativo.
 * 
 * Funcionalidades clave:
 * - Gráfico Line-Column de ApexCharts con ejes Y duales.
 * - Anotaciones visuales para límites de Alerta (80%) y Crítico (100%).
 * - Desglose técnico de la fórmula CH_Adjusted = CH_Theoretical * R.
 * - Reporte ejecutivo narrativo generado por el backend.
 * 
 * @param props - Propiedades del componente con filtros de predicción.
 */
const SectorSaturationChart: React.FC<Props> = ({ filters }) => {
    // series: Almacena los sets de datos para volumen (barras) e índice (línea)
    const [series, setSeries] = useState<any[]>([]);

    // options: Configuración estética y técnica de ApexCharts
    const [options, setOptions] = useState<ApexOptions>({});

    // history: Registros históricos para alimentar la tabla de datos inferior
    const [history, setHistory] = useState<any[]>([]);

    // loading: Control de estado de carga asíncrona
    const [loading, setLoading] = useState(true);

    // error: Mensajes de fallo en la comunicación con la API
    const [error, setError] = useState<string | null>(null);

    // metrics: Objeto detallado con resultados de capacidad (TFC, T_Transfer, CH)
    const [metrics, setMetrics] = useState<any>(null);

    // Re-ejecuta la consulta cada vez que el usuario cambia un filtro en la UI
    useEffect(() => {
        if (filters.sector_id) {
            fetchData();
        }
    }, [filters]);

    /**
     * Coordina la obtención de datos desde el controlador predictivo.
     * Realiza el mapeo y transformación del JSON de respuesta a estructuras de visualización.
     */
    const fetchData = async () => {
        try {
            setLoading(true);
            // Consulta el endpoint /predictive/sector-saturation/{id}
            const data = await getSectorSaturationForecast(filters, 30);

            if (data.error) {
                setError(data.error);
                setLoading(false);
                return;
            }

            // Mapeo exhaustivo de métricas de capacidad técnica
            const newMetrics = data.metrics || data.capacity_metrics || {};
            if (data.description) newMetrics.description = data.description;
            if (data.calculation_steps) newMetrics.calculation_steps = data.calculation_steps;
            if (data.executive_report) newMetrics.executive_report = data.executive_report;

            setMetrics(newMetrics);

            // Preparación del historial para la DataTable
            let historyData = data.history || [];
            if (data.seasonal && Array.isArray(historyData) && historyData.length > 0 && historyData[0].name) {
                historyData = historyData.flatMap((h: any) => h.data.map((d: any) => ({
                    Fecha: `${h.name}-${d.x}`,
                    Vuelos: d.y
                })));
            } else {
                historyData = historyData.map((d: any) => ({
                    Fecha: d.date || d.x,
                    Vuelos: d.value || d.y
                }));
            }
            setHistory(historyData);

            // Segmentación de ejes para gráfico dual
            const dates = data.forecast.map((item: any) => item.date);
            const dailyFlights = data.forecast.map((item: any) => item.predicted_daily_flights);
            const saturation = data.forecast.map((item: any) => item.saturation_index);

            setSeries([
                {
                    name: 'Vuelos Diarios (Predicción)',
                    type: 'column',
                    data: dailyFlights
                },
                {
                    name: 'Índice Saturación (%)',
                    type: 'line',
                    data: saturation
                }
            ]);

            setOptions({
                chart: {
                    height: 350,
                    type: 'line',
                    stacked: false,
                    fontFamily: 'Inter, sans-serif',
                    toolbar: { show: true }
                },
                dataLabels: { enabled: false },
                stroke: { width: [1, 4], curve: 'smooth' },
                title: {
                    text: data.seasonal ? `Análisis Estacional: ${data.sector_name}` : `Proyección de Riesgo: ${data.sector_name}`,
                    align: 'left',
                    style: { fontSize: '18px', color: '#1e293b' }
                },
                xaxis: {
                    categories: dates,
                    labels: { style: { colors: '#64748b' } }
                },
                yaxis: [
                    {
                        title: { text: "Flujo de Vuelos", style: { color: '#008FFB' } },
                        labels: { style: { colors: '#008FFB' } }
                    },
                    {
                        opposite: true,
                        title: { text: "Saturación (%)", style: { color: '#FEB019' } },
                        labels: { style: { colors: '#FEB019' } },
                        min: 0,
                    }
                ],
                tooltip: { shared: true, intersect: false },
                legend: { position: 'top', horizontalAlign: 'right' },
                annotations: {
                    yaxis: [
                        {
                            y: 80, yAxisIndex: 1,
                            borderColor: '#FEB019',
                            strokeDashArray: 5,
                            label: { text: 'Umbral Alerta' }
                        },
                        {
                            y: (newMetrics.stochastic_range && newMetrics.CH_Adjusted) ? (newMetrics.stochastic_range.lower / newMetrics.CH_Adjusted) * 100 : 100,
                            y2: (newMetrics.stochastic_range && newMetrics.CH_Adjusted) ? (newMetrics.stochastic_range.upper / newMetrics.CH_Adjusted) * 100 : 100,
                            yAxisIndex: 1,
                            fillColor: '#ef4444',
                            opacity: 0.15,
                            label: { text: 'Banda Estocástica (95%)', style: { background: '#ef4444', color: '#fff', fontSize: '10px' } }
                        },
                        {
                            y: 100, yAxisIndex: 1,
                            borderColor: '#ef4444',
                            strokeDashArray: 0,
                            label: { text: 'Saturación Nominal', style: { background: '#ef4444', color: '#fff' } }
                        }
                    ]
                }
            });

            setLoading(false);
        } catch (err: any) {
            setError(`Fallo técnico en el cálculo: ${err.message}`);
            setLoading(false);
        }
    };

    if (loading) return <div className="p-4 text-center">Calculando Saturación...</div>;
    if (error) return <div className="p-4 text-center text-red-500">{error}</div>;

    return (
        <div className="bg-white p-4 rounded shadow mb-4">
            <ReactApexChart options={options} series={series} type="line" height={350} />

            {/* Panel de métricas operacionales del sector */}
            {metrics && (
                <div className="mt-4 grid grid-cols-4 gap-4 text-center border-t pt-2 bg-gray-50 rounded p-2">
                    <div>
                        <span className="block text-gray-500 text-xs">TFC Dinámico (RAC 14)</span>
                        <span className="font-bold">{metrics.dynamic_tfc} s</span>
                    </div>
                    <div>
                        <span className="block text-gray-500 text-xs">Rango Estocástico (95%)</span>
                        <span className="font-bold text-slate-600">{metrics.stochastic_range?.lower} - {metrics.stochastic_range?.upper} v/hr</span>
                    </div>
                    <div>
                        <span className="block text-gray-500 text-xs">Capacidad Asegurada</span>
                        <span className="font-bold text-blue-600">{metrics.CH_Adjusted} vuelos/hr</span>
                    </div>
                    <div>
                        <span className="block text-gray-500 text-xs">Pico de Saturación</span>
                        <span className={`font-bold ${metrics.Max_Saturation > 100 ? 'text-red-500' : 'text-amber-500'}`}>{metrics.Max_Saturation ?? 0}%</span>
                    </div>
                </div>
            )}
            ...

            {metrics?.calculation_steps && (
                <div className="mt-6 bg-slate-50 p-4 rounded-lg border border-slate-200">
                    <h4 className="font-bold text-slate-700 mb-3 flex items-center gap-2">
                        <span className="bg-blue-600 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">i</span>
                        Desglose del Cálculo de Capacidad
                    </h4>
                    <div className="grid gap-3 md:grid-cols-2">
                        {metrics.calculation_steps.map((step: any, idx: number) => (
                            <div key={idx} className="bg-white p-3 rounded border border-slate-100 shadow-sm">
                                <p className="text-xs font-bold text-blue-600 uppercase mb-1">{step.step}</p>
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
                title={filters.start_date ? "Análisis de Saturación Estacional" : "Saturación de Sector"}
                algorithm="Modelo Híbrido: Predicción AI (Demand) + Agentes Estocásticos RAC 14 (Capacity)"
                variables={['Tiempo de Ocupación Dinámico (TFC)', 'Factor Ashford Probabilístico', 'Bandas de Incertidumbre (Estocástico)']}
                filters="Sector Específico"
                dataVolume={filters.start_date ? "Comparación histórica del periodo seleccionado" : "Datos de vuelos del sector en los últimos 90 días combinados con simulación montecarlo"}
                explanation={error || (metrics?.description || "Calculando...")}
            />

            <DataTable data={history} title="Historial de Demanda del Sector (Muestreo)" />
        </div>
    );
};

export default SectorSaturationChart;
