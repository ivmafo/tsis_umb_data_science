import { useEffect, useState } from 'react';
import Chart from 'react-apexcharts';
import { api } from '../api';
import { FileText, FileSpreadsheet } from 'lucide-react';

interface DestinationsTreemapProps {
    filters: any;
    allowExport?: boolean;
}

export const DestinationsTreemap = ({ filters, allowExport = true }: DestinationsTreemapProps) => {
    const [series, setSeries] = useState<any[]>([]);
    const [topData, setTopData] = useState<any[]>([]);
    const [bottomData, setBottomData] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [empty, setEmpty] = useState(false);
    const [exporting, setExporting] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setEmpty(false);
            try {
                // Construct Filters Payload
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

                const response = await api.post('/stats/flights-by-destination', payload);

                if (response.data && response.data.length > 0) {
                    // Start formatting for ApexCharts
                    const formattedData = response.data.map((item: any) => ({
                        x: item.name,
                        y: item.value
                    }));

                    setSeries([{
                        data: formattedData
                    }]);

                    // Extract Top 10
                    setTopData(response.data.slice(0, 10));

                    // Extract Bottom 10 (Last 10 items)
                    setBottomData(response.data.slice(-10));

                } else {
                    setEmpty(true);
                    setSeries([]);
                    setTopData([]);
                    setBottomData([]);
                }
            } catch (error) {
                console.error("Error fetching destination stats:", error);
                setEmpty(true);
            } finally {
                setLoading(false);
            }
        };

        const t = setTimeout(fetchData, 500);
        return () => clearTimeout(t);
    }, [filters]);

    const handleExport = async (type: 'pdf' | 'excel') => {
        if (exporting) return;
        setExporting(true);
        try {
            // Construct Filters Payload (Duplicate logic, ideally refactor)
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

            const endpoint = type === 'pdf' ? '/reports/destination/pdf' : '/reports/destination/excel';
            const filename = type === 'pdf' ? 'reporte_destino.pdf' : 'reporte_destino.xlsx';

            const response = await api.post(endpoint, payload, {
                responseType: 'blob'
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.parentNode?.removeChild(link);
        } catch (error: any) {
            console.error(`Error exporting ${type}:`, error);
            if (error.response) {
                alert(`Error al exportar: Servidor respondió con ${error.response.status} - ${error.response.statusText}`);
            } else if (error.request) {
                alert("Error al exportar: No se recibió respuesta del servidor. Verifique su conexión.");
            } else {
                alert(`Error al exportar: ${error.message}`);
            }
        } finally {
            setExporting(false);
        }
    };

    const options: any = {
        legend: {
            show: false
        },
        chart: {
            height: 500,
            type: 'treemap',
            toolbar: {
                show: false
            },
            fontFamily: 'Inter, sans-serif',
            animations: {
                enabled: true,
                easing: 'easeinout',
                speed: 800,
                animateGradually: {
                    enabled: true,
                    delay: 150
                },
                dynamicAnimation: {
                    enabled: true,
                    speed: 350
                }
            }
        },
        title: {
            text: undefined
        },
        colors: [
            '#10b981', '#34d399', '#f43f5e', '#f97316', '#eab308', '#8b5cf6',
            '#3b82f6', '#06b6d4', '#6366f1', '#d946ef', '#ef4444', '#14b8a6',
            '#64748b', '#a855f7', '#d946ef', '#f43f5e'
        ], // Slightly different palette (more greens/teals) needed? Kept similar for now but started with green.
        plotOptions: {
            treemap: {
                distributed: true,
                enableShades: true,
                shadeIntensity: 0.5,
                reverseNegativeShade: true,
                useFillColorAsStroke: false
            }
        },
        dataLabels: {
            enabled: true,
            style: {
                fontSize: '14px',
                fontWeight: 'bold',
                colors: ['#ffffff']
            },
            formatter: function (text: string, op: any) {
                return [text, op.value];
            },
            offsetY: -4
        },
        tooltip: {
            enabled: true,
            theme: 'light',
            style: {
                fontSize: '14px',
                fontFamily: 'Inter, sans-serif',
            },
            x: {
                show: true,
            },
            y: {
                formatter: function (value: number) {
                    return value + " Vuelos";
                },
                title: {
                    formatter: function () {
                        return "";
                    }
                }
            },
            marker: {
                show: false,
            }
        },
        stroke: {
            show: true,
            width: 2,
            colors: ['#fff']
        }
    };

    if (loading) return (
        <div className="h-96 flex justify-center items-center text-slate-400 gap-2">
            <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            Cargando...
        </div>
    );

    if (empty) return (
        <div className="h-96 flex justify-center items-center text-slate-400 bg-slate-50 rounded-xl border-dashed border-2 border-slate-200">
            No hay vuelos que coincidan con los filtros.
        </div>
    );

    return (
        <div className="w-full bg-white p-2 rounded-xl">
            {/* Header with Export Buttons */}
            {allowExport && (
                <div className="flex justify-end gap-2 mb-2">
                    <button
                        onClick={() => handleExport('pdf')}
                        disabled={exporting}
                        className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-white bg-rose-500 rounded hover:bg-rose-600 transition-colors disabled:opacity-50"
                        title="Exportar a PDF"
                    >
                        <FileText className="w-3.5 h-3.5" />
                        PDF
                    </button>
                    <button
                        onClick={() => handleExport('excel')}
                        disabled={exporting}
                        className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-white bg-emerald-600 rounded hover:bg-emerald-700 transition-colors disabled:opacity-50"
                        title="Exportar a Excel"
                    >
                        <FileSpreadsheet className="w-3.5 h-3.5" />
                        Excel
                    </button>
                </div>
            )}
            {/* Chart Section */}
            <div className="h-[520px] mb-6">
                <Chart
                    options={options}
                    series={series}
                    type="treemap"
                    height={500}
                />
            </div>

            {/* Tables Section - Grid Layout */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* Top 10 Table */}
                <div className="overflow-hidden rounded-lg border border-slate-200 shadow-sm">
                    <div className="bg-slate-50 px-4 py-3 border-b border-slate-200">
                        <h3 className="text-sm font-semibold text-slate-700">Top 10 Destinos (Más frecuentes)</h3>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-slate-200">
                            <thead className="bg-white">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider w-16">#</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Destino</th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Vuelos</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-slate-200">
                                {topData.map((item, index) => (
                                    <tr key={item.name + 'top'} className="hover:bg-slate-50 transition-colors">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{index + 1}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">{item.name}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-mono font-semibold text-indigo-600">{item.value}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Bottom 10 Table */}
                {bottomData.length > 0 && (
                    <div className="overflow-hidden rounded-lg border border-slate-200 shadow-sm">
                        <div className="bg-slate-50 px-4 py-3 border-b border-slate-200">
                            <h3 className="text-sm font-semibold text-slate-700">Bottom 10 Destinos (Menos frecuentes)</h3>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-slate-200">
                                <thead className="bg-white">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider w-16">#</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Destino</th>
                                        <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Vuelos</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-slate-200">
                                    {bottomData.map((item, index) => (
                                        <tr key={item.name + 'bottom'} className="hover:bg-slate-50 transition-colors">
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{index + 1}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">{item.name}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-mono font-semibold text-red-500">{item.value}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
