
import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { Calculator, AlertTriangle, ClipboardCheck } from 'lucide-react';

interface Sector {
    id: string;
    name: string;
}

export interface UncertaintyRange {
    lower: number;
    upper: number;
}

export interface StochasticCapacityReport {
    nominal_theoretical_capacity: number;
    ashford_baseline_capacity: number;
    stochastic_simulated_capacity: number;
    uncertainty_range: UncertaintyRange;
    applied_utilization_factor: number;
    status: string;
}

export interface PhysicistMetrics {
    dynamic_tfc: number;
    dynamic_rot: number;
    bottleneck_source: string;
}

export interface LegacyNominalComparison {
    ch_theoretical: number;
    ch_adjusted: number;
    tps_seconds: number;
    scv_aircraft: number;
    total_flights_analyzed: number;
    r_factor: number;
    tfc_breakdown: any;
}

interface CapacityResult {
    sector_name: string;
    physicist_metrics: PhysicistMetrics;
    stochastic_capacity_report: StochasticCapacityReport;
    legacy_nominal_comparison: LegacyNominalComparison;
    formula_used?: string;
}

/**
 * Vista de Reporte de Capacidad ATC.
 * Implementa la metodología de cálculo de capacidad basada en la Circular 006 (SCV / DORATASK).
 * Permite seleccionar un sector y un rango de fechas para calcular métricas como TPS, TFC, SCV y CH.
 */
/**
 * Vista de Reporte de Capacidad ATC.
 * 
 * Este componente implementa la lógica de negocio para la determinación de la 
 * Capacidad de Sectores Aeronáuticos siguiendo la metodología técnica de la 
 * Circular 006 (SCV / DORATASK).
 * 
 * Atributos Técnicos:
 * - Análisis Estadístico: Calcula el TPS (Tiempo Promedio en Sector) mediante
 *   agregación de trayectorias históricas en DuckDB.
 * - Integración de TFC: Combina tiempos de trabajo manuales (Transferencia, 
 *   Comunicaciones, etc.) con datos automáticos.
 * - Modelado Matemático: Calcula la Capacidad Simultánea (SCV) y deriva la 
 *   Capacidad Horaria (CH) teórica y ajustada por factor de carga R.
 */
