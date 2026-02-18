import { useState, useMemo } from 'react';
import { MultiSelectLookup } from '../components/MultiSelectLookup';
import { FlightsTreemap } from '../components/FlightsTreemap';
import { DestinationsTreemap } from '../components/DestinationsTreemap';
import { FlightTypeChart } from '../components/FlightTypeChart';
import { CompanyBarChart } from '../components/CompanyBarChart';
import { FlightsTimeChart } from '../components/FlightsTimeChart';
import { FlightsYearChart } from '../components/FlightsYearChart';
import { PeakHoursHeatmap } from '../components/PeakHoursHeatmap';
import { RegionsTreemap } from '../components/RegionsTreemap';
import { getAirports, refreshFilters, searchFilterValues, exportRawData, downloadExecutiveReport } from '../api';
import { Filter, RefreshCw, BarChart3, Download, FileText, FileSpreadsheet } from 'lucide-react';

/**
 * Vista de Distribución de Vuelos.
 * Dashboard integral para el análisis estadístico y visualización de la operación aérea.
 * Permite filtrar por múltiples dimensiones (tiempo, espacio, flota) y exportar reportes ejecutivos.
 */
/**
 * Orquestador Analítico: Vista de Distribución de Vuelos.
 * 
 * Este componente es el núcleo de inteligencia de negocio de la plataforma.
 * Actúa como una "Single-Page Analysis" que centraliza el filtrado multidimensional
 * y la visualización agregada de métricas operacionales.
 * 
 * Capacidades Principales:
 * - Filtrado Olap-like: Segmentación por Tiempo, Espacio, Aeronave y Operador.
 * - Motor de Exportación Dual: Generación de data cruda (CSV) y reportes ejecutivos (PDF/XLS).
 * - Reactividad Coordinada: Sincroniza múltiples widgets de visualización mediante un bus de filtros memorizado.
 */
