import { useState, useEffect } from 'react';
import type { Region } from '../../api';
import { getRegions, deleteRegion, createRegion, updateRegion } from '../../api';
import { RegionForm } from './RegionForm';
import { Plus, Pencil, Trash2, Globe, Calendar } from 'lucide-react';

/**
 * Componente de Gestión: Maestro de Regiones Aeronáuticas.
 * 
 * Este componente es el centro de control para la definición de regiones 
 * de búsqueda y análisis. Proporciona una interfaz CRUD completa integrada 
 * con el backend DuckDB.
 * 
 * Atributos Técnicos:
 * - Ciclo de Vida: Carga inicial de datos (fetch) y sincronización post-mutación.
 * - Modo Edición: Gestión de estado dual (Creación/Edición) mediante el estado 'editingRegion'.
 * - Seguridad Operativa: Confirmación de borrado físico para prevenir pérdida de metadatos.
 */
export const RegionsList = () => {
    // regions: Pool de regiones registradas en el sistema
    const [regions, setRegions] = useState<Region[]>([]);

    // loading: Estado de espera durante la resolución de la lista principal
    const [loading, setLoading] = useState(true);

    // isFormOpen: Control de visibilidad para el componente modal RegionForm
    const [isFormOpen, setIsFormOpen] = useState(false);

    // editingRegion: Buffer de datos para el objeto que se está modificando; null para nuevos registros
    const [editingRegion, setEditingRegion] = useState<Region | null>(null);

    /**
     * Recupera el inventario de regiones desde el servicio API.
     */
    const fetchRegions = async () => {
        try {
            const data = await getRegions();
            setRegions(data);
        } catch (error) {
            console.error("Fallo en la sincronización de regiones:", error);
        } finally {
            setLoading(false);
        }
    };

    // Inicialización del componente
    useEffect(() => {
        fetchRegions();
    }, []);

    /**
     * Prepara el bus de datos para una nueva inserción.
     */
    const handleCreate = () => {
        setEditingRegion(null);
        setIsFormOpen(true);
    };

    /**
     * Mapea un registro existente al bus de edición.
     * @param region - Objeto regional a modificar.
     */
    const handleEdit = (region: Region) => {
        setEditingRegion(region);
        setIsFormOpen(true);
    };

    /**
     * Ejecuta el comando de purga física en el backend.
     * @param id - Identificador único de la región.
     */
    const handleDelete = async (id: number) => {
        if (confirm('ADVERTENCIA: ¿Confirma la eliminación de esta región? Las asociaciones con aeropuertos podrían verse afectadas.')) {
            try {
                await deleteRegion(id);
                fetchRegions();
            } catch (error) {
                console.error("Fallo en ejecución de borrado:", error);
                alert("Error técnico: La región podría tener dependencias activas.");
            }
        }
    };

    /**
     * Orquestador de guardado. Decide entre POST (Creación) o PUT (Actualización).
     * @param data - Payload de la región procesado por el formulario.
     */
    const handleFormSubmit = async (data: Region) => {
        try {
            if (editingRegion && editingRegion.id) {
                // Flujo de Actualización (Update Adaptive)
                await updateRegion(editingRegion.id, data);
            } else {
                // Flujo de Creación (Insert Initial)
                await createRegion(data);
            }
            await fetchRegions();
        } catch (error) {
            throw error; // El error es capturado por el componente hijo para feedback visual
        }
    };

    if (loading) return (
        <div className="p-8 text-center text-slate-500 animate-pulse flex flex-col items-center gap-2">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
            <span className="text-xs font-bold uppercase tracking-widest">Sincronizando Regiones...</span>
        </div>
    );

    return (
        <div className="card overflow-hidden">
            {/* CABECERA DE LA SECCIÓN */}
            <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex justify-between items-center">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-indigo-100 text-indigo-600 rounded-lg">
                        <Globe className="w-5 h-5" />
                    </div>
                    <h3 className="font-semibold text-slate-700">Regiones Registradas</h3>
                </div>
                <button
                    onClick={handleCreate}
                    className="btn-primary flex items-center gap-2 text-sm px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-all"
                >
                    <Plus size={16} /> Nueva Región
                </button>
            </div>

            {/* LISTADO DE REGIONES */}
            <div className="divide-y divide-slate-100">
                {regions.length === 0 ? (
                    <div className="p-12 text-center text-slate-400">
                        <Globe className="w-12 h-12 mx-auto mb-3 opacity-20" />
                        <p>No hay regiones registradas en el sistema.</p>
                        <button onClick={handleCreate} className="text-primary hover:underline mt-2 text-sm font-medium">
                            Crear la primera región
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
                        {regions.map((region) => (
                            <div key={region.id} className="p-5 bg-white border border-slate-100 rounded-2xl shadow-sm hover:shadow-md transition-all group">
                                <div className="flex justify-between items-start mb-3">
                                    <div className="flex flex-col">
                                        <h4 className="font-bold text-slate-900 group-hover:text-primary transition-colors text-lg">
                                            {region.name}
                                        </h4>
                                        <span className="text-xs font-mono bg-slate-50 px-2 py-0.5 rounded text-slate-600 border border-slate-100 w-fit mt-1">
                                            {region.code}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <button
                                            onClick={() => handleEdit(region)}
                                            className="p-2 text-slate-400 hover:text-primary hover:bg-slate-50 rounded-lg transition-all"
                                            title="Editar"
                                        >
                                            <Pencil size={18} />
                                        </button>
                                        <button
                                            onClick={() => region.id && handleDelete(region.id)}
                                            className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-all"
                                            title="Eliminar"
                                        >
                                            <Trash2 size={18} />
                                        </button>
                                    </div>
                                </div>
                                <p className="text-sm text-slate-500 line-clamp-2 min-h-[40px] leading-relaxed">
                                    {region.description || "Sin descripción adicional."}
                                </p>
                                <div className="flex gap-4 mt-4 pt-4 border-t border-slate-50 text-[10px] text-slate-400 uppercase font-bold tracking-wider">
                                    <span className="flex items-center gap-1.5">
                                        <Calendar className="w-3.5 h-3.5" />
                                        {region.created_at ? new Date(region.created_at).toLocaleDateString() : 'Pendiente'}
                                    </span>
                                    {region.nivel_min !== undefined && (
                                        <span className="px-2 py-0.5 bg-indigo-50 text-indigo-600 rounded">
                                            Min: FL {region.nivel_min}
                                        </span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* FORMULARIO MODAL */}
            <RegionForm
                isOpen={isFormOpen}
                onClose={() => setIsFormOpen(false)}
                initialData={editingRegion}
                onSubmit={handleFormSubmit}
            />
        </div>
    );
};
