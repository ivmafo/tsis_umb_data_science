import React, { useEffect, useState } from 'react';
import ReactApexChart from 'react-apexcharts';
import { getSectorSaturationForecast } from '../api';
import type { ApexOptions } from 'apexcharts';
import { MethodologySection } from './MethodologySection';
import { DataTable } from './DataTable';

import { type PredictiveFilters } from '../api';

interface Props {
    filters: PredictiveFilters;
}

const SectorSaturationChart: React.FC<Props> = ({ filters }) => {
    const [series, setSeries] = useState<any[]>([]);
    const [options, setOptions] = useState<ApexOptions>({});
    const [history, setHistory] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [metrics, setMetrics] = useState<any>(null);

    useEffect(() => {
        if (filters.sector_id) {
            fetchData();
        }
    }, [filters]);

    const fetchData = async () => {
        try {
            setLoading(true);
            const data = await getSectorSaturationForecast(filters, 30);

            if (data.error) {
                setError(data.error);
                setLoading(false);
                return;
            }

            // Consolidate metrics
            const newMetrics = data.metrics || data.capacity_metrics || {};
            if (data.description) newMetrics.description = data.description;
            if (data.calculation_steps) newMetrics.calculation_steps = data.calculation_steps;
            if (data.executive_report) newMetrics.executive_report = data.executive_report;

            setMetrics(newMetrics);
            let historyData = data.history || [];
            // If seasonal, history is array of series. Flatten for table?
            if (data.seasonal && Array.isArray(historyData) && historyData.length > 0 && historyData[0].name) {
                historyData = historyData.flatMap((h: any) => h.data.map((d: any) => ({
                    Fecha: `${h.name}-${d.x}`, // Approx date for table
                    Vuelos: d.y
                })));
            } else {
                historyData = historyData.map((d: any) => ({
                    Fecha: d.date || d.x,
                    Vuelos: d.value || d.y
                }));
            }
            setHistory(historyData);

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
                    fontFamily: 'Inter, sans-serif'
                },
                dataLabels: {
                    enabled: false
                },
                stroke: {
                    width: [1, 4]
                },
                title: {
                    text: data.seasonal ? `Saturación Estacional: ${data.sector_name}` : `Predicción de Saturación: ${data.sector_name}`,
                    align: 'left',
                    style: { fontSize: '16px', fontWeight: 'bold' }
                },
                xaxis: {
                    categories: dates
                },
                yaxis: [
                    {
                        axisTicks: { show: true },
                        axisBorder: { show: true, color: '#008FFB' },
                        labels: { style: { colors: '#008FFB' } },
                        title: {
                            text: "Vuelos Diarios",
                            style: { color: '#008FFB' }
                        },
                        tooltip: { enabled: true }
                    },
                    {
                        seriesName: 'Índice Saturación (%)',
                        opposite: true,
                        axisTicks: { show: true },
                        axisBorder: { show: true, color: '#FEB019' },
                        labels: { style: { colors: '#FEB019' } },
                        title: {
                            text: "Saturación (%)",
                            style: { color: '#FEB019' }
                        },
                        min: 0,
                        max: 120,
                    }
                ],
                tooltip: {
                    fixed: {
                        enabled: true,
                        position: 'topLeft',
                        offsetY: 30,
                        offsetX: 60
                    },
                },
                legend: {
                    horizontalAlign: 'left',
                    offsetX: 40
                },
                annotations: {
                    yaxis: [
                        {
                            y: 80,
                            yAxisIndex: 1,
                            borderColor: '#FEB019',
                            label: {
                                borderColor: '#FEB019',
                                style: { color: '#fff', background: '#FEB019' },
                                text: 'Alerta (80%)',
                            }
                        },
                        {
                            y: 100,
                            yAxisIndex: 1,
                            borderColor: '#FF0000',
                            label: {
                                borderColor: '#FF0000',
                                style: { color: '#fff', background: '#FF0000' },
                                text: 'Crítico (100%)',
                            }
                        }
                    ]
                }
            });

            setLoading(false);
        } catch (err: any) {
            console.error(err);
            setError(`Failed to load: ${err.message || 'Unknown error'}`);
            setLoading(false);
        }
    };

    if (loading) return <div className="p-4 text-center">Calculando Saturación...</div>;
    if (error) return <div className="p-4 text-center text-red-500">{error}</div>;

    return (
        <div className="bg-white p-4 rounded shadow mb-4">
            <ReactApexChart options={options} series={series} type="line" height={350} />

            {metrics && (
                <div className="mt-4 grid grid-cols-4 gap-4 text-center border-t pt-2 bg-gray-50 rounded p-2">
                    <div>
                        <span className="block text-gray-500 text-xs">Tiempo Prom. (TFC)</span>
                        <span className="font-bold">{metrics.TFC} s</span>
                    </div>
                    <div>
                        <span className="block text-gray-500 text-xs">Capacidad Teórica (CH)</span>
                        <span className="font-bold">{metrics.CH_Theoretical} vuelos/hr</span>
                    </div>
                    <div>
                        <span className="block text-gray-500 text-xs">Factor (R)</span>
                        <span className="font-bold">{metrics.R_Factor}</span>
                    </div>
                    <div>
                        <span className="block text-gray-500 text-xs">Capacidad Ajustada</span>
                        <span className="font-bold text-blue-600">{metrics.CH_Adjusted} vuelos/hr</span>
                    </div>
                </div>
            )}

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
                algorithm="Modelo Híbrido: Predicción RF + Capacidad (Circular 006)"
                variables={['Tiempo de Ocupación (TFC)', 'Vuelos Previstos', 'Factor Buffer (1.3)']}
                filters="Sector Específico"
                dataVolume={filters.start_date ? "Comparación histórica del periodo seleccionado" : "Datos de vuelos del sector en los últimos 90 días"}
                explanation={error || (metrics?.description || "Calculando...")}
            />

            <DataTable data={history} title="Historial de Demanda del Sector (Muestreo)" />
        </div>
    );
};

export default SectorSaturationChart;
