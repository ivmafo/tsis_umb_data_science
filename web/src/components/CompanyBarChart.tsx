import { useEffect, useState } from 'react';
import Chart from 'react-apexcharts';
import { api } from '../api';

import { FileText, FileSpreadsheet } from 'lucide-react';

interface CompanyBarChartProps {
    filters: any;
    allowExport?: boolean;
}

export const CompanyBarChart = ({ filters, allowExport = true }: CompanyBarChartProps) => {
    const [series, setSeries] = useState<any[]>([]);
    const [categories, setCategories] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [empty, setEmpty] = useState(false);
    const [exporting, setExporting] = useState(false);

    const handleExport = async (type: 'pdf' | 'excel') => {
        if (exporting) return;
        setExporting(true);
        try {
            const endpoint = type === 'pdf' ? '/reports/company/pdf' : '/reports/company/excel';
            const filename = `reporte_empresa.${type === 'pdf' ? 'pdf' : 'xlsx'}`;
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

                const response = await api.post('/stats/flights-by-company', payload);

                if (response.data && response.data.length > 0) {
                    const data = response.data;
                    const values = data.map((item: any) => item.value);
                    const cats = data.map((item: any) => item.name);

                    setSeries([{
                        name: 'Vuelos',
                        data: values
                    }]);
                    setCategories(cats);
                } else {
                    setEmpty(true);
                    setSeries([]);
                    setCategories([]);
                }
            } catch (error) {
                console.error("Error fetching company stats:", error);
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
            type: 'bar',
            height: 600, // Slightly taller for bar chart
            fontFamily: 'Inter, sans-serif',
            toolbar: { show: false }
        },
        plotOptions: {
            bar: {
                borderRadius: 4,
                horizontal: true,
                barHeight: '70%',
                distributed: true
            }
        },
        colors: [
            '#3b82f6', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308',
            '#22c55e', '#06b6d4', '#6366f1', '#d946ef', '#ef4444', '#14b8a6'
        ],
        dataLabels: {
            enabled: true,
            textAnchor: 'start',
            style: {
                colors: ['#fff']
            },
            formatter: function (val: any) {
                return val
            },
            offsetX: 0,
        },
        xaxis: {
            categories: categories,
            labels: {
                style: {
                    fontFamily: 'Inter, sans-serif',
                }
            }
        },
        yaxis: {
            labels: {
                style: {
                    fontFamily: 'Inter, sans-serif',
                    fontSize: '13px',
                    fontWeight: 600
                },
                maxWidth: 200 // Ensure space for long company names
            }
        },
        grid: {
            borderColor: '#f1f5f9'
        },
        tooltip: {
            y: {
                formatter: function (val: any) {
                    return val + " Vuelos";
                }
            }
        },
        legend: {
            show: false // No legend needed for single series distributed
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
        <div className="w-full bg-white p-2 rounded-xl">
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
                options={options}
                series={series}
                type="bar"
                height={600}
            />
        </div>
    );
};
