import { useState, useEffect } from 'react';
import { FaSearch, FaPlus, FaTrash, FaTimes, FaEdit } from 'react-icons/fa';
import { getAirports, createAirport, deleteAirport, updateAirport, type Airport } from '../api';

/**
 * Vista AirportsView.
 * Proporciona una interfaz completa para la gestión de aeropuertos en el sistema.
 * Permite buscar, filtrar, crear, editar y eliminar registros de aeropuertos.
 */
/**
 * Vista de Adminsitración: Catálogo Maestro de Aeropuertos.
 * 
 * Este componente proporciona una interfaz de gestión centralizada para los
 * nodos de la red aeronáutica. Permite el mantenimiento operativo (CRUD) de 
 * los metadatos de aeropuertos, fundamentales para el enlace geográfico de 
 * los registros de vuelos.
 * 
 * Atributos Técnicos:
 * - Búsqueda con Debounce: Optimiza la carga del servidor mediante un retraso
 *   de 300ms entre pulsaciones de teclas antes de disparar la consulta.
 * - Paginación Dinámica: Mapeo de estados 'page' y 'pageSize' hacia el API
 *   de DuckDB para navegación eficiente en sets de datos grandes.
 * - Validación de Integridad: Bloqueo de borrado si existen dependencias
 *   activas en la persistencia.
 */
