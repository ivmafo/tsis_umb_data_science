import { useState, useEffect } from 'react';
import { getCalendarEvents, saveCalendarEvent, deleteCalendarEvent } from '../api';
import type { CalendarEvent } from '../api';
import { FaCalendarAlt, FaPlus, FaTrash, FaInfoCircle, FaCalendarCheck } from 'react-icons/fa';

export const CalendarEventsView = () => {
    const [events, setEvents] = useState<CalendarEvent[]>([]);
    const [year, setYear] = useState<number>(new Date().getFullYear());
    const [loading, setLoading] = useState(false);
    
    // Form State
    const [fecha, setFecha] = useState('');
    const [descripcion, setDescripcion] = useState('');
    const [tipo, setTipo] = useState('festivo');
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);

    const loadEvents = async () => {
        setLoading(true);
        try {
            const data = await getCalendarEvents(year);
            setEvents(data);
        } catch (err) {
            console.error("Error cargando eventos de calendario:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadEvents();
    }, [year]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!fecha || !descripcion || !tipo) {
            setError("Por favor, rellene todos los campos del formulario.");
            return;
        }

        setError(null);
        setSuccessMessage(null);
        setSubmitting(true);

        try {
            await saveCalendarEvent({
                fecha,
                descripcion,
                tipo
            });
            setSuccessMessage("Evento registrado exitosamente en el calendario.");
            setFecha('');
            setDescripcion('');
            loadEvents();
            
            // Auto hide success msg
            setTimeout(() => setSuccessMessage(null), 5000);
        } catch (err: any) {
            setError(err.response?.data?.detail || "Fallo técnico al registrar el evento en el calendario.");
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (dateStr: string) => {
        if (confirm(`¿Está seguro de que desea eliminar el evento personalizado para la fecha ${dateStr}?`)) {
            try {
                await deleteCalendarEvent(dateStr);
                loadEvents();
            } catch (err) {
                console.error("Error al eliminar evento:", err);
                alert("No se pudo eliminar el evento personalizado.");
            }
        }
    };

    const getBadgeStyle = (type: string) => {
        switch (type) {
            case 'festivo':
                return 'bg-rose-100 text-rose-800 border border-rose-200';
            case 'receso':
                return 'bg-amber-100 text-amber-800 border border-amber-200';
            case 'fin_de_ano':
                return 'bg-indigo-100 text-indigo-800 border border-indigo-200';
            default:
                return 'bg-slate-100 text-slate-800 border border-slate-200';
        }
    };

    const formatTypeLabel = (type: string) => {
        switch (type) {
            case 'festivo': return 'Festivo / Puente';
            case 'receso': return 'Receso Escolar';
            case 'fin_de_ano': return 'Fin de Año';
            default: return 'Personalizado';
        }
    };

    return (
        <div className="p-8 space-y-8 max-w-7xl mx-auto">
            {/* Cabecera Principal */}
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-200 pb-6">
                <div>
                    <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-3">
                        <FaCalendarAlt className="text-indigo-600" />
                        Calendario y Temporadas
                    </h1>
                    <p className="text-slate-500 mt-1">
                        Parametrización del calendario aeronáutico de Colombia y eventos de alta afluencia para el motor predictivo.
                    </p>
                </div>

                {/* Filtro de Año */}
                <div className="flex items-center gap-3 bg-white px-4 py-2 rounded-xl shadow-sm border border-slate-200">
                    <span className="text-sm font-semibold text-slate-700">Año de Consulta:</span>
                    <select 
                        value={year}
                        onChange={(e) => setYear(Number(e.target.value))}
                        className="bg-transparent font-bold text-indigo-600 focus:outline-none border-b-2 border-transparent focus:border-indigo-600 transition-colors"
                    >
                        {[2024, 2025, 2026, 2027, 2028].map(y => (
                            <option key={y} value={y}>{y}</option>
                        ))}
                    </select>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Panel del Formulario (Personalizar Calendario) */}
                <div className="lg:col-span-1 bg-white p-6 rounded-2xl shadow-xl border border-slate-100 h-fit space-y-6">
                    <div>
                        <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                            <FaPlus className="text-indigo-500 text-sm" />
                            Agregar Evento
                        </h2>
                        <p className="text-xs text-slate-400 mt-1">
                            Introduce eventos locales o temporadas para que los algoritmos de IA los reconozcan en sus simulaciones.
                        </p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        {error && (
                            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl flex items-center gap-2">
                                <FaInfoCircle className="flex-shrink-0" />
                                <span>{error}</span>
                            </div>
                        )}

                        {successMessage && (
                            <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs rounded-xl flex items-center gap-2">
                                <FaCalendarCheck className="flex-shrink-0" />
                                <span>{successMessage}</span>
                            </div>
                        )}

                        <div>
                            <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-2">Fecha del Evento</label>
                            <input 
                                type="date" 
                                value={fecha}
                                onChange={(e) => setFecha(e.target.value)}
                                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all font-medium text-slate-700"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-2">Descripción</label>
                            <input 
                                type="text"
                                placeholder="Ej. Semana Santa, Fiesta Patronal, Paro"
                                value={descripcion}
                                onChange={(e) => setDescripcion(e.target.value)}
                                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all font-medium text-slate-700"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-2">Tipo de Impacto</label>
                            <select 
                                value={tipo}
                                onChange={(e) => setTipo(e.target.value)}
                                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all font-medium text-slate-700"
                                required
                            >
                                <option value="festivo">Festivo / Puente Nacional</option>
                                <option value="receso">Semana de Receso Escolar</option>
                                <option value="fin_de_ano">Temporada de Fin de Año</option>
                                <option value="custom">Otro Personalizado</option>
                            </select>
                        </div>

                        <button 
                            type="submit"
                            disabled={submitting}
                            className="w-full bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 text-white font-bold py-3 px-4 rounded-xl shadow-lg shadow-indigo-600/10 hover:shadow-indigo-600/20 transition-all text-sm flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {submitting ? 'Guardando...' : 'Registrar en Calendario'}
                        </button>
                    </form>
                </div>

                {/* Tabla de Eventos Mezclados */}
                <div className="lg:col-span-2 bg-white p-6 rounded-2xl shadow-xl border border-slate-100 space-y-6">
                    <div>
                        <h2 className="text-xl font-bold text-slate-800">Calendario Unificado ({year})</h2>
                        <p className="text-xs text-slate-400 mt-1">
                            Calendario activo que combina los días no laborables del gobierno colombiano (generados automáticamente) y tus personalizaciones.
                        </p>
                    </div>

                    {loading ? (
                        <div className="flex flex-col items-center justify-center p-16 space-y-4">
                            <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                            <span className="text-indigo-600 font-medium animate-pulse text-sm">Cargando base de datos y calendario...</span>
                        </div>
                    ) : events.length === 0 ? (
                        <div className="text-center py-16 bg-slate-50 rounded-2xl border border-dashed border-slate-200 p-8">
                            <FaCalendarAlt className="mx-auto text-slate-300 text-5xl mb-4" />
                            <p className="text-slate-600 font-bold">No se encontraron eventos para el año {year}</p>
                            <p className="text-slate-400 text-xs mt-1">
                                Intente cambiar de año o registre un evento personalizado en el panel de la izquierda.
                            </p>
                        </div>
                    ) : (
                        <div className="overflow-hidden border border-slate-100 rounded-xl">
                            <div className="overflow-x-auto max-h-[500px]">
                                <table className="w-full text-left border-collapse">
                                    <thead>
                                        <tr className="bg-slate-50 border-b border-slate-100">
                                            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Fecha</th>
                                            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Nombre del Evento</th>
                                            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Tipo</th>
                                            <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Procedencia</th>
                                            <th className="px-6 py-4 text-xs font-bold text-slate-500 text-right uppercase tracking-wider">Acción</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-100">
                                        {events.map((event) => (
                                            <tr key={event.fecha} className="hover:bg-slate-50/50 transition-colors">
                                                <td className="px-6 py-4 text-sm font-semibold text-slate-700 whitespace-nowrap">
                                                    {event.fecha}
                                                </td>
                                                <td className="px-6 py-4 text-sm font-medium text-slate-800">
                                                    {event.descripcion}
                                                </td>
                                                <td className="px-6 py-4 text-xs">
                                                    <span className={`px-2.5 py-1 rounded-full font-bold uppercase tracking-wide text-[10px] ${getBadgeStyle(event.tipo)}`}>
                                                        {formatTypeLabel(event.tipo)}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 text-xs">
                                                    {event.es_oficial ? (
                                                        <span className="bg-emerald-50 text-emerald-700 border border-emerald-100 px-2 py-0.5 rounded font-medium">
                                                            Oficial (Librería)
                                                        </span>
                                                    ) : (
                                                        <span className="bg-blue-50 text-blue-700 border border-blue-100 px-2 py-0.5 rounded font-medium">
                                                            Manual (DuckDB)
                                                        </span>
                                                    )}
                                                </td>
                                                <td className="px-6 py-4 text-right whitespace-nowrap">
                                                    {event.es_oficial ? (
                                                        <span className="text-xs text-slate-400 italic">Inmutable</span>
                                                    ) : (
                                                        <button 
                                                            onClick={() => handleDelete(event.fecha)}
                                                            className="text-rose-500 hover:text-rose-700 p-1.5 rounded-lg hover:bg-rose-50 transition-colors inline-flex cursor-pointer"
                                                            title="Eliminar evento personalizado"
                                                        >
                                                            <FaTrash className="w-3.5 h-3.5" />
                                                        </button>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
