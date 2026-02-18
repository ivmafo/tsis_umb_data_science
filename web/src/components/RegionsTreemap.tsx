import { useEffect, useState } from 'react';
import Chart from 'react-apexcharts';
import { api } from '../api';

import { FileText, FileSpreadsheet } from 'lucide-react';

interface RegionsTreemapProps {
    filters: any;
    endpoint?: string;
    dimension?: 'origin' | 'destination'; // New prop to identify report type
    allowExport?: boolean;
}

export const RegionsTreemap = ({ filters, endpoint = '/stats/flights-by-region', dimension = 'origin', allowExport = true }: RegionsTreemapProps) => {
    const [series, setSeries] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [empty, setEmpty] = useState(false);
    const [exporting, setExporting] = useState(false);

    const handleExport = async (type: 'pdf' | 'excel') => {
        if (exporting) return;
        setExporting(true);
        try {
            const endpointUrl = type === 'pdf' ? '/reports/region/pdf' : '/reports/region/excel';
            const filename = `reporte_region_${dimension}.${type === 'pdf' ? 'pdf' : 'xlsx'}`;

            // Should pass dimension in body
            const payload = { ...filters, dimension };

            const response = await api.post(endpointUrl, payload, { responseType: 'blob' });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.parentNode?.removeChild(link);
        } catch (error) {
            console.error("Export error:", error);
            alert("Error al exportar. Verifique que el servicio de reportes esté activo.");
        } finally {
            setExporting(false);
        }
    };

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setEmpty(false);
            try {
                const response = await api.post(endpoint, filters);

                // API returns: [{ name: 'Andina', data: [{ x: 'SKBO', y: 1500 }, ...] }, ...]
                // This matches ApexCharts Multi-series Treemap format

                if (response.data && response.data.length > 0) {
                    setSeries(response.data);
                } else {
                    setEmpty(true);
                    setSeries([]);
                }
            } catch (error) {
                console.error("Error fetching regions:", error);
                setEmpty(true);
            } finally {
                setLoading(false);
            }
        };

        const t = setTimeout(fetchData, 500);
        return () => clearTimeout(t);
    }, [filters]);

    const chartOptions: any = {
        chart: {
            type: 'treemap',
            toolbar: {
                show: true,
                tools: {
                    download: true,
                    selection: false,
                    zoom: false,
                    zoomin: false,
                    zoomout: false,
                    pan: false,
                    reset: false
                }
            },
            fontFamily: 'Inter, sans-serif'
        },
        title: {
            text: undefined
        },
        dataLabels: {
            enabled: true,
            style: {
                fontSize: '12px',
                fontWeight: 'bold',
                colors: ['#fff']
            },
            formatter: function (text: string, op: any) {
                return [text, op.value];
            }
        },
        plotOptions: {
            treemap: {
                distributed: false, // False is correct for multi-series (each series has its own color usually)
                enableShades: true,
                shadeIntensity: 0.5,
                colorScale: {
                    ranges: [
                        { from: 0, to: 0, color: '#f1f5f9' }
                    ]
                }
            }
        },
        legend: {
            show: true,
            position: 'top',
            horizontalAlign: 'center'
        },
        tooltip: {
            y: {
                formatter: function (val: number) {
                    return val + " vuelos"
                }
            }
        },
        // We can define a palette of colors for the Regions
        colors: [
            "#3b82f6", // Blue
            "#10b981", // Emerald
            "#f59e0b", // Amber
            "#ef4444", // Red
            "#8b5cf6", // Violet
            "#ec4899", // Pink
            "#06b6d4"  // Cyan
        ]
    };

    if (loading) return (
        <div className="h-[350px] flex justify-center items-center text-slate-400 gap-2">
            <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            Cargando...
        </div>
    );

    if (empty) return (
        <div className="h-[350px] flex justify-center items-center text-slate-400 bg-slate-50 rounded-xl border-dashed border-2 border-slate-200">
            No hay datos suficientes para mostrar regiones.
        </div>
    );

    return (
        <div className="w-full bg-white p-4 rounded-xl">
            {allowExport && (
                <div className="flex justify-end gap-2 mb-2">
                    <button onClick={() => handleExport('pdf')} disabled={exporting} className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-white bg-rose-500 rounded hover:bg-rose-600 disabled:opacity-50">
                        <FileText className="w-3 h-3" /> PDF
                    </button>
                    <button onClick={() => handleExport('excel')} disabled={exporting} className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-white bg-emerald-600 rounded hover:bg-emerald-700 disabled:opacity-50">
                        <FileSpreadsheet className="w-3 h-3" /> Excel
                    </button>
                </div>
            )}
            <Chart
                options={chartOptions}
                series={series}
                type="treemap"
                height={350}
            />
        </div>
    );
};
