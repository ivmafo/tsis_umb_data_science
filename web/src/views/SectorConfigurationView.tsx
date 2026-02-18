
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

/**
 * Vista de Ingeniería: Configuración de Sectores y Parámetros Operativos.
 * 
 * Este componente es el núcleo de parametrización del sistema. Define los
 * límites lógicos (Orígenes/Destinos) y los coeficientes técnicos de trabajo
 * (TFC) que alimentan el motor de cálculo de capacidad Circular 006.
 * 
 * Atributos Técnicos:
 * - Geometría de Flujo: Mapeo de aeropuertos para definir 'qué es un sector'.
 * - Coeficientes DORATASK: Gestión de tiempos de Transferencia, Comunicación, 
 *   Separación y Coordinación.
 * - Factor Operacional R: Implementa un control de slider para el ajuste fino
 *   de la capacidad declarada frente a la teórica.
 */
const SectorConfigurationView: React.FC = () => {
    // sectors: Colección de definiciones de sectores persistidas en DuckDB
    const [sectors, setSectors] = useState<Sector[]>([]);

    // loading: Estado de bloqueo para la sincronización inicial de red
    const [loading, setLoading] = useState(true);

    // editingSector: Buffer temporal (Snapshot) del sector en proceso de modificación
    const [editingSector, setEditingSector] = useState<Sector | null>(null);

    // isCreating: Flag de UX para alternar entre POST (Nuevo) y PUT (Actualización)
    const [isCreating, setIsCreating] = useState(false);

    /**
     * Sincronización inicial del maestro de sectores.
     */
    useEffect(() => {
        fetchSectors();
    }, []);

    /**
     * Consultar catálogo de sectores.
     * Invoca el endpoint /sectors/ para recuperar el estado actual de la configuración.
     */
    const fetchSectors = async () => {
        try {
            const response = await api.get('/sectors/');
            setSectors(response.data);
            setLoading(false);
        } catch (error) {
            console.error("Fallo técnico al recuperar sectores (Config):", error);
            setLoading(false);
        }
    };

    /**
     * Motor de Persistencia de Sectores.
     * Consolida los cambios del buffer 'editingSector' hacia la base de datos distribuida.
     */
    const handleSave = async () => {
        if (!editingSector) return;

        try {
            if (editingSector.id) {
                // Transacción de Actualización (PUT)
                await api.put(`/sectors/${editingSector.id}`, editingSector);
            } else {
                // Transacción de Inserción (POST)
                await api.post('/sectors/', editingSector);
            }
            setEditingSector(null);
            setIsCreating(false);
            fetchSectors(); // Re-indexar lista local
        } catch (error) {
            console.error("Fallo en persistencia de sector:", error);
            alert("Error de validación: Verifique que el nombre sea único y los parámetros sean numéricos.");
        }
    };

    /**
     * Manejador de Eliminación.
     * Purga física del sector de la configuración global.
     */
    const handleDelete = async (id: string) => {
        if (!confirm("ADVERTENCIA: ¿Desea eliminar la configuración de este sector? Los reportes asociados quedarán huérfanos.")) return;
        try {
            await api.delete(`/sectors/${id}`);
            fetchSectors();
        } catch (error) {
            console.error("Fallo al purgar sector:", error);
        }
    };

    /**
     * Transición a Modo Edición.
     * Clona el objeto del sector para evitar mutaciones directas en la lista durante la edición.
     */
    const startEdit = (sector: Sector) => {
        setEditingSector({ ...sector });
        setIsCreating(false);
    };

    /**
     * Transición a Modo Creación.
     * Inicializa un scaffold de sector con los valores por defecto de la Circular 006.
     */
    const startCreate = () => {
        setEditingSector({
            name: '',
            definition: { origins: [], destinations: [] },
            t_transfer: 0,
            t_comm_ag: 0,
            t_separation: 0,
            t_coordination: 0,
            adjustment_factor_r: 0.8, // Valor base recomendado por OACI
            capacity_baseline: 0
        });
        setIsCreating(true);
    };

    if (loading) return (
        <div className="p-8 text-center text-slate-500 animate-pulse">
            Cargando configuración de sectores...
        </div>
    );

    return (
        <div className="p-6 bg-slate-50 min-h-screen">
            {/* ENCABEZADO DE LA VISTA */}
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900">Gestión de Sectores ATC</h1>
                    <p className="text-slate-500">Parámetros operativos según Circular Técnica Reglamentaria 006</p>
                </div>
                {!editingSector && (
                    <button onClick={startCreate} className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 shadow-lg shadow-indigo-200 transition-all">
                        <Plus className="w-5 h-5" />
                        Nuevo Sector
                    </button>
                )}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* COLUMNA IZQUIERDA: Listado de Sectores */}
                <div className={`lg:col-span-1 space-y-4 ${editingSector ? 'hidden lg:block opacity-50 pointer-events-none' : ''}`}>
                    {sectors.map(sector => (
                        <div key={sector.id} className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 hover:border-indigo-200 hover:shadow-md transition-all group">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h3 className="font-bold text-lg text-slate-800 group-hover:text-indigo-600 transition-colors">{sector.name}</h3>
                                    <div className="text-xs text-slate-500 mt-2 space-y-1">
                                        <p className="flex items-center gap-1 font-medium">Orígenes: <span className="text-slate-700">{sector.definition.origins?.join(', ') || 'Global'}</span></p>
                                        <p className="flex items-center gap-1 font-medium">Destinos: <span className="text-slate-700">{sector.definition.destinations?.join(', ') || 'Global'}</span></p>
                                    </div>
                                </div>
                                <div className="flex gap-1">
                                    <button onClick={() => startEdit(sector)} className="p-2 text-indigo-500 hover:bg-indigo-50 rounded-lg transition-colors" title="Editar">
                                        <Pencil className="w-4 h-4" />
                                    </button>
                                    <button onClick={() => sector.id && handleDelete(sector.id)} className="p-2 text-rose-500 hover:bg-rose-50 rounded-lg transition-colors" title="Eliminar">
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                            {/* MINI PANEL DE PARÁMETROS */}
                            <div className="mt-4 pt-4 border-t border-slate-50 grid grid-cols-2 gap-3 text-[10px] uppercase font-bold tracking-wider">
                                <div className="bg-slate-50 p-2 rounded">
                                    <span className="text-slate-400 block mb-0.5">T. Transfer</span>
                                    <span className="text-slate-700">{sector.t_transfer}s</span>
                                </div>
                                <div className="bg-slate-50 p-2 rounded">
                                    <span className="text-slate-400 block mb-0.5">T. Comm A/G</span>
                                    <span className="text-slate-700">{sector.t_comm_ag}s</span>
                                </div>
                                <div className="bg-indigo-50 p-2 rounded col-span-2 flex justify-between items-center text-indigo-600">
                                    <span>Factor R</span>
                                    <span className="text-sm">{sector.adjustment_factor_r}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                    {sectors.length === 0 && (
                        <div className="text-center p-12 text-slate-400 border-2 border-dashed border-slate-200 rounded-2xl bg-white/50">
                            No hay sectores definidos. Comience agregando uno nuevo.
                        </div>
                    )}
                </div>

                {/* COLUMNA DERECHA: Formulario de Edición/Creación */}
                {editingSector && (
                    <div className="lg:col-span-2">
                        <div className="bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden sticky top-6">
                            <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
                                <h2 className="font-bold text-xl text-slate-800">
                                    {isCreating ? 'Configurar Nuevo Sector' : 'Editar Sector ATC'}
                                </h2>
                                <button onClick={() => setEditingSector(null)} className="p-2 hover:bg-slate-200 rounded-full text-slate-400 transition-colors">
                                    <X className="w-6 h-6" />
                                </button>
                            </div>

                            <div className="p-8 space-y-8">
                                {/* SECCIÓN: Definición Geográfica */}
                                <div className="space-y-4">
                                    <h3 className="text-xs font-bold text-indigo-600 uppercase tracking-widest flex items-center gap-2">
                                        <div className="w-1.5 h-1.5 bg-indigo-600 rounded-full"></div>
                                        Definición del Flujo Geográfico
                                    </h3>
                                    <div>
                                        <label className="block text-sm font-semibold text-slate-700 mb-1.5">Nombre Identificador del Sector</label>
                                        <input
                                            type="text"
                                            value={editingSector.name}
                                            onChange={e => setEditingSector({ ...editingSector, name: e.target.value })}
                                            className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all font-medium"
                                            placeholder="Ej: APP Norte - Subsector 01"
                                        />
                                    </div>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div className="space-y-2">
                                            <label className="block text-sm font-semibold text-slate-700">Aeropuertos de Origen</label>
                                            <MultiSelectLookup
                                                label=""
                                                placeholder="Buscar códigos OACI..."
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
                                            <p className="text-[10px] text-slate-400 leading-tight">Vuelos que despegan o proceden de estas terminales.</p>
                                        </div>
                                        <div className="space-y-2">
                                            <label className="block text-sm font-semibold text-slate-700">Aeropuertos de Destino</label>
                                            <MultiSelectLookup
                                                label=""
                                                placeholder="Buscar códigos OACI..."
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
                                            <p className="text-[10px] text-slate-400 leading-tight">Vuelos con destino final o arribo a estas terminales.</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="h-px bg-slate-100"></div>

                                {/* SECCIÓN: Parámetros del Tiempo de Carga (TFC) */}
                                <div className="space-y-5">
                                    <div className="flex items-center justify-between">
                                        <h3 className="text-xs font-bold text-amber-600 uppercase tracking-widest flex items-center gap-2">
                                            <div className="w-1.5 h-1.5 bg-amber-600 rounded-full"></div>
                                            Tiempos Promedio de Carga (TFC)
                                        </h3>
                                        <span className="text-[10px] bg-amber-50 text-amber-700 px-3 py-1 rounded-full border border-amber-100 font-bold">CIRCULAR TÉCNICA 006</span>
                                    </div>
                                    <p className="text-sm text-slate-500 italic leading-snug">
                                        Valores en SEGUNDOS determinados mediante estudios de tiempos y movimientos o registros históricos.
                                    </p>

                                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                                        {[
                                            { label: 'Transferencia', key: 't_transfer', desc: 'Aceptación/Traspaso' },
                                            { label: 'Comms A/G', key: 't_comm_ag', desc: 'Fraseología Aire/Tierra' },
                                            { label: 'Separación', key: 't_separation', desc: 'Vectores/Nivelación' },
                                            { label: 'Coordinación', key: 't_coordination', desc: 'Interfonía P/P' },
                                        ].map((field) => (
                                            <div key={field.key} className="bg-slate-50 p-4 rounded-xl border border-slate-100 hover:border-amber-200 transition-colors">
                                                <label className="block text-[10px] font-bold text-slate-400 uppercase mb-2">{field.label}</label>
                                                <div className="relative group">
                                                    <input
                                                        type="number"
                                                        step="0.1"
                                                        value={editingSector[field.key as keyof Sector] as number}
                                                        onChange={e => setEditingSector({ ...editingSector, [field.key]: parseFloat(e.target.value) || 0 })}
                                                        className="w-full bg-white px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-amber-500 font-mono font-bold text-slate-700"
                                                    />
                                                    <span className="absolute right-3 top-2.5 text-xs text-slate-300 font-medium">seg</span>
                                                </div>
                                                <p className="text-[9px] text-slate-400 mt-2 font-medium">{field.desc}</p>
                                            </div>
                                        ))}
                                    </div>

                                    {/* FACTOR DE AJUSTE R */}
                                    <div className="bg-indigo-50/50 p-6 rounded-2xl border border-indigo-100 mt-6 group">
                                        <div className="flex justify-between items-center mb-4">
                                            <div>
                                                <label className="block text-sm font-bold text-indigo-900">Factor de Ajuste Operacional (R)</label>
                                                <p className="text-xs text-indigo-600 mt-0.5">Penalización por factores externos (MET, ATSR, etc.)</p>
                                            </div>
                                            <span className="text-2xl font-mono font-black text-indigo-600 bg-white px-4 py-1 rounded-xl shadow-sm border border-indigo-100">
                                                {editingSector.adjustment_factor_r}
                                            </span>
                                        </div>
                                        <input
                                            type="range"
                                            min="0.5"
                                            max="1.0"
                                            step="0.05"
                                            value={editingSector.adjustment_factor_r}
                                            onChange={e => setEditingSector({ ...editingSector, adjustment_factor_r: parseFloat(e.target.value) })}
                                            className="w-full accent-indigo-600 cursor-pointer"
                                        />
                                        <div className="flex justify-between text-[10px] text-indigo-400 font-bold mt-2">
                                            <span>MÁXIMA RESTRICCIÓN (0.5)</span>
                                            <span>CONDICIONES IDEALES (1.0)</span>
                                        </div>
                                    </div>
                                </div>

                                {/* ACCIONES DEL FORMULARIO */}
                                <div className="pt-8 flex justify-end gap-4 border-t border-slate-50">
                                    <button
                                        type="button"
                                        onClick={() => setEditingSector(null)}
                                        className="px-6 py-2.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-xl font-semibold transition-all"
                                    >
                                        Abstenerse
                                    </button>
                                    <button
                                        onClick={handleSave}
                                        className="px-8 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold shadow-lg shadow-indigo-100 transition-all flex items-center gap-2 active:scale-95"
                                    >
                                        <Check className="w-5 h-5" />
                                        Guardar Sector
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