export const FlightDistributionView = () => {
    // FILTROS DE SEGMENTACIÓN (Multi-Select Pools)
    // Se gestionan como arrays de objetos {id, label, value} para compatibilidad con MultiSelectLookup
    const [selectedMetricula, setSelectedMatricula] = useState<any[]>([]);
    const [selectedTipoAeronave, setSelectedTipoAeronave] = useState<any[]>([]);
    const [selectedEmpresa, setSelectedEmpresa] = useState<any[]>([]);
    const [selectedTipoVuelo, setSelectedTipoVuelo] = useState<any[]>([]);
    const [selectedCallsign, setSelectedCallsign] = useState<any[]>([]);
    const [selectedOrigins, setSelectedOrigins] = useState<any[]>([]);
    const [selectedDestinations, setSelectedDestinations] = useState<any[]>([]);

    // DIMENSIONES TEMPORALES Y LIMITADORES OPERATIVOS
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [minLevel, setMinLevel] = useState('');
    const [maxLevel, setMaxLevel] = useState('');

    // CONTROL DE ESTADOS DE TRANSACCIÓN Y UI
    const [refreshing, setRefreshing] = useState(false);
    const [showReport, setShowReport] = useState(true);
    const [exporting, setExporting] = useState(false);
    const [downloadingReport, setDownloadingReport] = useState(false);

    /**
     * Proveedor asíncrono de Aeropuertos.
     * Implementa la lógica de búsqueda para los buscadores de origen y destino.
     */
    const fetchAirportOptions = async (query: string) => {
        try {
            const response = await getAirports(1, 20, query);
            return response.data.map(airport => ({
                id: airport.id,
                label: `${airport.icao_code} - ${airport.name}`,
                value: airport
            }));
        } catch (error) {
            console.error("Fallo al recuperar catálogo de aeropuertos:", error);
            return [];
        }
    };

    /**
     * Factoría de Buscadores de Filtros Paramétricos.
     * Crea una función de búsqueda especializada para una categoría de filtro (ParentID).
     * @param parentId - Identificador de la categoría en la tabla de filtros del backend.
     */
    const createFilterFetcher = (parentId: number) => async (query: string) => {
        try {
            const results = await searchFilterValues(parentId, query);
            return results.map(r => ({
                id: r.id,
                label: r.value,
                value: r.value
            }));
        } catch (error) {
            console.error(`Fallo técnico en buscador persistente (ID: ${parentId}):`, error);
            return [];
        }
    };

    /**
     * Acción de Mantenimiento: Refresco de Diccionario de Filtros.
     * Dispara la reconstrucción de los índices de autocompletado en el servidor.
     */
    const handleRefreshFilters = async () => {
        if (!confirm("ADVERTENCIA: ¿Desea reconstruir los índices de filtros? Esta operación escanea toda la tabla de vuelos.")) return;
        setRefreshing(true);
        try {
            const res = await refreshFilters();
            alert(`Índices actualizados. El sistema detectó ${res.total_records} registros únicos.`);
        } catch (error) {
            console.error("Error en sincronización de filtros:", error);
            alert("Error al intentar refrescar la caché del servidor.");
        } finally {
            setRefreshing(false);
        }
    };

    const handleGenerateReport = () => {
        setShowReport(true);
    };

    /**
     * Bus de Filtros Memorizado (Compute Optimization).
     * Previene que los componentes de visualización se refresquen si no han cambiado las dimensiones de búsqueda.
     */
    const currentFilters = useMemo(() => ({
        startDate,
        endDate,
        minLevel,
        maxLevel,
        selectedOrigins,
        selectedDestinations,
        selectedMetricula,
        selectedTipoAeronave,
        selectedEmpresa,
        selectedTipoVuelo,
        selectedCallsign
    }), [
        startDate, endDate, minLevel, maxLevel,
        selectedOrigins, selectedDestinations, selectedMetricula,
        selectedTipoAeronave, selectedEmpresa, selectedTipoVuelo, selectedCallsign
    ]);

    /**
     * Handler de Exportación Masiva (CSV).
     * Mapea el estado de la UI al esquema de nombres esperado por el backend.
     */
    const handleExport = async () => {
        // Guardián de relevancia: Evita exportaciones vacías que saturan el worker
        const hasFilters = Object.values(currentFilters).some(value => {
            if (Array.isArray(value)) return value.length > 0;
            return value !== '' && value !== null && value !== undefined;
        });

        if (!hasFilters) {
            alert("Debe definir al menos un criterio (Fecha, Nivel o Aeropuerto) para la extracción de datos.");
            return;
        }

        setExporting(true);
        try {
            // Transformación del payload al formato de contrato del API
            const payload = {
                start_date: startDate || null,
                end_date: endDate || null,
                min_level: minLevel || null,
                max_level: maxLevel || null,
                origins: selectedOrigins?.map((o: any) => o.value?.icao_code || o.value) || [],
                destinations: selectedDestinations?.map((d: any) => d.value?.icao_code || d.value) || [],
                matriculas: selectedMetricula?.map((m: any) => m.value) || [],
                tipo_aeronave: selectedTipoAeronave?.map((t: any) => t.value) || [],
                empresa: selectedEmpresa?.map((e: any) => e.value) || [],
                tipo_vuelo: selectedTipoVuelo?.map((t: any) => t.value) || [],
                callsign: selectedCallsign?.map((c: any) => c.value) || [],
            };

            const blob = await exportRawData(payload);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `extraccion_vuelos_${new Date().toISOString().slice(0, 10)}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error("Fallo crítico en exportación CSV:", error);
            alert("Error al generar la extracción de datos.");
        } finally {
            setExporting(false);
        }
    };

    /**
     * Generador de Reportes Ejecutivos Dinámicos.
     * Solicita al servidor un renderizado PDF/XLS basado en los filtros activos.
     * @param type - Formato de destino.
     */
    const handleExecutiveReport = async (type: 'pdf' | 'excel') => {
        setDownloadingReport(true);
        try {
            const payload = {
                start_date: startDate || null,
                end_date: endDate || null,
                min_level: minLevel || null,
                max_level: maxLevel || null,
                origins: selectedOrigins?.map((o: any) => o.value?.icao_code || o.value) || [],
                destinations: selectedDestinations?.map((d: any) => d.value?.icao_code || d.value) || [],
                matriculas: selectedMetricula?.map((m: any) => m.value) || [],
                tipo_aeronave: selectedTipoAeronave?.map((t: any) => t.value) || [],
                empresa: selectedEmpresa?.map((e: any) => e.value) || [],
                tipo_vuelo: selectedTipoVuelo?.map((t: any) => t.value) || [],
                callsign: selectedCallsign?.map((c: any) => c.value) || [],
            };

            const blob = await downloadExecutiveReport(payload, type);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `rep_ejecutivo_vuelos_${new Date().toISOString().slice(0, 10)}.${type === 'pdf' ? 'pdf' : 'xlsx'}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error("Fallo al generar reporte ejecutivo:", error);
            alert("Error al descargar el informe consolidado.");
        } finally {
            setDownloadingReport(false);
        }
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            {/* ENCABEZADO Y CONTROLES GLOBALES */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-slate-800">Distribución de Vuelos</h1>
                    <p className="text-slate-500 mt-1">Análisis y visualización de rutas aéreas procesadas</p>
                </div>
                <div className="flex gap-2">
                    <button
                        className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors shadow-sm"
                        onClick={handleGenerateReport}
                    >
                        <BarChart3 className="w-4 h-4" />
                        <span>Generar Reportes</span>
                    </button>

                    {/* Menú desplegable para Informe Ejecutivo */}
                    <div className="relative inline-block text-left group">
                        <button
                            disabled={downloadingReport}
                            className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors shadow-sm disabled:opacity-50"
                        >
                            {downloadingReport ? <RefreshCw className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4 text-indigo-600" />}
                            <span>Informe Ejecutivo</span>
                        </button>
                        <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 hidden group-hover:block border border-slate-100">
                            <button onClick={() => handleExecutiveReport('pdf')} className="flex items-center gap-2 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 w-full text-left">
                                <FileText className="w-4 h-4 text-rose-500" /> Descargar PDF
                            </button>
                            <button onClick={() => handleExecutiveReport('excel')} className="flex items-center gap-2 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 w-full text-left">
                                <FileSpreadsheet className="w-4 h-4 text-emerald-600" /> Descargar Excel
                            </button>
                        </div>
                    </div>

                    {/* Exportación de Data Cruda */}
                    <button
                        className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors shadow-sm disabled:opacity-50"
                        onClick={handleExport}
                        disabled={exporting}
                    >
                        {exporting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
                        <span>{exporting ? 'Exportando...' : 'Exportar CSV'}</span>
                    </button>

                    <button
                        onClick={handleRefreshFilters}
                        disabled={refreshing}
                        className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 text-slate-600 rounded-lg hover:bg-slate-50 transition-colors disabled:opacity-50"
                    >
                        <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
                        {refreshing ? 'Actualizando...' : 'Refrescar Filtros'}
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                {/* CONTENIDO PRINCIPAL: DASHBOARD DE GRÁFICOS */}
                <div className="lg:col-span-9 space-y-6 order-2 lg:order-1">
                    {showReport ? (
                        <div className="space-y-6">
                            {/* Fila 1: Origen y Destino */}
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                                    <div className="flex items-center gap-2 mb-4 text-slate-700 font-semibold border-b border-slate-100 pb-2">
                                        <BarChart3 className="w-5 h-5 text-indigo-600" />
                                        <h2 className="text-lg">Vuelos por Origen</h2>
                                    </div>
                                    <FlightsTreemap filters={currentFilters} />
                                </div>
                                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                                    <div className="flex items-center gap-2 mb-4 text-slate-700 font-semibold border-b border-slate-100 pb-2">
                                        <BarChart3 className="w-5 h-5 text-indigo-600" />
                                        <h2 className="text-lg">Vuelos por Destino</h2>
                                    </div>
                                    <DestinationsTreemap filters={currentFilters} />
                                </div>
                            </div>

                            {/* Fila 2: Distribución por Regiones (Origen) */}
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                                <div className="flex items-center gap-2 mb-4 text-slate-700 font-semibold border-b border-slate-100 pb-2">
                                    <BarChart3 className="w-5 h-5 text-indigo-600" />
                                    <h2 className="text-lg">Distribución Geográfica: Regiones y Origen</h2>
                                </div>
                                <RegionsTreemap filters={currentFilters} />
                            </div>

                            {/* Fila 3: Distribución por Regiones (Destino) */}
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                                <div className="flex items-center gap-2 mb-4 text-slate-700 font-semibold border-b border-slate-100 pb-2">
                                    <BarChart3 className="w-5 h-5 text-indigo-600" />
                                    <h2 className="text-lg">Distribución Geográfica: Regiones y Destino</h2>
                                </div>
                                <RegionsTreemap filters={currentFilters} endpoint="/stats/flights-by-region-destination" />
                            </div>

                            {/* Fila 4: Tipo de Vuelo y Empresa */}
                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                                <div className="lg:col-span-1 bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                                    <div className="flex items-center gap-2 mb-4 text-slate-700 font-semibold border-b border-slate-100 pb-2">
                                        <BarChart3 className="w-5 h-5 text-indigo-600" />
                                        <h2 className="text-lg">Tipo de Vuelo</h2>
                                    </div>
                                    <FlightTypeChart filters={currentFilters} />
                                </div>
                                <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                                    <div className="flex items-center gap-2 mb-4 text-slate-700 font-semibold border-b border-slate-100 pb-2">
                                        <BarChart3 className="w-5 h-5 text-indigo-600" />
                                        <h2 className="text-lg">Vuelos por Empresa</h2>
                                    </div>
                                    <CompanyBarChart filters={currentFilters} />
                                </div>
                            </div>

                            {/* Fila 5: Evolución Histórica (Mes / Año) */}
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                                <div className="flex items-center gap-2 mb-4 text-slate-700 font-semibold border-b border-slate-100 pb-2">
                                    <BarChart3 className="w-5 h-5 text-indigo-600" />
                                    <h2 className="text-lg">Evolución en el Tiempo (Vuelos por Mes)</h2>
                                </div>
                                <div className="mb-8">
                                    <FlightsTimeChart filters={currentFilters} />
                                </div>
                                <div className="flex items-center gap-2 mb-4 text-slate-700 font-semibold border-b border-slate-100 pb-2 mt-8">
                                    <BarChart3 className="w-5 h-5 text-indigo-500" />
                                    <h2 className="text-lg">Evolución en el Tiempo (Vuelos por Año)</h2>
                                </div>
                                <FlightsYearChart filters={currentFilters} />
                            </div>

                            {/* Fila 6: Mapas de Calor (Distribución Horaria) */}
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                                <div className="flex items-center gap-2 mb-4 text-slate-700 font-semibold border-b border-slate-100 pb-2">
                                    <BarChart3 className="w-5 h-5 text-indigo-600" />
                                    <h2 className="text-lg">Mapa de Calor: Horas Salida y Días de Semana</h2>
                                </div>
                                <PeakHoursHeatmap filters={currentFilters} timeColumn="hora_salida" color="#6366f1" />
                            </div>

                            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                                <div className="flex items-center gap-2 mb-4 text-slate-700 font-semibold border-b border-slate-100 pb-2">
                                    <BarChart3 className="w-5 h-5 text-orange-500" />
                                    <h2 className="text-lg">Mapa de Calor: Horas de Llegada y Días de Semana</h2>
                                </div>
                                <PeakHoursHeatmap filters={currentFilters} timeColumn="hora_llegada" color="#f97316" />
                            </div>
                        </div>
                    ) : (
                        <div className="bg-white p-10 rounded-xl shadow-sm border border-slate-100 text-center text-slate-400 h-96 flex flex-col items-center justify-center">
                            <div className="text-4xl mb-4 opacity-50">📊</div>
                            <p>Selecciona los filtros y presiona "Generar Reportes" para ver los resultados.</p>
                        </div>
                    )}
                </div>

                {/* BARRA LATERAL: PANEL DE FILTROS */}
                <div className="lg:col-span-3 space-y-6 order-1 lg:order-2">
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 sticky top-4">
                        <div className="flex items-center gap-2 mb-4 text-slate-700 font-semibold border-b border-slate-100 pb-2">
                            <Filter className="w-5 h-5 text-slate-500" />
                            <h2>Filtros</h2>
                        </div>

                        <div className="space-y-4">
                            {/* Filtros de Fecha y Hora */}
                            <div className="space-y-1">
                                <label className="block text-sm font-medium text-slate-700">Fecha/Hora Desde</label>
                                <input type="datetime-local" step="1" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="block w-full px-3 py-2 border border-slate-300 rounded-md sm:text-sm focus:ring-indigo-500 focus:border-indigo-500" />
                            </div>
                            <div className="space-y-1">
                                <label className="block text-sm font-medium text-slate-700">Fecha/Hora Hasta</label>
                                <input type="datetime-local" step="1" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="block w-full px-3 py-2 border border-slate-300 rounded-md sm:text-sm focus:ring-indigo-500 focus:border-indigo-500" />
                            </div>

                            {/* Filtros de Nivel de Vuelo */}
                            <div className="grid grid-cols-2 gap-2">
                                <div className="space-y-1">
                                    <label className="block text-sm font-medium text-slate-700">Nivel Min</label>
                                    <input type="number" placeholder="100" value={minLevel} onChange={(e) => setMinLevel(e.target.value)} className="block w-full px-3 py-2 border border-slate-300 rounded-md sm:text-sm" />
                                </div>
                                <div className="space-y-1">
                                    <label className="block text-sm font-medium text-slate-700">Nivel Max</label>
                                    <input type="number" placeholder="450" value={maxLevel} onChange={(e) => setMaxLevel(e.target.value)} className="block w-full px-3 py-2 border border-slate-300 rounded-md sm:text-sm" />
                                </div>
                            </div>
                        </div>

                        <hr className="my-4 border-slate-100" />

                        {/* Buscadores de Aeropuertos */}
                        <div className="space-y-4">
                            <MultiSelectLookup label="Origen" placeholder="Ej: SKBO" value={selectedOrigins} onChange={setSelectedOrigins} fetchOptions={fetchAirportOptions} />
                            <MultiSelectLookup label="Destino" placeholder="Ej: SKRG" value={selectedDestinations} onChange={setSelectedDestinations} fetchOptions={fetchAirportOptions} />
                        </div>

                        <hr className="my-4 border-slate-100" />

                        {/* Filtros Paramétricos (Dinámicos) */}
                        <div className="space-y-4">
                            <MultiSelectLookup label="Matrícula" placeholder="Buscar..." value={selectedMetricula} onChange={setSelectedMatricula} fetchOptions={createFilterFetcher(1)} />
                            <MultiSelectLookup label="Tipo Aeronave" placeholder="Buscar..." value={selectedTipoAeronave} onChange={setSelectedTipoAeronave} fetchOptions={createFilterFetcher(2)} />
                            <MultiSelectLookup label="Empresa" placeholder="Buscar..." value={selectedEmpresa} onChange={setSelectedEmpresa} fetchOptions={createFilterFetcher(3)} />
                            <MultiSelectLookup label="Tipo Vuelo" placeholder="Buscar..." value={selectedTipoVuelo} onChange={setSelectedTipoVuelo} fetchOptions={createFilterFetcher(4)} />
                            <MultiSelectLookup label="Callsign" placeholder="Buscar..." value={selectedCallsign} onChange={setSelectedCallsign} fetchOptions={createFilterFetcher(5)} />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
