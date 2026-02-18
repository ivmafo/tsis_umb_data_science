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

export const FlightDistributionView = () => {
    // State for filters
    const [selectedMetricula, setSelectedMatricula] = useState<any[]>([]);
    const [selectedTipoAeronave, setSelectedTipoAeronave] = useState<any[]>([]);
    const [selectedEmpresa, setSelectedEmpresa] = useState<any[]>([]);
    const [selectedTipoVuelo, setSelectedTipoVuelo] = useState<any[]>([]);
    const [selectedCallsign, setSelectedCallsign] = useState<any[]>([]);
    const [selectedOrigins, setSelectedOrigins] = useState<any[]>([]);
    const [selectedDestinations, setSelectedDestinations] = useState<any[]>([]);

    // Date Range State
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');

    // Level Range State
    const [minLevel, setMinLevel] = useState('');
    const [maxLevel, setMaxLevel] = useState('');

    const [refreshing, setRefreshing] = useState(false);

    // State for Report Generation
    const [showReport, setShowReport] = useState(true);
    const [exporting, setExporting] = useState(false);
    const [downloadingReport, setDownloadingReport] = useState(false);

    // Helpers to fetch options
    const fetchAirportOptions = async (query: string) => {
        try {
            const response = await getAirports(1, 20, query);
            return response.data.map(airport => ({
                id: airport.id,
                label: `${airport.icao_code} - ${airport.name}`,
                value: airport
            }));
        } catch (error) {
            console.error("Error fetching airports:", error);
            return [];
        }
    };

    // Generic fetch for dynamic filters
    const createFilterFetcher = (parentId: number) => async (query: string) => {
        try {
            const results = await searchFilterValues(parentId, query);
            return results.map(r => ({
                id: r.id,
                label: r.value,
                value: r.value
            }));
        } catch (error) {
            console.error(`Error fetching filter ${parentId}:`, error);
            return [];
        }
    };

    const handleRefreshFilters = async () => {
        if (!confirm("¿Refrescar filtros? Esto recalculará los valores disponibles basados en los datos actuales.")) return;
        setRefreshing(true);
        try {
            const res = await refreshFilters();
            alert(`Filtros actualizados. Total de valores: ${res.total_records}`);
        } catch (error) {
            console.error("Error refreshing filters:", error);
            alert("Error al refrescar filtros.");
        } finally {
            setRefreshing(false);
        }
    };

    const handleGenerateReport = () => {
        setShowReport(true);
    };

    // Consolidate filters object for the component
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
    ]);

    const handleExport = async () => {
        // Validation: At least one filter must be active
        const hasFilters = Object.values(currentFilters).some(value => {
            if (Array.isArray(value)) return value.length > 0;
            return value !== '' && value !== null && value !== undefined;
        });

        if (!hasFilters) {
            alert("Para exportar, debe seleccionar al menos un filtro (fecha, nivel, origen, etc.).");
            return;
        }

        setExporting(true);
        try {
            // Construct payload matching backend expectations (snake_case and extracted values)
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
            a.download = `data_cruda_vuelos_${new Date().toISOString().slice(0, 10)}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error("Error exporting data:", error);
            alert("Error al exportar datos. Intente nuevamente.");
        } finally {
            setExporting(false);
        }
    };

    const handleExecutiveReport = async (type: 'pdf' | 'excel') => {
        setDownloadingReport(true);
        try {
            // Construct Payload
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
            a.download = `reporte_ejecutivo_${new Date().toISOString().slice(0, 10)}.${type === 'pdf' ? 'pdf' : 'xlsx'}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error("Error downloading executive report:", error);
            alert("Error al descargar el informe ejecutivo.");
        } finally {
            setDownloadingReport(false);
        }
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-slate-800">Distribución de Vuelos</h1>
                    <p className="text-slate-500 mt-1">Análisis y visualización de rutas</p>
                </div>
                <div className="flex gap-2">
                    <button
                        className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors shadow-sm"
                        onClick={handleGenerateReport}
                    >
                        <BarChart3 className="w-4 h-4" />
                        <span>Generar Reportes</span>
                    </button>

                    {/* Executive Report Dropdown */}
                    <div className="relative inline-block text-left group">
                        <button
                            disabled={downloadingReport}
                            className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors shadow-sm disabled:opacity-50"
                        >
                            {downloadingReport ? <RefreshCw className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4 text-indigo-600" />}
                            <span>Informe Ejecutivo</span>
                        </button>
                        {/* Simple Hover Dropdown */}
                        <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 hidden group-hover:block border border-slate-100">
                            <button
                                onClick={() => handleExecutiveReport('pdf')}
                                className="flex items-center gap-2 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 w-full text-left"
                            >
                                <FileText className="w-4 h-4 text-rose-500" /> Descargar PDF
                            </button>
                            <button
                                onClick={() => handleExecutiveReport('excel')}
                                className="flex items-center gap-2 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 w-full text-left"
                            >
                                <FileSpreadsheet className="w-4 h-4 text-emerald-600" /> Descargar Excel
                            </button>
                        </div>
                    </div>

                    <button
                        className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors shadow-sm disabled:opacity-50"
                        onClick={handleExport}
                        disabled={exporting}
                    >
                        {exporting ? (
                            <RefreshCw className="w-4 h-4 animate-spin" />
                        ) : (
                            <Download className="w-4 h-4" />
                        )}
                        <span>{exporting ? 'Exportando...' : 'Exportar'}</span>
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

                {/* Main Content (Charts) */}
                <div className="lg:col-span-9 space-y-6 order-2 lg:order-1">
                    {showReport ? (
                        <div className="space-y-6">
                            {/* First Row: Origin and Destination (50/50) */}
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 animate-in fade-in slide-in-from-bottom-4 duration-500">
                                    <div className="flex items-center gap-2 mb-4 text-slate-700 font-semibold border-b border-slate-100 pb-2">
                                        <BarChart3 className="w-5 h-5 text-indigo-600" />
                                        <h2 className="text-lg">Vuelos por Origen</h2>
                                    </div>
                                    <FlightsTreemap filters={currentFilters} />
                                </div>

                                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-100">
                                    <div className="flex items-center gap-2 mb-4 text-slate-700 font-semibold border-b border-slate-100 pb-2">
                                        <BarChart3 className="w-5 h-5 text-indigo-600" />
                                        <h2 className="text-lg">Vuelos por Destino</h2>
                                    </div>
                                    <DestinationsTreemap filters={currentFilters} />
                                </div>
                            </div>

                            {/* Second Row: Regions Treemap (Full Width) */}
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-150">
                                <div className="flex items-center gap-2 mb-4 text-slate-700 font-semibold border-b border-slate-100 pb-2">
                                    <BarChart3 className="w-5 h-5 text-indigo-600" />
                                    <h2 className="text-lg">Distribución Geográfica: Regiones y Origen</h2>
                                </div>
                                <RegionsTreemap filters={currentFilters} />
                            </div>

                            {/* Third Row: Regions Destination Treemap (Full Width) */}
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-200">
                                <div className="flex items-center gap-2 mb-4 text-slate-700 font-semibold border-b border-slate-100 pb-2">
                                    <BarChart3 className="w-5 h-5 text-indigo-600" />
                                    <h2 className="text-lg">Distribución Geográfica: Regiones y Destino</h2>
                                </div>
                                <RegionsTreemap filters={currentFilters} endpoint="/stats/flights-by-region-destination" />
                            </div>

                            {/* Fourth Row: Type (1/3) and Company (2/3) */}
                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                                <div className="lg:col-span-1 bg-white p-6 rounded-xl shadow-sm border border-slate-100 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-200">
                                    <div className="flex items-center gap-2 mb-4 text-slate-700 font-semibold border-b border-slate-100 pb-2">
                                        <BarChart3 className="w-5 h-5 text-indigo-600" />
                                        <h2 className="text-lg">Tipo de Vuelo</h2>
                                    </div>
                                    <FlightTypeChart filters={currentFilters} />
                                </div>

                                <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-slate-100 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-300">
                                    <div className="flex items-center gap-2 mb-4 text-slate-700 font-semibold border-b border-slate-100 pb-2">
                                        <BarChart3 className="w-5 h-5 text-indigo-600" />
                                        <h2 className="text-lg">Vuelos por Empresa</h2>
                                    </div>
                                    <CompanyBarChart filters={currentFilters} />
                                </div>
                            </div>

                            {/* Third Row: Time Evolution (Full Width) */}
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-400">
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
                                <div className="">
                                    <FlightsYearChart filters={currentFilters} />
                                </div>
                            </div>

                            {/* Fourth Row: Peak Hours Heatmap (Full Width) */}
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-500">
                                <div className="flex items-center gap-2 mb-4 text-slate-700 font-semibold border-b border-slate-100 pb-2">
                                    <BarChart3 className="w-5 h-5 text-indigo-600" />
                                    <h2 className="text-lg">Mapa de Calor: Horas Salida y Días de Semana</h2>
                                </div>
                                <PeakHoursHeatmap filters={currentFilters} timeColumn="hora_salida" color="#6366f1" />
                            </div>

                            {/* Fifth Row: Arrival Peak Hours Heatmap (Full Width) */}
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-600">
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

                {/* Sidebar (Filters) */}
                <div className="lg:col-span-3 space-y-6 order-1 lg:order-2">
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 sticky top-4">
                        <div className="flex items-center gap-2 mb-4 text-slate-700 font-semibold border-b border-slate-100 pb-2">
                            <Filter className="w-5 h-5 text-slate-500" />
                            <h2>Filtros</h2>
                        </div>

                        <div className="space-y-4">
                            {/* Date Range Filters */}
                            <div className="space-y-1">
                                <label className="block text-sm font-medium text-slate-700">Fecha/Hora Desde (24h)</label>
                                <input
                                    type="datetime-local"
                                    step="1"
                                    value={startDate}
                                    onChange={(e) => setStartDate(e.target.value)}
                                    className="block w-full px-3 py-2 border border-slate-300 rounded-md leading-5 bg-white placeholder-slate-400 focus:outline-none focus:placeholder-slate-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 sm:text-sm transition duration-150 ease-in-out"
                                />
                            </div>
                            <div className="space-y-1">
                                <label className="block text-sm font-medium text-slate-700">Fecha/Hora Hasta (24h)</label>
                                <input
                                    type="datetime-local"
                                    step="1"
                                    value={endDate}
                                    onChange={(e) => setEndDate(e.target.value)}
                                    className="block w-full px-3 py-2 border border-slate-300 rounded-md leading-5 bg-white placeholder-slate-400 focus:outline-none focus:placeholder-slate-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 sm:text-sm transition duration-150 ease-in-out"
                                />
                            </div>

                            {/* Level Range Filters */}
                            <div className="grid grid-cols-2 gap-2">
                                <div className="space-y-1">
                                    <label className="block text-sm font-medium text-slate-700">Nivel Desde</label>
                                    <input
                                        type="number"
                                        placeholder="Ej: 100"
                                        value={minLevel}
                                        onChange={(e) => setMinLevel(e.target.value)}
                                        className="block w-full px-3 py-2 border border-slate-300 rounded-md leading-5 bg-white placeholder-slate-400 focus:outline-none focus:placeholder-slate-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 sm:text-sm transition duration-150 ease-in-out"
                                    />
                                </div>
                                <div className="space-y-1">
                                    <label className="block text-sm font-medium text-slate-700">Nivel Hasta</label>
                                    <input
                                        type="number"
                                        placeholder="Ej: 400"
                                        value={maxLevel}
                                        onChange={(e) => setMaxLevel(e.target.value)}
                                        className="block w-full px-3 py-2 border border-slate-300 rounded-md leading-5 bg-white placeholder-slate-400 focus:outline-none focus:placeholder-slate-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 sm:text-sm transition duration-150 ease-in-out"
                                    />
                                </div>
                            </div>


                        </div>



                        <hr className="border-slate-100" />

                        {/* Airport Filters */}
                        <div className="space-y-4">
                            <MultiSelectLookup
                                label="Origen"
                                placeholder="Buscar aeropuerto..."
                                value={selectedOrigins}
                                onChange={setSelectedOrigins}
                                fetchOptions={fetchAirportOptions}
                            />
                            <MultiSelectLookup
                                label="Destino"
                                placeholder="Buscar aeropuerto..."
                                value={selectedDestinations}
                                onChange={setSelectedDestinations}
                                fetchOptions={fetchAirportOptions}
                            />
                        </div>

                        <hr className="border-slate-100" />

                        {/* Dynamic Filters */}
                        <div className="space-y-4">
                            <MultiSelectLookup
                                label="Matrícula"
                                placeholder="Buscar matrícula..."
                                value={selectedMetricula}
                                onChange={setSelectedMatricula}
                                fetchOptions={createFilterFetcher(1)}
                            />

                            <MultiSelectLookup
                                label="Tipo de Aeronave"
                                placeholder="Buscar tipo..."
                                value={selectedTipoAeronave}
                                onChange={setSelectedTipoAeronave}
                                fetchOptions={createFilterFetcher(2)}
                            />

                            <MultiSelectLookup
                                label="Empresa"
                                placeholder="Buscar empresa..."
                                value={selectedEmpresa}
                                onChange={setSelectedEmpresa}
                                fetchOptions={createFilterFetcher(3)}
                            />

                            <MultiSelectLookup
                                label="Tipo de Vuelo"
                                placeholder="Buscar tipo..."
                                value={selectedTipoVuelo}
                                onChange={setSelectedTipoVuelo}
                                fetchOptions={createFilterFetcher(4)}
                            />

                            <MultiSelectLookup
                                label="Callsign"
                                placeholder="Buscar callsign..."
                                value={selectedCallsign}
                                onChange={setSelectedCallsign}
                                fetchOptions={createFilterFetcher(5)}
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