export const AirportsView = () => {
    // pool: Inventario de aeropuertos en la ventana actual de paginación
    const [airports, setAirports] = useState<Airport[]>([]);

    // loading: Semáforo de estado de red para feedback visual (animate-pulse)
    const [loading, setLoading] = useState(true);

    // search: Buffer de texto para el predicado de búsqueda OACI/Nombre
    const [search, setSearch] = useState("");

    // page: Puntero de navegación paginada (Base 1)
    const [page, setPage] = useState(1);
    const [total, setTotal] = useState(0);
    const pageSize = 10;

    // ESTADOS DEL MODAL Y FORMULARIO (Buffer de Transacción)
    const [showModal, setShowModal] = useState(false);
    const [editingId, setEditingId] = useState<number | null>(null);
    const [formData, setFormData] = useState<Partial<Airport>>({
        icao_code: '',
        iata_code: '',
        name: '',
        city: '',
        country: '',
        type: 'small_airport',
        latitude: 0,
        longitude: 0,
        altitude: 0,
        timezone: 0,
        dst: 'U',
        source: 'User'
    });

    /**
     * Limpia el buffer del formulario para nuevos registros o cancelaciones.
     */
    const resetForm = () => {
        setFormData({
            icao_code: '', iata_code: '', name: '', city: '', country: '',
            type: 'small_airport', latitude: 0, longitude: 0, altitude: 0, timezone: 0, dst: 'U', source: 'User'
        });
        setEditingId(null);
    };

    /**
     * Sincroniza la lista de aeropuertos con el backend.
     * Incorpora los parámetros de búsqueda y paginación en el payload GET.
     */
    const fetchAirports = async () => {
        setLoading(true);
        try {
            // Llamada al endpoint paginado /airports/
            const data = await getAirports(page, pageSize, search);
            setAirports(data.data);
            setTotal(data.total);
        } catch (err) {
            console.error("Fallo crítico en sincronización de aeropuertos:", err);
        } finally {
            setLoading(false);
        }
    };

    /**
     * Ciclo de vida: Listener de Búsqueda Reactivo.
     * Implementa un debounce de 300ms para estabilizar la entrada del usuario.
     */
    useEffect(() => {
        const timer = setTimeout(() => {
            fetchAirports();
        }, 300);
        return () => clearTimeout(timer);
    }, [page, search]);

    /**
     * Persistencia: Envío de Formulario.
     * Determina automáticamente el verbo HTTP (POST/PUT) basado en 'editingId'.
     */
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            // Regla de Integridad: Requiere llaves primarias informativas
            if (!formData.name || !formData.icao_code) {
                alert("Restricción: El Nombre y Código ICAO son mandatorios.");
                return;
            }

            if (editingId) {
                // Modo PUT: Actualización de registro existente
                await updateAirport(editingId, formData);
            } else {
                // Modo POST: Inserción de nueva entidad
                await createAirport(formData as Airport);
            }

            setShowModal(false);
            resetForm();
            fetchAirports(); // Re-sincronizar vista post-escritura
        } catch (error) {
            console.error("Error en flujo de persistencia aeroportuaria:", error);
            alert("No se pudo completar la transacción. Verifique códigos duplicados.");
        }
    };

    /**
     * Preparación de Edición.
     * Mapea el objeto de la lista al buffer local del modal.
     */
    const handleEdit = (airport: Airport) => {
        setEditingId(airport.id);
        setFormData({
            icao_code: airport.icao_code,
            iata_code: airport.iata_code || '',
            name: airport.name,
            city: airport.city || '',
            country: airport.country || '',
            type: airport.type || 'small_airport',
            latitude: airport.latitude || 0,
            longitude: airport.longitude || 0,
            altitude: airport.altitude || 0,
            timezone: airport.timezone || 0,
            dst: airport.dst || 'U',
            source: airport.source || 'User'
        });
        setShowModal(true);
    };

    /**
     * Purga de Registro.
     * Solicita eliminación física del nodo si no tiene constraints en el backend.
     */
    const handleDelete = async (id: number) => {
        if (!confirm("ADVERTENCIA DE INTEGRIDAD: ¿Desea eliminar este aeropuerto? Esta acción podría invalidar registros de vuelos asociados.")) return;
        try {
            await deleteAirport(id);
            fetchAirports();
        } catch (error) {
            console.error("Fallo en purga de aeropuerto:", error);
            alert("Acción Bloqueada: El registro posee dependencias activas en el histórico de vuelos.");
        }
    };

    /**
     * Disparador de Creación.
     */
    const openCreateModal = () => {
        resetForm();
        setShowModal(true);
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500 relative">
            {/* CABECERA Y ACCIÓN PRINCIPAL */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-slate-800">Catálogo de Aeropuertos</h1>
                    <p className="text-slate-500 mt-1">Gestión administrativa de terminales y nodos de red</p>
                </div>
                <button
                    onClick={openCreateModal}
                    className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark transition-all shadow-lg shadow-primary/20"
                >
                    <FaPlus />
                    <span>Nuevo Aeropuerto</span>
                </button>
            </div>

            {/* BARRA DE BÚSQUEDA DINÁMICA */}
            <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-100 flex gap-4">
                <div className="relative flex-1">
                    <FaSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                        type="text"
                        placeholder="Buscar por nombre, código OACI o ciudad..."
                        className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary/30 outline-none transition-all"
                        value={search}
                        onChange={(e) => {
                            setSearch(e.target.value);
                            setPage(1); // Reiniciar a página 1 en cada búsqueda
                        }}
                    />
                </div>
            </div>

            {/* TABLA DE RESULTADOS */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-slate-50 border-b border-slate-100">
                            <tr>
                                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-widest">ID</th>
                                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-widest">Identificadores</th>
                                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-widest">Terminal / Nombre</th>
                                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-widest">Ubicación Geográfica</th>
                                <th className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-widest">Acciones</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50">
                            {loading ? (
                                <tr><td colSpan={5} className="p-12 text-center text-slate-400 animate-pulse">Cargando registros aeroportuarios...</td></tr>
                            ) : airports.map((airport) => (
                                <tr key={airport.id} className="hover:bg-slate-50/50 transition-colors group">
                                    <td className="px-6 py-4 text-sm text-slate-400 font-mono">#{airport.id}</td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-2">
                                            <span className="text-sm font-bold text-primary bg-primary/5 px-2 py-0.5 rounded border border-primary/10">{airport.icao_code}</span>
                                            {airport.iata_code && <span className="text-xs text-slate-400 font-medium">{airport.iata_code}</span>}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="text-sm font-semibold text-slate-800">{airport.name}</div>
                                        <div className="text-[10px] text-slate-400 uppercase font-bold">{airport.type?.replace('_', ' ')}</div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="text-sm text-slate-600">{airport.city}</div>
                                        <div className="text-xs text-slate-400 font-medium">{airport.country}</div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex gap-1">
                                            <button
                                                onClick={() => handleEdit(airport)}
                                                className="p-2 text-slate-400 hover:text-primary hover:bg-slate-100 rounded-lg transition-all"
                                                title="Editar"
                                            >
                                                <FaEdit />
                                            </button>
                                            <button
                                                onClick={() => handleDelete(airport.id)}
                                                className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-all"
                                                title="Eliminar"
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

                {/* CONTROLES DE PAGINACIÓN */}
                <div className="p-4 border-t border-slate-50 flex justify-between items-center bg-slate-50/30">
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                        Mostrando <span className="text-slate-700">{(page - 1) * pageSize + 1} - {Math.min(page * pageSize, total)}</span> de {total}
                    </span>
                    <div className="flex gap-2">
                        <button
                            disabled={page === 1}
                            onClick={() => setPage(p => p - 1)}
                            className="px-4 py-1.5 text-sm font-bold text-slate-600 bg-white border border-slate-200 rounded-lg disabled:opacity-30 hover:shadow-sm transition-all"
                        >
                            Anterior
                        </button>
                        <button
                            disabled={page * pageSize >= total}
                            onClick={() => setPage(p => p + 1)}
                            className="px-4 py-1.5 text-sm font-bold text-primary bg-white border border-primary/20 rounded-lg disabled:opacity-30 hover:shadow-sm transition-all"
                        >
                            Siguiente
                        </button>
                    </div>
                </div>
            </div>

            {/* MODAL DE EDICIÓN / CREACIÓN */}
            {showModal && (
                <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-[100] p-4 animate-in fade-in duration-300">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[95vh] overflow-hidden flex flex-col animate-in zoom-in-95 duration-300">
                        <div className="p-6 border-b border-slate-50 flex justify-between items-center bg-slate-50/50">
                            <h2 className="text-xl font-bold text-slate-800">
                                {editingId ? 'Actualizar Aeropuerto' : 'Nuevo Registro de Aeropuerto'}
                            </h2>
                            <button onClick={() => setShowModal(false)} className="p-2 hover:bg-slate-200 rounded-full text-slate-400 transition-colors">
                                <FaTimes />
                            </button>
                        </div>

                        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-1.5">
                                    <label className="block text-sm font-bold text-slate-700">Nombre de la Terminal *</label>
                                    <input
                                        type="text" required
                                        className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                                        value={formData.name}
                                        onChange={e => setFormData({ ...formData, name: e.target.value })}
                                        placeholder="Ej: Aeropuerto Internacional El Dorado"
                                    />
                                </div>
                                <div className="space-y-1.5">
                                    <label className="block text-sm font-bold text-slate-700">Ciudad de Operación</label>
                                    <input
                                        type="text"
                                        className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                                        value={formData.city}
                                        onChange={e => setFormData({ ...formData, city: e.target.value })}
                                        placeholder="Ej: Bogotá"
                                    />
                                </div>
                                <div className="space-y-1.5">
                                    <label className="block text-sm font-bold text-slate-700">País / Región</label>
                                    <input
                                        type="text"
                                        className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                                        value={formData.country}
                                        onChange={e => setFormData({ ...formData, country: e.target.value })}
                                        placeholder="Ej: Colombia"
                                    />
                                </div>
                                <div className="space-y-1.5">
                                    <label className="block text-sm font-bold text-slate-700">Tipo de Instalación</label>
                                    <select
                                        className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary/20 outline-none transition-all cursor-pointer"
                                        value={formData.type}
                                        onChange={e => setFormData({ ...formData, type: e.target.value })}
                                    >
                                        <option value="small_airport">Pequeño Aeropuerto</option>
                                        <option value="medium_airport">Mediano Aeropuerto</option>
                                        <option value="large_airport">Gran Aeropuerto Hub</option>
                                        <option value="heliport">Helipuerto</option>
                                    </select>
                                </div>
                                <div className="space-y-1.5">
                                    <label className="block text-sm font-bold text-slate-700">Código OACI (ICAO) *</label>
                                    <input
                                        type="text" required
                                        className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary/20 outline-none transition-all uppercase font-mono"
                                        value={formData.icao_code}
                                        onChange={e => setFormData({ ...formData, icao_code: e.target.value })}
                                        placeholder="Ej: SKBO"
                                    />
                                </div>
                                <div className="space-y-1.5">
                                    <label className="block text-sm font-bold text-slate-700">Código IATA</label>
                                    <input
                                        type="text"
                                        className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary/20 outline-none transition-all uppercase font-mono"
                                        value={formData.iata_code}
                                        onChange={e => setFormData({ ...formData, iata_code: e.target.value })}
                                        placeholder="Ej: BOG"
                                    />
                                </div>
                            </div>

                            <div className="flex justify-end gap-3 pt-6 border-t border-slate-100">
                                <button
                                    type="button"
                                    onClick={() => setShowModal(false)}
                                    className="px-6 py-2.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-xl font-semibold transition-all"
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    className="px-8 py-2.5 bg-primary text-white hover:bg-primary-dark rounded-xl font-bold shadow-lg shadow-primary/20 transition-all active:scale-95"
                                >
                                    {editingId ? 'Guardar Cambios' : 'Crear Aeropuerto'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};