const CapacityReportView: React.FC = () => {
    // ESTADOS: Diccionario de sectores y puntero de selección activa
    const [sectors, setSectors] = useState<Sector[]>([]);
    const [selectedSector, setSelectedSector] = useState<string>('');

    // DIMENSIONES: Acotamiento temporal para la muestra de vuelos a analizar
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');

    // RESULTADOS: Objeto de métricas calculado por el motor de inferencia del backend
    const [result, setResult] = useState<CapacityResult | null>(null);

    // CONTROL: Semáforos de proceso y feedback de errores
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    /**
     * Sincroniza el catálogo de sectores maestros al inicio.
     */
    useEffect(() => {
        api.get('/sectors/')
            .then(res => setSectors(res.data))
            .catch(err => console.error("Fallo al recuperar catálogo de sectores:", err));
    }, []);

    /**
     * Motor de Cálculo de Capacidad.
     * Invoca el procedimiento almacenado/servicio de cálculo en el backend,
     * enviando el ID del sector y el rango de fechas para el procesamiento de trayectorias.
     */
    const handleCalculate = async () => {
        if (!selectedSector) return;
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            // Transacción: Cálculo de indicadores basados en Circular 006
            const res = await api.post(`/sectors/${selectedSector}/calculate`, {
                start_date: startDate,
                end_date: endDate
            });

            // Si el backend devuelve status 200 pero reporta un error lógico (ej: sin vuelos)
            if (res.data && res.data.error) {
                setError(res.data.error);
                setResult(null);
            } else {
                setResult(res.data);
            }
        } catch (err: any) {
            console.error("Fallo técnico en motor de capacidad:", err);
            setError(err.response?.data?.detail || "Error en el cálculo. Verifique la existencia de vuelos en el rango seleccionado.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-6 bg-slate-50 min-h-screen">
            {/* ENCABEZADO DE LA VISTA */}
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Calculadora de Capacidad ATC</h1>
            <p className="text-slate-500 mb-8">Metodología Circular 006 (SCV / DORATASK)</p>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* PANEL DE CONTROL: PARÁMETROS DE CÁLCULO */}
                <div className="lg:col-span-1 bg-white p-6 rounded-xl shadow-sm border border-slate-200 h-fit">
                    <h2 className="font-bold text-lg text-slate-800 mb-4 flex items-center gap-2">
                        <Calculator className="w-5 h-5 text-indigo-600" />
                        Parámetros de Cálculo
                    </h2>

                    <div className="space-y-4">
                        {/* Selección del Sector Aeronáutico */}
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Seleccionar Sector</label>
                            <select
                                value={selectedSector}
                                onChange={e => setSelectedSector(e.target.value)}
                                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                            >
                                <option value="">-- Seleccione un Sector --</option>
                                {sectors.map(s => (
                                    <option key={s.id} value={s.id}>{s.name}</option>
                                ))}
                            </select>
                        </div>

                        {/* Rango de Fechas para la muestra estadística */}
                        <div className="grid grid-cols-2 gap-2">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Fecha Inicio</label>
                                <input
                                    type="date"
                                    value={startDate}
                                    onChange={e => setStartDate(e.target.value)}
                                    className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-indigo-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Fecha Fin</label>
                                <input
                                    type="date"
                                    value={endDate}
                                    onChange={e => setEndDate(e.target.value)}
                                    className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-indigo-500"
                                />
                            </div>
                        </div>

                        {/* Botón de Acción Principal */}
                        <button
                            onClick={handleCalculate}
                            disabled={!selectedSector || loading}
                            className={`w-full py-3 rounded-lg font-bold text-white shadow-md transition-all flex justify-center items-center gap-2
                                ${!selectedSector || loading ? 'bg-slate-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 hover:shadow-lg'}
                            `}
                        >
                            {loading ? 'Calculando...' : 'Calcular Capacidad'}
                        </button>

                        {/* Manejo de Errores en UI */}
                        {error && (
                            <div className="p-3 bg-red-50 text-red-700 text-sm rounded-lg border border-red-100 flex items-start gap-2">
                                <AlertTriangle className="w-5 h-5 shrink-0" />
                                <span>{error}</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* PANEL DE RESULTADOS Y ANÁLISIS DETALLADO */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Placeholder cuando no hay resultados cargados */}
                    {!result && !loading && (
                        <div className="bg-white p-12 rounded-xl shadow-sm border border-slate-200 text-center text-slate-400 flex flex-col items-center">
                            <ClipboardCheck className="w-16 h-16 mb-4 text-slate-300" />
                            <p className="text-lg">Seleccione un sector y rango de fechas para ver el análisis de capacidad.</p>
                        </div>
                    )}

                    {/* Visualización de Resultados */}
                    {result && (
                        <>
                            {/* KPIs PRINCIPALES: CH y SCV */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {/* Capacidad Horaria Ajustada */}
                                <div className="bg-indigo-600 p-6 rounded-xl shadow-lg text-white relative overflow-hidden">
                                    <div className="absolute top-0 right-0 p-4 opacity-10">
                                        <Calculator className="w-24 h-24" />
                                    </div>
                                    <h3 className="text-indigo-100 text-sm font-medium uppercase tracking-wider">Capacidad Estocástica RAC 14</h3>
                                    <div className="flex items-baseline gap-2 mt-1">
                                        <span className="text-5xl font-bold">{Math.round(result.stochastic_capacity_report.stochastic_simulated_capacity)}</span>
                                        <span className="text-xl text-indigo-200">vuelos/hora</span>
                                    </div>
                                    <p className="mt-2 text-indigo-200 text-sm">
                                        Rango 95%: {Math.round(result.stochastic_capacity_report.uncertainty_range.lower)} - {Math.round(result.stochastic_capacity_report.uncertainty_range.upper)}
                                    </p>
                                </div>

                                {/* Capacidad Analítica */}
                                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col justify-center">
                                    <h3 className="text-slate-500 text-sm font-bold uppercase tracking-wider">Capacidad Nominal (CH)</h3>
                                    <div className="flex items-baseline gap-2 mt-1">
                                        <span className="text-4xl font-bold text-slate-900">{result.legacy_nominal_comparison.ch_adjusted}</span>
                                        <span className="text-lg text-slate-500">vuelos/hora</span>
                                    </div>
                                    <p className="mt-2 text-slate-400 text-xs">
                                        Cálculo heredado determinista con factor R={result.legacy_nominal_comparison.r_factor}.
                                    </p>
                                </div>
                            </div>

                            {/* DESGLOSE DETALLADO DEL CÁLCULO */}
                            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                                <div className="px-6 py-4 border-b border-slate-100 bg-slate-50">
                                    <h3 className="font-bold text-slate-800">Desglose de Cálculo (Metodología Circular 006)</h3>
                                </div>
                                <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">

                                    {/* Componente: Datos Automáticos (Análisis Estadístico) */}
                                    <div>
                                        <h4 className="text-sm font-bold text-indigo-600 mb-3 border-b border-indigo-100 pb-1">Automático (Datos Históricos)</h4>
                                        <div className="space-y-4">
                                            <div>
                                                <div className="flex justify-between text-sm mb-1">
                                                    <span className="text-slate-600">TPS (Tiempo Promedio en Sector)</span>
                                                    <span className="font-bold text-slate-900">{result.legacy_nominal_comparison.tps_seconds.toFixed(1)} seg</span>
                                                </div>
                                                <div className="w-full bg-slate-100 rounded-full h-2">
                                                    <div className="bg-indigo-500 h-2 rounded-full" style={{ width: '100%' }}></div>
                                                </div>
                                            </div>
                                            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                                                <div className="text-xs text-slate-500">Vuelos Analizados</div>
                                                <div className="text-xl font-bold text-slate-800">{result.legacy_nominal_comparison.total_flights_analyzed}</div>
                                                {result.legacy_nominal_comparison.total_flights_analyzed < 30 && (
                                                    <div className="mt-2 text-xs text-amber-600 font-medium flex items-center gap-1">
                                                        <AlertTriangle className="w-3 h-3" />
                                                        Muestra pequeña ({'<'}30), baja confianza estadística.
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Componente: TFC Dinámico (Tiempo de Trabajo del Controlador RAC 14) */}
                                    <div>
                                        <h4 className="text-sm font-bold text-emerald-600 mb-3 border-b border-emerald-100 pb-1">Modelado Físico (Agentes RAC 14)</h4>
                                        <div className="space-y-2">
                                            <div className="flex justify-between items-center text-sm">
                                                <span className="text-slate-600">Tiempo ROT Limitante</span>
                                                <span className="font-mono text-slate-800 bg-slate-100 px-2 py-0.5 rounded">{result.physicist_metrics.dynamic_rot.toFixed(1)}s</span>
                                            </div>
                                            <div className="flex justify-between items-center text-sm">
                                                <span className="text-slate-600">Cuello de Botella</span>
                                                <span className="font-mono text-slate-800 bg-slate-100 px-2 py-0.5 rounded uppercase">{result.physicist_metrics.bottleneck_source}</span>
                                            </div>
                                            <div className="mt-2 pt-2 border-t border-slate-100 flex justify-between items-center font-bold">
                                                <span className="text-slate-800">TFC Dinámico Final</span>
                                                <span className="text-emerald-600">{result.physicist_metrics.dynamic_tfc.toFixed(1)}s</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 text-xs text-slate-400 font-mono">
                                    Fórmula: RAC 14 Estocástico + Factor Ashford {result.stochastic_capacity_report.applied_utilization_factor}
                                </div>
                            </div>

                            {/* SECCIÓN EDUCATIVA: EXPLICACIÓN DE FÓRMULAS */}
                            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden mt-6">
                                <div className="px-6 py-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
                                    <ClipboardCheck className="w-5 h-5 text-indigo-600" />
                                    <h3 className="font-bold text-slate-800">Información Detallada del Cálculo</h3>
                                </div>
                                <div className="p-6 space-y-6">

                                    {/* Explicación CH */}
                                    <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-start border-b border-slate-100 pb-6">
                                        <div className="md:col-span-4">
                                            <h4 className="font-bold text-indigo-700 text-sm uppercase tracking-wider mb-1">Capacidad Estocástica (RAC 14)</h4>
                                            <p className="text-xs text-slate-500">Volumen máximo de tránsito aéreo con penalización por varianza e infraestructura.</p>
                                        </div>
                                        <div className="md:col-span-8 bg-slate-50 p-4 rounded-lg font-mono text-xs text-slate-700">
                                            <div className="flex flex-col gap-2">
                                                <div className="flex items-center gap-2">
                                                    <span className="font-bold">Fórmula de Demanda (Ashford):</span>
                                                    <code className="bg-white px-2 py-1 rounded border border-slate-200">Capacidad * Factor({result.stochastic_capacity_report.applied_utilization_factor})</code>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <span className="font-bold">Cálculo Estocástico (Montecarlo):</span>
                                                    <span><strong>{result.stochastic_capacity_report.stochastic_simulated_capacity.toFixed(0)}</strong> vuelos/hora seguros al 95%.</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Explicación SCV */}
                                    <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-start border-b border-slate-100 pb-6">
                                        <div className="md:col-span-4">
                                            <h4 className="font-bold text-slate-700 text-sm uppercase tracking-wider mb-1">Cálculo Nominal (Legacy 006)</h4>
                                            <p className="text-xs text-slate-500">Método de la Circular 006 para Capacidad Simultánea y Horaria Teórica.</p>
                                        </div>
                                        <div className="md:col-span-8 bg-slate-50 p-4 rounded-lg font-mono text-xs text-slate-700">
                                            <div className="flex flex-col gap-2">
                                                <div className="flex items-center gap-2">
                                                    <span className="font-bold">SCV Lógico:</span>
                                                    <span>{result.legacy_nominal_comparison.tps_seconds.toFixed(1)} / (TFC * 1.3) = <strong>{result.legacy_nominal_comparison.scv_aircraft}</strong> aeronaves</span>
                                                </div>
                                                <div className="mt-1 text-slate-500 italic">
                                                    * Se obtuvo un Factor R de {result.legacy_nominal_comparison.r_factor} que derivó en una capacidad tradicional de {result.legacy_nominal_comparison.ch_adjusted} vuelos/hora.
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Explicación de Datos Automáticos */}
                                    <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-start">
                                        <div className="md:col-span-4">
                                            <h4 className="font-bold text-slate-700 text-sm uppercase tracking-wider mb-1">TFC Dinámico (El Físico)</h4>
                                            <p className="text-xs text-slate-500">Agente físico que evalúa asimetría vertical y penalizaciones RAC 14.</p>
                                        </div>
                                        <div className="md:col-span-8 bg-slate-50 p-4 rounded-lg font-mono text-xs text-slate-700">
                                            <div className="flex flex-col gap-2">
                                                <div>
                                                    <span className="font-bold block mb-1">Análisis de Limitante (Cuello de Botella):</span>
                                                    <p className="text-slate-600 mb-1">El valor del TFC Dinámico fue establecido en <strong>{result.physicist_metrics.dynamic_tfc.toFixed(1)}s</strong> determinado que la dependencia mayor es: {result.physicist_metrics.bottleneck_source.toUpperCase()}.</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                </div>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

export default CapacityReportView;
