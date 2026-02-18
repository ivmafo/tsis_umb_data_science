import { useState, useEffect } from 'react';
import { FaSearch, FaPlus, FaTrash, FaTimes, FaEdit, FaMapMarkedAlt } from 'react-icons/fa';
import {
    getRegionAirports,
    createRegionAirport,
    deleteRegionAirport,
    updateRegionAirport,
    getRegions,
    type RegionAirport,
    type Region
} from '../api';

/**
 * Vista de Asociación: Mapeo de Regiones y Aeropuertos (RA).
 * 
 * Este componente gestiona la relación muchos-a-muchos entre las Regiones
 * Aeronáuticas y los Aeropuertos (nodos). Es la base para el filtrado espacial
 * agregador que permite ver la demanda de vuelos 'por región' en lugar de 
 * 'por punto'.
 * 
 * Atributos Técnicos:
 * - Carga en Paralelo: Utiliza Promise.all para sincronizar el catálogo de
 *   regiones y las asignaciones existentes de forma atómica.
 * - Validación Cruzada: Asegura integridad referencial mediante selectores
 *   poblados dinámicamente desde el maestro de regiones.
 * - Registro Histórico: Incluye visualización de fecha de creación de la 
 *   asociación para auditoría.
 */
export const RegionAirportsView = () => {
    // items: Lista de enlaces Region <-> Aeropuerto vigentes
    const [items, setItems] = useState<RegionAirport[]>([]);

    // regions: Catálogo de regiones para poblar el dropdown de asignación
    const [regions, setRegions] = useState<Region[]>([]);

    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [page, setPage] = useState(1);
    const [total, setTotal] = useState(0);
    const pageSize = 10;

    // ESTADO: Gestión de transaccionalidad en el modal
    const [showModal, setShowModal] = useState(false);
    const [editingId, setEditingId] = useState<number | null>(null);
    const [formData, setFormData] = useState({
        icao_code: '',
        region_id: 0
    });

    /**
     * Orquestador de Datos.
     * Recupera simultáneamente las asignaciones paginadas y el catálogo maestro
     * de regiones para evitar inconsistencias en el renderizado de etiquetas.
     */
    const loadData = async () => {
        setLoading(true);
        try {
            // Paralelización de peticiones para optimizar TTI (Time to Interactive)
            const [raData, rData] = await Promise.all([
                getRegionAirports(page, pageSize, search),
                getRegions()
            ]);
            setItems(raData.data);
            setTotal(raData.total);
            setRegions(rData);
        } catch (err) {
            console.error("Fallo técnico en carga de asignaciones RA:", err);
        } finally {
            setLoading(false);
        }
    };

    /**
     * Listener de búsqueda con estabilidad (Debounce implícito por timeout).
     */
    useEffect(() => {
        const timer = setTimeout(() => {
            loadData();
        }, 300);
        return () => clearTimeout(timer);
    }, [page, search]);

    /**
     * Limpieza de buffer transaccional.
     */
    const resetForm = () => {
        setFormData({ icao_code: '', region_id: 0 });
        setEditingId(null);
    };

    /**
     * Handler de Guardado.
     * Implementa lógica dual de creación/actualización basándose en el contexto del trigger.
     */
    const handleCreateOrUpdate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            // Reglas de Validación Front-end
            if (!formData.icao_code || formData.region_id <= 0) {
                alert("Error: El Código ICAO y la Región de destino son obligatorios.");
                return;
            }

            if (editingId) {
                // Actualización de enlace existente
                await updateRegionAirport(editingId, formData);
            } else {
                // Generación de nueva asignación
                await createRegionAirport(formData);
            }

            setShowModal(false);
            resetForm();
            loadData(); // Re-sincronizar pool
        } catch (error: any) {
            console.error("Fallo en flujo de guardado RA:", error);
            const msg = error.response?.data?.detail || "Error interno al persistir asignación.";
            alert(msg);
        }
    };

    /**
     * Inyección de datos en modal para edición.
     */
    const handleEdit = (item: RegionAirport) => {
        setEditingId(item.id);
        setFormData({
            icao_code: item.icao_code,
            region_id: item.region_id
        });
        setShowModal(true);
    };

    /**
     * Operación de Purga.
     * Elimina el enlace lógico sin afectar las entidades base (Region o Aeropuerto).
     */
    const handleDelete = async (id: number) => {
        if (!confirm("¿Desea eliminar esta asignación? El aeropuerto dejará de pertenecer a la región para efectos de cálculo.")) return;
        try {
            await deleteRegionAirport(id);
            loadData();
        } catch (error) {
            console.error("Fallo al purgar asignación RA:", error);
        }
    };

    /**
     * Apertura de formulario de creación.
     */
    const openCreateModal = () => {
        resetForm();
        setShowModal(true);
    };

    const getRegionDisplay = (regionId: number) => {
        const region = regions.find(r => r.id === regionId);
        if (!region) return `Region ${regionId}`;
        // Prefer name, fallback to code or description if needed
        return region.name || region.code || `Region ${regionId}`;
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-slate-800">Asignación Regiones (RA)</h1>
                    <p className="text-slate-500 mt-1">Gestión de la tabla de enlace Region-Aeropuerto</p>
                </div>
                <button
                    onClick={openCreateModal}
                    className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark transition-colors shadow-lg shadow-primary/30"
                >
                    <FaPlus />
                    <span>Nueva Asignación</span>
                </button>
            </div>

            {/* Search */}
            <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-100 flex gap-4">
                <div className="relative flex-1">
                    <FaSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                        type="text"
                        placeholder="Buscar por código ICAO..."
                        className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                        value={search}
                        onChange={(e) => {
                            setSearch(e.target.value);
                            setPage(1);
                        }}
                    />
                </div>
            </div>

            {/* Table */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-slate-50 text-left">
                            <tr>
                                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">ID</th>
                                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Aeropuerto (ICAO)</th>
                                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Región</th>
                                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Creado</th>
                                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Acciones</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {loading ? (
                                <tr><td colSpan={5} className="p-8 text-center text-slate-500">Cargando...</td></tr>
                            ) : items.map((item) => (
                                <tr key={item.id} className="hover:bg-slate-50/50 transition-colors">
                                    <td className="px-6 py-4 text-sm text-slate-500">#{item.id}</td>
                                    <td className="px-6 py-4 text-sm text-slate-800 font-medium">{item.icao_code}</td>
                                    <td className="px-6 py-4 text-sm text-slate-600">
                                        <div className="flex items-center gap-2">
                                            <FaMapMarkedAlt className="text-slate-400" />
                                            <span>{getRegionDisplay(item.region_id)}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-xs text-slate-500">{item.created_at}</td>
                                    <td className="px-6 py-4">
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => handleEdit(item)}
                                                className="p-1.5 text-blue-600 hover:bg-blue-50 rounded"
                                            >
                                                <FaEdit />
                                            </button>
                                            <button
                                                onClick={() => handleDelete(item.id)}
                                                className="p-1.5 text-red-600 hover:bg-red-50 rounded"
                                            >
                                                <FaTrash />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Pagination */}
                <div className="p-4 border-t border-slate-100 flex justify-between items-center bg-slate-50/50">
                    <span className="text-sm text-slate-500">Mostrando {(page - 1) * pageSize + 1} - {Math.min(page * pageSize, total)} de {total}</span>
                    <div className="flex gap-2">
                        <button
                            disabled={page === 1}
                            onClick={() => setPage(p => p - 1)}
                            className="px-3 py-1 border border-slate-200 rounded bg-white disabled:opacity-50 hover:bg-slate-50"
                        >
                            Anterior
                        </button>
                        <button
                            disabled={page * pageSize >= total}
                            onClick={() => setPage(p => p + 1)}
                            className="px-3 py-1 border border-slate-200 rounded bg-white disabled:opacity-50 hover:bg-slate-50"
                        >
                            Siguiente
                        </button>
                    </div>
                </div>
            </div>

            {/* Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
                        <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                            <h2 className="text-xl font-bold text-slate-800">
                                {editingId ? 'Editar Asignación' : 'Nueva Asignación'}
                            </h2>
                            <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600">
                                <FaTimes />
                            </button>
                        </div>
                        <form onSubmit={handleCreateOrUpdate} className="p-6 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Código ICAO</label>
                                <input
                                    type="text" required
                                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 outline-none uppercase"
                                    value={formData.icao_code}
                                    onChange={e => setFormData({ ...formData, icao_code: e.target.value.toUpperCase() })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Región</label>
                                <select
                                    required
                                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 outline-none bg-white"
                                    value={formData.region_id || ''}
                                    onChange={e => setFormData({ ...formData, region_id: parseInt(e.target.value) || 0 })}
                                >
                                    <option value="">Seleccione una Región</option>
                                    {regions.map(region => (
                                        <option key={region.id} value={region.id}>
                                            {region.name}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div className="flex justify-end gap-3 pt-4 border-t border-slate-100 mt-6">
                                <button
                                    type="button"
                                    onClick={() => setShowModal(false)}
                                    className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg font-medium"
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 bg-primary text-white hover:bg-primary-dark rounded-lg font-medium shadow-lg shadow-primary/30"
                                >
                                    Guardar
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};
