import { useState, useEffect } from 'react';
import type { Region } from '../../api';
import { getRegions, deleteRegion, createRegion, updateRegion } from '../../api';
import { RegionForm } from './RegionForm';
import { Plus, Pencil, Trash2, Globe, Calendar } from 'lucide-react';

export const RegionsList = () => {
    const [regions, setRegions] = useState<Region[]>([]);
    const [loading, setLoading] = useState(true);
    const [isFormOpen, setIsFormOpen] = useState(false);
    const [editingRegion, setEditingRegion] = useState<Region | null>(null);

    const fetchRegions = async () => {
        try {
            const data = await getRegions();
            setRegions(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRegions();
    }, []);

    const handleCreate = () => {
        setEditingRegion(null);
        setIsFormOpen(true);
    };

    const handleEdit = (region: Region) => {
        setEditingRegion(region);
        setIsFormOpen(true);
    };

    const handleDelete = async (id: number) => {
        if (confirm('¿Estás seguro de eliminar esta región?')) {
            try {
                await deleteRegion(id);
                fetchRegions();
            } catch (error) {
                console.error("Error deleting region", error);
            }
        }
    };

    const handleFormSubmit = async (data: Region) => {
        if (editingRegion && editingRegion.id) {
            await updateRegion(editingRegion.id, data);
        } else {
            await createRegion(data);
        }
        await fetchRegions();
    };

    if (loading) return <div className="p-8 text-center text-slate-500 animate-pulse">Cargando datos...</div>;

    return (
        <div className="card overflow-hidden">
            <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex justify-between items-center">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-indigo-100 text-indigo-600 rounded-lg">
                        <Globe className="w-5 h-5" />
                    </div>
                    <h3 className="font-semibold text-slate-700">Regiones Registradas</h3>
                </div>
                <button
                    onClick={handleCreate}
                    className="btn-primary flex items-center gap-2 text-sm"
                >
                    <Plus size={16} /> Nueva Región
                </button>
            </div>

            <div className="divide-y divide-slate-100">
                {regions.length === 0 ? (
                    <div className="p-12 text-center text-slate-400">
                        <Globe className="w-12 h-12 mx-auto mb-3 opacity-20" />
                        <p>No hay regiones registradas.</p>
                        <button onClick={handleCreate} className="text-primary hover:underline mt-2 text-sm">
                            Crear la primera región
                        </button>
                    </div>
                ) : (
                    regions.map((region) => (
                        <div key={region.id} className="p-4 hover:bg-slate-50 transition-colors group">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h4 className="font-semibold text-slate-900 flex items-center gap-2">
                                        {region.name}
                                        <span className="text-xs font-mono bg-slate-100 px-2 py-0.5 rounded text-slate-500 border border-slate-200">
                                            {region.code}
                                        </span>
                                    </h4>
                                    <p className="text-sm text-slate-500 mt-1 line-clamp-2 max-w-xl">
                                        {region.description || "Sin descripción"}
                                    </p>
                                    <div className="flex gap-4 mt-2 text-xs text-slate-400">
                                        <span className="flex items-center gap-1" title="Fecha de creación">
                                            <Calendar className="w-3 h-3" />
                                            {region.created_at ? new Date(region.created_at).toLocaleDateString() : '-'}
                                        </span>
                                        <span title="Nivel Mínimo">
                                            Min FL: {region.nivel_min}
                                        </span>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button
                                        onClick={() => handleEdit(region)}
                                        className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                        title="Editar"
                                    >
                                        <Pencil size={18} />
                                    </button>
                                    <button
                                        onClick={() => region.id && handleDelete(region.id)}
                                        className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                                        title="Eliminar"
                                    >
                                        <Trash2 size={18} />
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>

            <RegionForm
                isOpen={isFormOpen}
                onClose={() => setIsFormOpen(false)}
                initialData={editingRegion}
                onSubmit={handleFormSubmit}
            />
        </div>
    );
};
