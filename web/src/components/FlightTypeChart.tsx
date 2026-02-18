import { useEffect, useState } from 'react';
import Chart from 'react-apexcharts';
import { api } from '../api';

import { FileText, FileSpreadsheet } from 'lucide-react';

interface FlightTypeChartProps {
    filters: any;
    allowExport?: boolean;
}

export const FlightTypeChart = ({ filters, allowExport = true }: FlightTypeChartProps) => {
    const [series, setSeries] = useState<number[]>([]);
    const [labels, setLabels] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [empty, setEmpty] = useState(false);
    const [exporting, setExporting] = useState(false);

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
            console.error(error);
            alert("Error al exportar.");
        } finally {
            setExporting(false);
        }
    };

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setEmpty(false);
            try {
                // Construct Filters Payload (Same as Treemaps)
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
                    // Start formatting for ApexCharts Donut
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
                console.error("Error fetching flight type stats:", error);
                setEmpty(true);
            } finally {
                setLoading(false);
            }
        };

        const t = setTimeout(fetchData, 500);
        return () => clearTimeout(t);
    }, [filters]);

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
                        name: {
                            show: true,
                            fontSize: '14px',
                            fontFamily: 'Inter, sans-serif',
                            offsetY: -4
                        },
                        value: {
                            show: true,
                            fontSize: '24px',
                            fontFamily: 'Inter, sans-serif',
                            fontWeight: 600,
                            offsetY: 8,
                            formatter: function (val: any) {
                                return val;
                            }
                        },
                        total: {
                            show: true,
                            showAlways: true,
                            label: 'Total',
                            fontSize: '14px',
                            fontFamily: 'Inter, sans-serif',
                            color: '#64748b',
                            formatter: function (w: any) {
                                return w.globals.seriesTotals.reduce((a: any, b: any) => a + b, 0);
                            }
                        }
                    }
                }
            }
        },
        dataLabels: {
            enabled: false
        },
        legend: {
            position: 'right',
            offsetY: 0,
            height: 230,
            fontFamily: 'Inter, sans-serif',
            itemMargin: {
                horizontal: 0,
                vertical: 5
            },
            formatter: function (seriesName: string, opts: any) {
                return seriesName + ":  " + opts.w.globals.series[opts.seriesIndex]
            }
        },
        stroke: {
            show: true,
            colors: ['transparent']
        },
        tooltip: {
            enabled: true,
            y: {
                formatter: function (val: any) {
                    return val + " Vuelos";
                }
            }
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
