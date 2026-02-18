import { useEffect, useState } from 'react';
import Chart from 'react-apexcharts';
import { api } from '../api';

import { FileText, FileSpreadsheet } from 'lucide-react';

interface RegionsTreemapProps {
    /** Filtros globales (fechas, niveles, etc.) */
    filters: any;
    /** Ruta de la API para obtener el desglose jerárquico */
    endpoint?: string;
    /** Define si el análisis aplica a aeródromos 'origin' (salida) o 'destination' (llegada) */
    dimension?: 'origin' | 'destination';
    /** Control de acceso a botones de descarga de reportes */
    allowExport?: boolean;
}

/**
 * Visualización Jerárquica: Mapa de Árbol por Regiones (Treemap).
 * 
 * Este componente representa la distribución del tráfico aéreo mediante 
 * rectángulos anidados donde el área es proporcional al volumen de vuelos.
 * Estructura: Región Aeronáutica (Padre) -> Aeropuerto ICAO (Hijo).
 * 
 * Atributos Técnicos:
 * - Colorización por series para diferenciar regiones visualmente.
 * - Zoom inteligente y tooltips con métricas escaladas.
 * - Integración con el motor de reportes XLS/PDF.
 * 
 * @param props - Configuración de dimensionamiento y filtrado.
 */
export const RegionsTreemap = ({ filters, endpoint = '/stats/flights-by-region', dimension = 'origin', allowExport = true }: RegionsTreemapProps) => {
    // series: [{ name: 'Región', data: [{ x: 'ICAO', y: Valor }] }]
    const [series, setSeries] = useState<any[]>([]);

    const [loading, setLoading] = useState(false);

    const [empty, setEmpty] = useState(false);

    const [exporting, setExporting] = useState(false);

    /**
     * Delegación de generación de reportes regionales al backend.
     * @param type - Formato de documento solicitado.
     */
    const handleExport = async (type: 'pdf' | 'excel') => {
        if (exporting) return;
        setExporting(true);
        try {
            const endpointUrl = type === 'pdf' ? '/reports/region/pdf' : '/reports/region/excel';
            const filename = `rep_region_${dimension}_${new Date().toISOString().slice(0, 10)}.${type === 'pdf' ? 'pdf' : 'xlsx'}`;

            // Adjunta la dimensión actual al payload para filtrar por origen/destino en SQL
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
            console.error("Fallo crítico en exportación regional:", error);
        } finally {
            setExporting(false);
        }
    };

    /**
     * Orquestador de carga de datos para el Treemap.
     * Llama recursivamente cuando los filtros globales cambian.
     */
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setEmpty(false);
            try {
                const response = await api.post(endpoint, filters);

                if (response.data && response.data.length > 0) {
                    setSeries(response.data);
                } else {
                    setEmpty(true);
                    setSeries([]);
                }
            } catch (error) {
                console.error("Fallo de red en carga de Regiones:", error);
                setEmpty(true);
            } finally {
                setLoading(false);
            }
        };

        const t = setTimeout(fetchData, 500);
        return () => clearTimeout(t);
    }, [filters, endpoint]);

    /**
     * Opciones de renderizado de ApexCharts.
     * Configura el modo Treemap no-distribuido para permitir la agrupación por colores de serie.
     */
    const chartOptions: any = {
        chart: {
            type: 'treemap',
            fontFamily: 'Inter, sans-serif',
            toolbar: { show: true }
        },
        dataLabels: {
            enabled: true,
            style: { fontSize: '12px', fontWeight: 'bold' },
            formatter: (text: string, op: any) => [text, op.value]
        },
        plotOptions: {
            treemap: {
                distributed: false, // Importante: Mantiene colores coherentes por región (serie)
                enableShades: true,
                shadeIntensity: 0.5
            }
        },
        legend: { show: true, position: 'top' },
        tooltip: {
            y: { formatter: (val: number) => `${val} operaciones` }
        },
        colors: [
            "#3b82f6", // Región 1
            "#10b981", // Región 2
            "#f59e0b", // Región 3
            "#ef4444", // Región 4
            "#8b5cf6", // Región 5
            "#ec4899"  // Región 6
        ]
    };

    if (loading) return (
        <div className="h-[350px] flex justify-center items-center text-slate-400 gap-2">
            <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            Cargando datos regionales...
        </div>
    );

    if (empty) return (
        <div className="h-[350px] flex justify-center items-center text-slate-400 bg-slate-50 rounded-xl border-dashed border-2 border-slate-200">
            No hay datos suficientes para mostrar la distribución por regiones.
        </div>
    );

    return (
        <div className="w-full bg-white p-4 rounded-xl">
            {/* BOTONES DE EXPORTACIÓN */}
            {allowExport && (
                <div className="flex justify-end gap-2 mb-2">
                    <button onClick={() => handleExport('pdf')} disabled={exporting} className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-white bg-rose-500 rounded hover:bg-rose-600 disabled:opacity-50 transition-colors shadow-sm">
                        <FileText className="w-3 h-3" /> PDF
                    </button>
                    <button onClick={() => handleExport('excel')} disabled={exporting} className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-white bg-emerald-600 rounded hover:bg-emerald-700 disabled:opacity-50 transition-colors shadow-sm">
                        <FileSpreadsheet className="w-3 h-3" /> Excel
                    </button>
                </div>
            )}
            {/* GRÁFICO DE APEXCHARTS */}
            <Chart
                options={chartOptions}
                series={series}
                type="treemap"
                height={350}
            />
        </div>
    );
};
