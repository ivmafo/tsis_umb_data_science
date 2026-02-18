
import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { MultiSelectLookup } from '../components/MultiSelectLookup';
import { Plus, Pencil, Trash2, Check, X } from 'lucide-react';

interface Sector {
    id?: string;
    name: string;
    definition: {
        origins: string[];
        destinations: string[];
    };
    t_transfer: number;
    t_comm_ag: number;
    t_separation: number;
    t_coordination: number;
    adjustment_factor_r: number;
    capacity_baseline: number;
}

const SectorConfigurationView: React.FC = () => {
    const [sectors, setSectors] = useState<Sector[]>([]);
    const [loading, setLoading] = useState(true);
    const [editingSector, setEditingSector] = useState<Sector | null>(null);
    const [isCreating, setIsCreating] = useState(false);

    useEffect(() => {
        fetchSectors();
    }, []);

    const fetchSectors = async () => {
        try {
            const response = await api.get('/sectors/');
            setSectors(response.data);
            setLoading(false);
        } catch (error) {
            console.error("Error fetching sectors", error);
            setLoading(false);
        }
    };

    const handleSave = async () => {
        if (!editingSector) return;

        try {
            if (editingSector.id) {
                await api.put(`/sectors/${editingSector.id}`, editingSector);
            } else {
                await api.post('/sectors/', editingSector);
            }
            setEditingSector(null);
            setIsCreating(false);
            fetchSectors();
        } catch (error) {
            console.error("Error saving sector", error);
            alert("Error al guardar el sector");
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm("¿Está seguro de eliminar este sector?")) return;
        try {
            await api.delete(`/sectors/${id}`);
            fetchSectors();
        } catch (error) {
            console.error("Error deleting sector", error);
        }
    };

    const startEdit = (sector: Sector) => {
        setEditingSector({ ...sector });
        setIsCreating(false);
    };

    const startCreate = () => {
        setEditingSector({
            name: '',
            definition: { origins: [], destinations: [] },
            t_transfer: 0,
            t_comm_ag: 0,
            t_separation: 0,
            t_coordination: 0,
            adjustment_factor_r: 0.8,
            capacity_baseline: 0
        });
        setIsCreating(true);
    };

    if (loading) return <div className="p-8 text-center">Cargando sectores...</div>;

    return (
        <div className="p-6 bg-slate-50 min-h-screen">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900">Gestión de Sectores ATC</h1>
                    <p className="text-slate-500">Circular Técnica Reglamentaria 006</p>
                </div>
                {!editingSector && (
                    <button onClick={startCreate} className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 shadow-sm transition-colors">
                        <Plus className="w-5 h-5" />
                        Nuevo Sector
                    </button>
                )}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* List Column */}
                <div className={`lg:col-span-1 space-y-4 ${editingSector ? 'hidden lg:block opacity-50 pointer-events-none' : ''}`}>
                    {sectors.map(sector => (
                        <div key={sector.id} className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 hover:border-indigo-300 transition-colors">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h3 className="font-bold text-lg text-slate-800">{sector.name}</h3>
                                    <div className="text-xs text-slate-500 mt-1 space-y-1">
                                        <p>Orígenes: {sector.definition.origins?.join(', ') || 'Todos'}</p>
                                        <p>Destinos: {sector.definition.destinations?.join(', ') || 'Todos'}</p>
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    <button onClick={() => startEdit(sector)} className="p-1.5 text-indigo-600 hover:bg-indigo-50 rounded-md">
                                        <Pencil className="w-4 h-4" />
                                    </button>
                                    <button onClick={() => sector.id && handleDelete(sector.id)} className="p-1.5 text-red-600 hover:bg-red-50 rounded-md">
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                            <div className="mt-3 pt-3 border-t border-slate-100 grid grid-cols-2 gap-2 text-xs">
                                <div>
                                    <span className="text-slate-400 block">T. Transfer</span>
                                    <span className="font-mono text-slate-700">{sector.t_transfer}s</span>
                                </div>
                                <div>
                                    <span className="text-slate-400 block">T. Comm A/G</span>
                                    <span className="font-mono text-slate-700">{sector.t_comm_ag}s</span>
                                </div>
                                <div>
                                    <span className="text-slate-400 block">Factor R</span>
                                    <span className="font-mono text-indigo-600 font-bold">{sector.adjustment_factor_r}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                    {sectors.length === 0 && (
                        <div className="text-center p-8 text-slate-400 border-2 border-dashed border-slate-200 rounded-xl">
                            No hay sectores definidos.
                        </div>
                    )}
                </div>

                {/* Form Column */}
                {editingSector && (
                    <div className="lg:col-span-2">
                        <div className="bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden">
                            <div className="px-6 py-4 border-b border-slate-100 bg-slate-50 flex justify-between items-center">
                                <h2 className="font-bold text-xl text-slate-800">
                                    {isCreating ? 'Configurar Nuevo Sector' : 'Editar Sector'}
                                </h2>
                                <button onClick={() => setEditingSector(null)} className="text-slate-400 hover:text-slate-600">
                                    <X className="w-6 h-6" />
                                </button>
                            </div>

                            <div className="p-6 space-y-6">
                                {/* Definition Section */}
                                <div className="space-y-4">
                                    <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider">Definición Geográfica</h3>
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 mb-1">Nombre del Sector</label>
                                        <input
                                            type="text"
                                            value={editingSector.name}
                                            onChange={e => setEditingSector({ ...editingSector, name: e.target.value })}
                                            className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all"
                                            placeholder="Ej: Sector Norte - Aproximación"
                                        />
                                    </div>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div>
                                            <label className="block text-sm font-medium text-slate-700 mb-1">Aeropuertos Origen</label>
                                            <MultiSelectLookup
                                                label=""
                                                placeholder="Buscar Orígenes..."
                                                value={editingSector.definition.origins.map(code => ({ id: code, label: code, value: code }))}
                                                onChange={(vals) => setEditingSector({
                                                    ...editingSector,
                                                    definition: {
                                                        ...editingSector.definition,
                                                        origins: vals.map(v => v.id as string)
                                                    }
                                                })}
                                                fetchOptions={async (query: string) => {
                                                    try {
                                                        const res = await api.get('/filters/origins');
                                                        const fullList = Array.isArray(res.data) ? res.data.map((s: string) => ({ id: s, label: s, value: s })) : [];
                                                        return fullList.filter((opt: { label: string }) => opt.label.toLowerCase().includes(query.toLowerCase()));
                                                    } catch (e) { return []; }
                                                }}
                                            />
                                            <p className="text-xs text-slate-500 mt-1">Vuelos que salen de estos aeropuertos.</p>
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-slate-700 mb-1">Aeropuertos Destino</label>
                                            <MultiSelectLookup
                                                label=""
                                                placeholder="Buscar Destinos..."
                                                value={editingSector.definition.destinations.map(code => ({ id: code, label: code, value: code }))}
                                                onChange={(vals) => setEditingSector({
                                                    ...editingSector,
                                                    definition: {
                                                        ...editingSector.definition,
                                                        destinations: vals.map(v => v.id as string)
                                                    }
                                                })}
                                                fetchOptions={async (query: string) => {
                                                    try {
                                                        const res = await api.get('/filters/destinations');
                                                        const fullList = Array.isArray(res.data) ? res.data.map((s: string) => ({ id: s, label: s, value: s })) : [];
                                                        return fullList.filter((opt: { label: string }) => opt.label.toLowerCase().includes(query.toLowerCase()));
                                                    } catch (e) { return []; }
                                                }}
                                            />
                                            <p className="text-xs text-slate-500 mt-1">Vuelos que llegan a estos aeropuertos.</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="border-t border-slate-100 my-4"></div>

                                {/* Manual Parameters Section */}
                                <div className="space-y-4">
                                    <div className="flex items-center justify-between">
                                        <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider">Parámetros Manuales (TFC)</h3>
                                        <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full border border-yellow-200">Requerido por Circular 006</span>
                                    </div>
                                    <p className="text-sm text-slate-500 italic">Ingrese los tiempos promedio en SEGUNDOS obtenidos mediante observación/cronómetro.</p>

                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                        {[
                                            { label: 'T. Transferencia', key: 't_transfer', desc: 'Aceptación/Transferencia' },
                                            { label: 'T. Comms A/G', key: 't_comm_ag', desc: 'Comunicaciones Aire-Tierra' },
                                            { label: 'T. Separación', key: 't_separation', desc: 'Maniobras de separación' },
                                            { label: 'T. Coordinación', key: 't_coordination', desc: 'Coord. Punto a Punto (P/P)' },
                                        ].map((field) => (
                                            <div key={field.key} className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                                                <label className="block text-xs font-bold text-slate-700 mb-1">{field.label}</label>
                                                <div className="relative">
                                                    <input
                                                        type="number"
                                                        step="0.1"
                                                        value={editingSector[field.key as keyof Sector] as number}
                                                        onChange={e => setEditingSector({ ...editingSector, [field.key]: parseFloat(e.target.value) || 0 })}
                                                        className="w-full px-2 py-1.5 border border-slate-300 rounded focus:ring-indigo-500 focus:border-indigo-500"
                                                    />
                                                    <span className="absolute right-2 top-1.5 text-xs text-slate-400">seg</span>
                                                </div>
                                                <p className="text-[10px] text-slate-400 mt-1 leading-tight">{field.desc}</p>
                                            </div>
                                        ))}
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                                        <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-100">
                                            <label className="block text-sm font-bold text-indigo-900 mb-1">Factor de Ajuste (R)</label>
                                            <div className="flex items-center gap-4">
                                                <input
                                                    type="range"
                                                    min="0.5"
                                                    max="1.0"
                                                    step="0.05"
                                                    value={editingSector.adjustment_factor_r}
                                                    onChange={e => setEditingSector({ ...editingSector, adjustment_factor_r: parseFloat(e.target.value) })}
                                                    className="w-full accent-indigo-600"
                                                />
                                                <span className="font-mono text-xl font-bold text-indigo-700">{editingSector.adjustment_factor_r}</span>
                                            </div>
                                            <p className="text-xs text-indigo-700 mt-2">Factor de reducción por limitaciones operacionales (Metereología, Terreno, etc.). Rango recomendado: 0.6 - 0.9.</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Actions */}
                                <div className="pt-6 flex justify-end gap-3 sticky bottom-0 bg-white border-t border-slate-100 mt-4">
                                    <button
                                        onClick={() => setEditingSector(null)}
                                        className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg font-medium transition-colors"
                                    >
                                        Cancelar
                                    </button>
                                    <button
                                        onClick={handleSave}
                                        className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-bold shadow-md hover:shadow-lg transition-all flex items-center gap-2"
                                    >
                                        <Check className="w-5 h-5" />
                                        Guardar Configuración
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SectorConfigurationView;
