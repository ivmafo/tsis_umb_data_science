import { useState, useEffect } from 'react';
import { FaSearch, FaPlus, FaTrash, FaTimes, FaEdit } from 'react-icons/fa';
import { getAirports, createAirport, deleteAirport, updateAirport, type Airport } from '../api';

export const AirportsView = () => {
    const [airports, setAirports] = useState<Airport[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [page, setPage] = useState(1);
    const [total, setTotal] = useState(0);
    const pageSize = 10;

    // Modal State
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

    const resetForm = () => {
        setFormData({
            icao_code: '', iata_code: '', name: '', city: '', country: '',
            type: 'small_airport', latitude: 0, longitude: 0, altitude: 0, timezone: 0, dst: 'U', source: 'User'
        });
        setEditingId(null);
    };

    const fetchAirports = async () => {
        setLoading(true);
        try {
            const data = await getAirports(page, pageSize, search);
            setAirports(data.data);
            setTotal(data.total);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const timer = setTimeout(() => {
            fetchAirports();
        }, 300); // 300ms debounce
        return () => clearTimeout(timer);
    }, [page, search]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            if (!formData.name || !formData.icao_code) {
                alert("Nombre y Código ICAO son requeridos");
                return;
            }

            if (editingId) {
                await updateAirport(editingId, formData);
            } else {
                await createAirport(formData as Airport);
            }

            setShowModal(false);
            resetForm();
            fetchAirports();
        } catch (error) {
            console.error("Failed to save airport", error);
            alert("Error al guardar aeropuerto");
        }
    };

    const handleEdit = (airport: Airport) => {
        setEditingId(airport.id);
        setFormData({
            icao_code: airport.icao_code,
            iata_code: airport.iata_code || '',
            name: airport.name,
            city: airport.city || '',
            country: airport.country || '',
            type: airport.type || 'small_airport',
            // Add other fields if present in table or need fetching
            latitude: airport.latitude || 0,
            longitude: airport.longitude || 0,
            altitude: airport.altitude || 0,
            timezone: airport.timezone || 0,
            dst: airport.dst || 'U',
            source: airport.source || 'User'
        });
        setShowModal(true);
    };

    const handleDelete = async (id: number) => {
        if (!confirm("¿Estás seguro de eliminar este aeropuerto?")) return;
        try {
            await deleteAirport(id);
            fetchAirports();
        } catch (error) {
            console.error("Failed to delete", error);
        }
    };

    const openCreateModal = () => {
        resetForm();
        setShowModal(true);
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500 relative">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-slate-800">Aeropuertos</h1>
                    <p className="text-slate-500 mt-1">Gestión de la base de datos de aeropuertos</p>
                </div>
                <button
                    onClick={openCreateModal}
                    className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark transition-colors shadow-lg shadow-primary/30"
                >
                    <FaPlus />
                    <span>Nuevo Aeropuerto</span>
                </button>
            </div>

            {/* Search Bar */}
            <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-100 flex gap-4">
                <div className="relative flex-1">
                    <FaSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                        type="text"
                        placeholder="Buscar por nombre, código o ciudad..."
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
                                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Códigos</th>
                                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Nombre</th>
                                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Ubicación</th>
                                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Acciones</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {loading ? (
                                <tr><td colSpan={5} className="p-8 text-center text-slate-500">Cargando...</td></tr>
                            ) : airports.map((airport) => (
                                <tr key={airport.id} className="hover:bg-slate-50/50 transition-colors">
                                    <td className="px-6 py-4 text-sm text-slate-500">#{airport.id}</td>
                                    <td className="px-6 py-4">
                                        <div className="flex flex-col">
                                            <span className="text-sm font-medium text-slate-800">{airport.icao_code}</span>
                                            <span className="text-xs text-slate-500">{airport.iata_code}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-slate-800 font-medium">{airport.name}</td>
                                    <td className="px-6 py-4 text-sm text-slate-600">
                                        {airport.city}, {airport.country}
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => handleEdit(airport)}
                                                className="p-1.5 text-blue-600 hover:bg-blue-50 rounded"
                                            >
                                                <FaEdit />
                                            </button>
                                            <button
                                                onClick={() => handleDelete(airport.id)}
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
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                        <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                            <h2 className="text-xl font-bold text-slate-800">
                                {editingId ? 'Editar Aeropuerto' : 'Nuevo Aeropuerto'}
                            </h2>
                            <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600">
                                <FaTimes />
                            </button>
                        </div>

                        <form onSubmit={handleSubmit} className="p-6 space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Nombre</label>
                                    <input
                                        type="text" required
                                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 outline-none"
                                        value={formData.name}
                                        onChange={e => setFormData({ ...formData, name: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Ciudad</label>
                                    <input
                                        type="text"
                                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 outline-none"
                                        value={formData.city}
                                        onChange={e => setFormData({ ...formData, city: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">País</label>
                                    <input
                                        type="text"
                                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 outline-none"
                                        value={formData.country}
                                        onChange={e => setFormData({ ...formData, country: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Tipo</label>
                                    <select
                                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 outline-none"
                                        value={formData.type}
                                        onChange={e => setFormData({ ...formData, type: e.target.value })}
                                    >
                                        <option value="small_airport">Small Airport</option>
                                        <option value="medium_airport">Medium Airport</option>
                                        <option value="large_airport">Large Airport</option>
                                        <option value="heliport">Heliport</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Código ICAO</label>
                                    <input
                                        type="text" required
                                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 outline-none uppercase"
                                        value={formData.icao_code}
                                        onChange={e => setFormData({ ...formData, icao_code: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Código IATA</label>
                                    <input
                                        type="text"
                                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 outline-none uppercase"
                                        value={formData.iata_code}
                                        onChange={e => setFormData({ ...formData, iata_code: e.target.value })}
                                    />
                                </div>
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
                                    Guardar Aeropuerto
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};
