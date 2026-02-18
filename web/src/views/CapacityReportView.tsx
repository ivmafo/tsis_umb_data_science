
import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { Calculator, AlertTriangle, ClipboardCheck } from 'lucide-react';

interface Sector {
    id: string;
    name: string;
}

interface CapacityResult {
    sector_name: string;
    TPS: number;
    TFC_Total: number;
    TFC_Breakdown: {
        t_transfer: number;
        t_comm_ag: number;
        t_separation: number;
        t_coordination: number;
    };
    SCV: number;
    CH_Theoretical: number;
    CH_Adjusted: number;
    R_Factor: number;
    total_flights_analyzed: number;
    formula_used: string;
}

const CapacityReportView: React.FC = () => {
    const [sectors, setSectors] = useState<Sector[]>([]);
    const [selectedSector, setSelectedSector] = useState<string>('');
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [result, setResult] = useState<CapacityResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        api.get('/sectors/').then(res => setSectors(res.data)).catch(console.error);
    }, []);

    const handleCalculate = async () => {
        if (!selectedSector) return;
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const res = await api.post(`/sectors/${selectedSector}/calculate`, {
                start_date: startDate,
                end_date: endDate
            });
            setResult(res.data);
        } catch (err: any) {
            console.error("Calculation error", err);
            setError(err.response?.data?.detail || "Error al calcular la capacidad. Verifique los datos del sector.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-6 bg-slate-50 min-h-screen">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Calculadora de Capacidad ATC</h1>
            <p className="text-slate-500 mb-8">Metodología Circular 006 (SCV / DORATASK)</p>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Controls */}
                <div className="lg:col-span-1 bg-white p-6 rounded-xl shadow-sm border border-slate-200 h-fit">
                    <h2 className="font-bold text-lg text-slate-800 mb-4 flex items-center gap-2">
                        <Calculator className="w-5 h-5 text-indigo-600" />
                        Parámetros de Cálculo
                    </h2>

                    <div className="space-y-4">
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

                        <button
                            onClick={handleCalculate}
                            disabled={!selectedSector || loading}
                            className={`w-full py-3 rounded-lg font-bold text-white shadow-md transition-all flex justify-center items-center gap-2
                                ${!selectedSector || loading ? 'bg-slate-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 hover:shadow-lg'}
                            `}
                        >
                            {loading ? 'Calculando...' : 'Calcular Capacidad'}
                        </button>

                        {error && (
                            <div className="p-3 bg-red-50 text-red-700 text-sm rounded-lg border border-red-100 flex items-start gap-2">
                                <AlertTriangle className="w-5 h-5 shrink-0" />
                                <span>{error}</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* Results */}
                <div className="lg:col-span-2 space-y-6">
                    {!result && !loading && (
                        <div className="bg-white p-12 rounded-xl shadow-sm border border-slate-200 text-center text-slate-400 flex flex-col items-center">
                            <ClipboardCheck className="w-16 h-16 mb-4 text-slate-300" />
                            <p className="text-lg">Seleccione un sector y rango de fechas para ver el análisis de capacidad.</p>
                        </div>
                    )}

                    {result && (
                        <>
                            {/* Main KPIs */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="bg-indigo-600 p-6 rounded-xl shadow-lg text-white relative overflow-hidden">
                                    <div className="absolute top-0 right-0 p-4 opacity-10">
                                        <Calculator className="w-24 h-24" />
                                    </div>
                                    <h3 className="text-indigo-100 text-sm font-medium uppercase tracking-wider">Capacidad Horaria (CH)</h3>
                                    <div className="flex items-baseline gap-2 mt-1">
                                        <span className="text-5xl font-bold">{result.CH_Adjusted}</span>
                                        <span className="text-xl text-indigo-200">vuelos/hora</span>
                                    </div>
                                    <p className="mt-2 text-indigo-200 text-sm">
                                        Basado en factor R={result.R_Factor}
                                    </p>
                                </div>

                                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col justify-center">
                                    <h3 className="text-slate-500 text-sm font-bold uppercase tracking-wider">Capacidad Simultánea (SCV)</h3>
                                    <div className="flex items-baseline gap-2 mt-1">
                                        <span className="text-4xl font-bold text-slate-900">{result.SCV}</span>
                                        <span className="text-lg text-slate-500">aeronaves</span>
                                    </div>
                                    <p className="mt-2 text-slate-400 text-xs">
                                        Máximo número de aeronaves controladas simultáneamente de forma segura.
                                    </p>
                                </div>
                            </div>

                            {/* Details Breakdown */}
                            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                                <div className="px-6 py-4 border-b border-slate-100 bg-slate-50">
                                    <h3 className="font-bold text-slate-800">Desglose de Cálculo (Metodología Circular 006)</h3>
                                </div>
                                <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
                                    {/* Automatic Data */}
                                    <div>
                                        <h4 className="text-sm font-bold text-indigo-600 mb-3 border-b border-indigo-100 pb-1">Automático (Datos Históricos)</h4>
                                        <div className="space-y-4">
                                            <div>
                                                <div className="flex justify-between text-sm mb-1">
                                                    <span className="text-slate-600">TPS (Tiempo Promedio en Sector)</span>
                                                    <span className="font-bold text-slate-900">{result.TPS.toFixed(1)} seg</span>
                                                </div>
                                                <div className="w-full bg-slate-100 rounded-full h-2">
                                                    <div className="bg-indigo-500 h-2 rounded-full" style={{ width: '100%' }}></div>
                                                </div>
                                            </div>
                                            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                                                <div className="text-xs text-slate-500">Vuelos Analizados</div>
                                                <div className="text-xl font-bold text-slate-800">{result.total_flights_analyzed}</div>
                                                {result.total_flights_analyzed < 30 && (
                                                    <div className="mt-2 text-xs text-amber-600 font-medium flex items-center gap-1">
                                                        <AlertTriangle className="w-3 h-3" />
                                                        Muestra pequeña ({'<'}30), baja confianza estadistica.
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Manual Data */}
                                    <div>
                                        <h4 className="text-sm font-bold text-emerald-600 mb-3 border-b border-emerald-100 pb-1">Manual (Parámetros TFC)</h4>
                                        <div className="space-y-2">
                                            {[
                                                { label: 'Transferencia', val: result.TFC_Breakdown.t_transfer },
                                                { label: 'Comms A/G', val: result.TFC_Breakdown.t_comm_ag },
                                                { label: 'Separación', val: result.TFC_Breakdown.t_separation },
                                                { label: 'Coordinación', val: result.TFC_Breakdown.t_coordination },
                                            ].map((item, idx) => (
                                                <div key={idx} className="flex justify-between items-center text-sm">
                                                    <span className="text-slate-600">{item.label}</span>
                                                    <span className="font-mono text-slate-800 bg-slate-100 px-2 py-0.5 rounded">{item.val}s</span>
                                                </div>
                                            ))}
                                            <div className="mt-2 pt-2 border-t border-slate-100 flex justify-between items-center font-bold">
                                                <span className="text-slate-800">Total TFC</span>
                                                <span className="text-emerald-600">{result.TFC_Total.toFixed(1)}s</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 text-xs text-slate-400 font-mono">
                                    Fórmula: {result.formula_used}
                                </div>
                            </div>

                            {/* Detailed Calculation Info */}
                            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden mt-6">
                                <div className="px-6 py-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
                                    <ClipboardCheck className="w-5 h-5 text-indigo-600" />
                                    <h3 className="font-bold text-slate-800">Información Detallada del Cálculo</h3>
                                </div>
                                <div className="p-6 space-y-6">

                                    {/* CH Explanation */}
                                    <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-start border-b border-slate-100 pb-6">
                                        <div className="md:col-span-4">
                                            <h4 className="font-bold text-indigo-700 text-sm uppercase tracking-wider mb-1">Capacidad Horaria (CH)</h4>
                                            <p className="text-xs text-slate-500">Volumen máximo de tránsito aéreo que puede ser gestionado en una hora.</p>
                                        </div>
                                        <div className="md:col-span-8 bg-slate-50 p-4 rounded-lg font-mono text-xs text-slate-700">
                                            <div className="flex flex-col gap-2">
                                                <div className="flex items-center gap-2">
                                                    <span className="font-bold">Fórmula:</span>
                                                    <code className="bg-white px-2 py-1 rounded border border-slate-200">CH = (3600 * SCV) / TPS</code>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <span className="font-bold">Cálculo:</span>
                                                    <span>(3600 * {result.SCV}) / {result.TPS.toFixed(1)} = <strong>{result.CH_Theoretical}</strong></span>
                                                </div>
                                                <div className="mt-1 text-slate-500 italic">
                                                    * Se ajusta posteriormente por el Factor R ({result.R_Factor}) para obtener el valor final: {result.CH_Theoretical} * {result.R_Factor} = <strong>{result.CH_Adjusted}</strong>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* SCV Explanation */}
                                    <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-start border-b border-slate-100 pb-6">
                                        <div className="md:col-span-4">
                                            <h4 className="font-bold text-slate-700 text-sm uppercase tracking-wider mb-1">Capacidad Simultánea (SCV)</h4>
                                            <p className="text-xs text-slate-500">Número máximo de aeronaves que se pueden gestionar simultáneamente bajo condiciones seguras.</p>
                                        </div>
                                        <div className="md:col-span-8 bg-slate-50 p-4 rounded-lg font-mono text-xs text-slate-700">
                                            <div className="flex flex-col gap-2">
                                                <div className="flex items-center gap-2">
                                                    <span className="font-bold">Fórmula:</span>
                                                    <code className="bg-white px-2 py-1 rounded border border-slate-200">SCV = TPS / (TFC * 1.3)</code>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <span className="font-bold">Cálculo:</span>
                                                    <span>{result.TPS.toFixed(1)} / ({result.TFC_Total.toFixed(1)} * 1.3) = <strong>{result.SCV}</strong></span>
                                                </div>
                                                <div className="mt-1 text-slate-500 italic">
                                                    * 1.3 es el factor de buffer de seguridad estándar.
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Automatic Data Explanation */}
                                    <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-start">
                                        <div className="md:col-span-4">
                                            <h4 className="font-bold text-slate-700 text-sm uppercase tracking-wider mb-1">Automático (Datos Históricos)</h4>
                                            <p className="text-xs text-slate-500">Datos extraídos automáticamente del análisis de vuelos históricos.</p>
                                        </div>
                                        <div className="md:col-span-8 bg-slate-50 p-4 rounded-lg font-mono text-xs text-slate-700">
                                            <div className="flex flex-col gap-2">
                                                <div>
                                                    <span className="font-bold block mb-1">TPS (Tiempo Promedio en Sector):</span>
                                                    <p className="text-slate-600 mb-1">Promedio de duración de vuelo dentro del sector para los <strong>{result.total_flights_analyzed}</strong> vuelos analizados.</p>
                                                    <code className="bg-white px-2 py-1 rounded border border-slate-200 block w-fit">AVG(duracion_vuelo)</code>
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
