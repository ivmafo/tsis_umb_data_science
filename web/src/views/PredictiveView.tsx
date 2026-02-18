import React, { useState, useEffect } from 'react';
import DailyDemandChart from '../components/DailyDemandChart';
import { PeakHoursHeatmap } from '../components/PeakHoursHeatmap';
import AirlineGrowthChart from '../components/AirlineGrowthChart';
import SectorSaturationChart from '../components/SectorSaturationChart';
import SeasonalTrendChart from '../components/SeasonalTrendChart';
import { api, type PredictiveFilters } from '../api';

const PredictiveView: React.FC = () => {
    const [activeTab, setActiveTab] = useState<'demand' | 'heatmap' | 'growth' | 'saturation' | 'seasonal'>('demand');

    // Filters State (Inputs)
    const [sectors, setSectors] = useState<any[]>([]);
    const [selectedSectorId, setSelectedSectorId] = useState<string>('');
    const [selectedAirport, setSelectedAirport] = useState<string>('');
    const [selectedRoute, setSelectedRoute] = useState<string>('');
    const [minLevel, setMinLevel] = useState<number | ''>('');
    const [maxLevel, setMaxLevel] = useState<number | ''>('');
    const [startDate, setStartDate] = useState<string>('');
    const [endDate, setEndDate] = useState<string>('');


    // Execution State (Trigger)
    const [appliedFilters, setAppliedFilters] = useState<PredictiveFilters | null>(null);

    // Derived Options based on selected sector
    const [availableAirports, setAvailableAirports] = useState<string[]>([]);
    const [availableRoutes, setAvailableRoutes] = useState<string[]>([]);

    const [loadingSectors, setLoadingSectors] = useState(false);

    useEffect(() => {
        fetchSectors();
    }, []);

    useEffect(() => {
        if (selectedSectorId) {
            const sector = sectors.find(s => s.id === selectedSectorId);
            if (sector && sector.definition) {
                const origins = sector.definition.origins || [];
                const destinations = sector.definition.destinations || [];
                const allAirports = Array.from(new Set([...origins, ...destinations])).sort();
                setAvailableAirports(allAirports);

                // Generate possible routes from origins to destinations
                const routes: string[] = [];
                origins.forEach((org: string) => {
                    destinations.forEach((dst: string) => {
                        if (org !== dst) {
                            routes.push(`${org}-${dst}`);
                        }
                    });
                });
                setAvailableRoutes(routes.sort());
            } else {
                setAvailableAirports([]);
                setAvailableRoutes([]);
            }
        } else {
            setAvailableAirports([]);
            setAvailableRoutes([]);
        }
    }, [selectedSectorId, sectors]);

    const fetchSectors = async () => {
        try {
            setLoadingSectors(true);
            const response = await api.get('/sectors/');
            setSectors(response.data);
            setLoadingSectors(false);
        } catch (error) {
            console.error("Error fetching sectors", error);
            setLoadingSectors(false);
        }
    };

    const handleGenerate = () => {
        const filters: PredictiveFilters = {
            sector_id: selectedSectorId || undefined,
            airport: selectedAirport || undefined,
            route: selectedRoute || undefined,
            min_level: minLevel === '' ? undefined : Number(minLevel),
            max_level: maxLevel === '' ? undefined : Number(maxLevel),
            start_date: startDate || undefined,
            end_date: endDate || undefined
        };
        setAppliedFilters(filters);
    };

    const handleClear = () => {
        setSelectedSectorId('');
        setSelectedAirport('');
        setSelectedRoute('');
        setMinLevel('');
        setMaxLevel('');
        setAppliedFilters(null);
        setStartDate('');
        setEndDate('');
    };

    return (
        <div className="p-6 bg-slate-50 min-h-screen">
            <div className="mb-6">
                <h1 className="text-3xl font-bold text-slate-900">Análisis Predictivo</h1>
                <p className="text-slate-500">Modelos de Machine Learning y Estadística para proyecciones futuras.</p>
            </div>

            {/* Global Filters Area */}
            <div className="bg-white p-6 rounded-xl shadow-md border border-slate-200 mb-8">
                <div className="flex flex-col gap-4">
                    <div className="flex flex-col md:flex-row gap-4">
                        {/* Sector Selector */}
                        <div className="flex-1">
                            <label className="block text-xs font-bold text-slate-600 uppercase mb-1">
                                Sector <span className="text-red-500">*</span> {loadingSectors && <span className="text-indigo-500 text-[10px] lowercase">(cargando...)</span>}
                            </label>
                            <select
                                value={selectedSectorId}
                                onChange={(e) => {
                                    setSelectedSectorId(e.target.value);
                                    setSelectedAirport('');
                                    setSelectedRoute('');
                                }}
                                disabled={loadingSectors}
                                className="w-full border border-slate-300 rounded px-3 py-2 bg-slate-50 focus:ring-2 focus:ring-indigo-500 outline-none transition-colors disabled:opacity-50 font-medium"
                            >
                                <option value="">-- Seleccione un Sector --</option>
                                {sectors.map(s => (
                                    <option key={s.id} value={s.id}>{s.name}</option>
                                ))}
                            </select>
                        </div>

                        {/* Airport Selector */}
                        <div className="flex-1">
                            <label className="block text-xs font-bold text-slate-600 uppercase mb-1">Aeropuerto (Opcional)</label>
                            <select
                                value={selectedAirport}
                                onChange={(e) => setSelectedAirport(e.target.value)}
                                disabled={!selectedSectorId}
                                className="w-full border border-slate-300 rounded px-3 py-2 bg-slate-50 focus:ring-2 focus:ring-indigo-500 outline-none disabled:opacity-50 transition-colors"
                            >
                                <option value="">-- Todos --</option>
                                {availableAirports.map(code => (
                                    <option key={code} value={code}>{code}</option>
                                ))}
                            </select>
                        </div>

                        {/* Route Selector */}
                        <div className="flex-1">
                            <label className="block text-xs font-bold text-slate-600 uppercase mb-1">Ruta (Opcional)</label>
                            <select
                                value={selectedRoute}
                                onChange={(e) => setSelectedRoute(e.target.value)}
                                disabled={!selectedSectorId}
                                className="w-full border border-slate-300 rounded px-3 py-2 bg-slate-50 focus:ring-2 focus:ring-indigo-500 outline-none disabled:opacity-50 transition-colors"
                            >
                                <option value="">-- Todas --</option>
                                {availableRoutes.map(r => (
                                    <option key={r} value={r}>{r}</option>
                                ))}
                            </select>
                        </div>

                        {/* Level Range */}
                        <div className="flex-1 flex gap-2">
                            <div className="flex-1">
                                <label className="block text-xs font-bold text-slate-600 uppercase mb-1">Nivel Min</label>
                                <input
                                    type="number"
                                    value={minLevel}
                                    onChange={(e) => setMinLevel(e.target.value === '' ? '' : Number(e.target.value))}
                                    placeholder="0"
                                    className="w-full border border-slate-300 rounded px-3 py-2 bg-slate-50 focus:ring-2 focus:ring-indigo-500 outline-none transition-colors"
                                />
                            </div>
                            <div className="flex-1">
                                <label className="block text-xs font-bold text-slate-600 uppercase mb-1">Nivel Max</label>
                                <input
                                    type="number"
                                    value={maxLevel}
                                    onChange={(e) => setMaxLevel(e.target.value === '' ? '' : Number(e.target.value))}
                                    placeholder="999"
                                    className="w-full border border-slate-300 rounded px-3 py-2 bg-slate-50 focus:ring-2 focus:ring-indigo-500 outline-none transition-colors"
                                />
                            </div>
                        </div>

                        {/* Date Range */}
                        <div className="flex-1 flex gap-2">
                            <div className="flex-1">
                                <label className="block text-xs font-bold text-slate-600 uppercase mb-1">Fecha Desde</label>
                                <input
                                    type="date"
                                    value={startDate}
                                    onChange={(e) => setStartDate(e.target.value)}
                                    className="w-full border border-slate-300 rounded px-3 py-2 bg-slate-50 focus:ring-2 focus:ring-indigo-500 outline-none transition-colors"
                                />
                            </div>
                            <div className="flex-1">
                                <label className="block text-xs font-bold text-slate-600 uppercase mb-1">Fecha Hasta</label>
                                <input
                                    type="date"
                                    value={endDate}
                                    onChange={(e) => setEndDate(e.target.value)}
                                    className="w-full border border-slate-300 rounded px-3 py-2 bg-slate-50 focus:ring-2 focus:ring-indigo-500 outline-none transition-colors"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="flex justify-end gap-3 mt-2">
                        <button
                            onClick={handleClear}
                            className="px-4 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
                        >
                            Limpiar Filtros
                        </button>
                        <button
                            onClick={handleGenerate}
                            disabled={!selectedSectorId}
                            className="px-6 py-2 text-sm font-bold text-white bg-indigo-600 rounded-lg shadow hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                            Generar Predicción
                        </button>
                    </div>
                </div>
            </div>

            {/* Navigation Tabs */}
            <div className="flex space-x-1 rounded-xl bg-slate-200 p-1 mb-6 w-fit">
                {[
                    { id: 'demand', label: 'Demanda Diaria' },
                    { id: 'heatmap', label: 'Picos de Hora' },
                    { id: 'growth', label: 'Crecimiento Aerolíneas' },
                    { id: 'saturation', label: 'Saturación Sectores' },
                    { id: 'seasonal', label: 'Predicción Estacional' },
                ].map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id as any)}
                        className={`
                            px-4 py-2 text-sm font-medium rounded-lg transition-all
                            ${activeTab === tab.id
                                ? 'bg-white text-indigo-700 shadow-sm'
                                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-300/50'}
                        `}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Content Area */}
            {!appliedFilters ? (
                <div className="flex flex-col items-center justify-center h-64 bg-white rounded-xl border-2 border-dashed border-slate-300">
                    <div className="text-slate-400 mb-2">
                        <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                    </div>
                    <p className="text-lg font-medium text-slate-500">Esperando parámetros...</p>
                    <p className="text-sm text-slate-400 mt-1">Seleccione un Sector y haga clic en <strong>Generar Predicción</strong></p>
                </div>
            ) : (
                <div className="space-y-6 animate-in fade-in duration-500">
                    {activeTab === 'demand' && (
                        <div>
                            <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4 rounded-r shadow-sm flex justify-between items-center">
                                <div>
                                    <p className="text-blue-800 font-medium">Proyección a 30 días</p>
                                    <p className="text-blue-600 text-sm">
                                        Filtros: Sector <strong>{sectors.find(s => s.id === appliedFilters.sector_id)?.name}</strong>
                                        {appliedFilters.airport && `, Aeropuerto ${appliedFilters.airport}`}
                                        {appliedFilters.route && `, Ruta ${appliedFilters.route}`}
                                    </p>
                                </div>
                            </div>
                            <DailyDemandChart filters={appliedFilters} />
                        </div>
                    )}

                    {activeTab === 'heatmap' && (
                        <div>
                            <div className="bg-indigo-50 border-l-4 border-indigo-500 p-4 mb-4 rounded-r shadow-sm">
                                <p className="text-indigo-700">
                                    <strong>Semana Típica Futura:</strong> Mapa de calor de congestión horaria.
                                </p>
                            </div>
                            <PeakHoursHeatmap filters={appliedFilters} isPredictive={true} />
                        </div>
                    )}

                    {activeTab === 'growth' && (
                        <div>
                            <div className="bg-green-50 border-l-4 border-green-500 p-4 mb-4 rounded-r shadow-sm">
                                <p className="text-green-700">
                                    <strong>Tendencias de Mercado:</strong> Crecimiento de aerolíneas.
                                </p>
                            </div>
                            <AirlineGrowthChart filters={appliedFilters} />
                        </div>
                    )}

                    {activeTab === 'saturation' && (
                        <div>
                            <div className="bg-amber-50 border-l-4 border-amber-500 p-4 mb-4 rounded-r shadow-sm">
                                <p className="text-amber-700">
                                    <strong>Saturación de Capacidad ATC:</strong> Demanda vs Capacidad.
                                </p>
                            </div>
                            {appliedFilters.sector_id ? (
                                <SectorSaturationChart filters={appliedFilters} />
                            ) : (
                                <div className="p-4 bg-red-50 text-red-600 rounded">Error: Sector ID missing.</div>
                            )}
                        </div>
                    )}

                    {activeTab === 'seasonal' && (
                        <div>
                            <div className="bg-purple-50 border-l-4 border-purple-500 p-4 mb-4 rounded-r shadow-sm">
                                <p className="text-purple-700">
                                    <strong>Tendencia Estacional de Largo Plazo:</strong> Análisis histórico y proyección futura con descomposición de Fourier.
                                </p>
                            </div>
                            <SeasonalTrendChart filters={appliedFilters} />
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default PredictiveView;
