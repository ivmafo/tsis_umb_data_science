import { useEffect, useState } from 'react';
import Chart from 'react-apexcharts';
import { api } from '../api';

import { FileText, FileSpreadsheet } from 'lucide-react';

interface FlightTypeChartProps {
    /** Filtros reactivos desde la barra lateral (Fechas, Orígenes, etc.) */
    filters: any;
    /** Habilita la funcionalidad de descarga de reportes categorizados */
    allowExport?: boolean;
}

/**
 * Visualización de Segmentación: Distribución por Tipo de Vuelo.
 * 
 * Componente que muestra un gráfico radial (Donut) con las proporciones
 * de vuelos según su naturaleza operativa (Regular, No Regular, Carga, etc.).
 * 
 * Funcionalidades:
 * - Desglose porcentual automático en Tooltips.
 * - Leyenda interactiva con sumatoria de unidades.
 * - Contador 'Total' centralizado en el centro del gráfico.
 * 
 * @param props - Propiedades de control y filtrado.
 */
export const FlightTypeChart = ({ filters, allowExport = true }: FlightTypeChartProps) => {
    // series: Array numérico con los conteos absolutos
    const [series, setSeries] = useState<number[]>([]);

    // labels: Etiquetas textuales correspondientes a cada segmento
    const [labels, setLabels] = useState<string[]>([]);

    // loading: Feedback de procesamiento asíncrono
    const [loading, setLoading] = useState(false);

    const [empty, setEmpty] = useState(false);

    const [exporting, setExporting] = useState(false);

    /**
     * Interfaz de exportación para reportes de categorización.
     * @param type - Formato de salida ('pdf' | 'excel').
     */
    const handleExport = async (type: 'pdf' | 'excel') => {
        if (exporting) return;
        setExporting(true);
        try {
            const endpoint = type === 'pdf' ? '/reports/flight-type/pdf' : '/reports/flight-type/excel';
            const filename = `reporte_tipo_vuelo.${type === 'pdf' ? 'pdf' : 'xlsx'}`;
            const response = await api.post(endpoint, filters, { responseType: 'blob' });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.parentNode?.removeChild(link);
        } catch (error) {
            console.error("Fallo en exportación de tipos:", error);
        } finally {
            setExporting(false);
        }
    };

    // Actualiza la visualización ante cambios en el payload de filtros
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setEmpty(false);
            try {
                // Reconstrucción del payload para asegurar tipos consistentes en backend DuckDB
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

                const response = await api.post('/stats/flights-by-type', payload);

                if (response.data && response.data.length > 0) {
                    const newSeries = response.data.map((item: any) => item.value);
                    const newLabels = response.data.map((item: any) => item.name);

                    setSeries(newSeries);
                    setLabels(newLabels);
                } else {
                    setEmpty(true);
                    setSeries([]);
                    setLabels([]);
                }
            } catch (error) {
                console.error("Error en estadísticas de tipo de vuelo:", error);
                setEmpty(true);
            } finally {
                setLoading(false);
            }
        };

        const t = setTimeout(fetchData, 500);
        return () => clearTimeout(t);
    }, [filters]);

    /**
     * Definición de apariencia para ApexCharts Donut.
     * Incluye labels de suma total y formateadores de leyenda.
     */
    const options: any = {
        chart: {
            type: 'donut',
            fontFamily: 'Inter, sans-serif',
        },
        labels: labels,
        colors: ['#3b82f6', '#ec4899', '#10b981', '#f59e0b', '#6366f1', '#84cc16'],
        plotOptions: {
            pie: {
                donut: {
                    size: '65%',
                    labels: {
                        show: true,
                        name: { show: true, fontSize: '14px', offsetY: -4 },
                        value: {
                            show: true,
                            fontSize: '24px',
                            fontWeight: 600,
                            offsetY: 8,
                            formatter: (val: any) => val
                        },
                        total: {
                            show: true,
                            showAlways: true,
                            label: 'Total General',
                            fontSize: '14px',
                            color: '#64748b',
                            formatter: (w: any) => w.globals.seriesTotals.reduce((a: any, b: any) => a + b, 0)
                        }
                    }
                }
            }
        },
        dataLabels: { enabled: false },
        legend: {
            position: 'right',
            offsetY: 0,
            height: 230,
            fontFamily: 'Inter, sans-serif',
            itemMargin: { horizontal: 0, vertical: 5 },
            formatter: (seriesName: string, opts: any) => `${seriesName}: ${opts.w.globals.series[opts.seriesIndex]}`
        },
        stroke: { show: true, colors: ['transparent'] },
        tooltip: {
            enabled: true,
            y: { formatter: (val: any) => `${val} Vuelos` }
        }
    };

    if (loading) return (
        <div className="h-80 flex justify-center items-center text-slate-400 gap-2">
            <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            Cargando...
        </div>
    );

    if (empty) return (
        <div className="h-80 flex justify-center items-center text-slate-400 bg-slate-50 rounded-xl border-dashed border-2 border-slate-200">
            No hay datos para mostrar.
        </div>
    );

    return (
        <div className="w-full bg-white p-2 rounded-xl flex flex-col items-center justify-center relative">
            {allowExport && (
                <div className="absolute top-2 right-2 flex gap-2 z-10">
                    <button onClick={() => handleExport('pdf')} disabled={exporting} className="p-1.5 text-white bg-rose-500 rounded hover:bg-rose-600 disabled:opacity-50" title="PDF">
                        <FileText className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleExport('excel')} disabled={exporting} className="p-1.5 text-white bg-emerald-600 rounded hover:bg-emerald-700 disabled:opacity-50" title="Excel">
                        <FileSpreadsheet className="w-4 h-4" />
                    </button>
                </div>
            )}
            <div className="w-full h-[400px]">
                <Chart
                    options={options}
                    series={series}
                    type="donut"
                    height={380}
                />
            </div>
        </div>
    );
};
