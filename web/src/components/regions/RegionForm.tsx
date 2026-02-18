import { useState, useEffect } from 'react';
import type { Region } from '../../api';
import { Save, X } from 'lucide-react';

interface RegionFormProps {
    /** Datos de la región en caso de edición; null para creación de nueva entidad */
    initialData?: Region | null;
    /** Control de visibilidad del modal */
    isOpen: boolean;
    /** Callback de cierre y cleanup del modal */
    onClose: () => void;
    /** Promesa de persistencia que interactúa con el API de regiones */
    onSubmit: (data: Region) => Promise<void>;
}

/**
 * Componente de Entrada: Formulario Maestros de Regiones.
 * 
 * Este componente orquestal permite la definición estructural de regiones
 * aeronáuticas, capturando metadatos críticos para la segmentación del 
 * análisis de capacidad y tráfico.
 * 
 * Atributos Técnicos:
 * - Sincronización de Efecto: Reinicia el estado interno al alternar 'initialData'.
 * - Casting de Tipos: Normaliza el nivel de vuelo (FL) a entero para DuckDB.
 * - Validación de Integridad: Previene el envío de campos clave nulos (Name/Code).
 * 
 * @param props - Configuración y gestores de evento.
 */
export const RegionForm = ({ isOpen, onClose, onSubmit, initialData }: RegionFormProps) => {
    // ESTADOS: Control granular de los atributos de la entidad Region
    const [name, setName] = useState('');
    const [code, setCode] = useState('');
    const [minLevel, setMinLevel] = useState('');
    const [description, setDescription] = useState('');

    // loading: Bloqueo de concurrencia durante la transacción de red
    const [loading, setLoading] = useState(false);

    /**
     * Reacciona a cambios en los datos de entrada para poblar el formulario.
     */
    useEffect(() => {
        if (initialData) {
            // Mapeo de datos para modo Edición
            setName(initialData.name || '');
            setCode(initialData.code || '');
            setMinLevel(initialData.nivel_min?.toString() || '');
            setDescription(initialData.description || '');
        } else {
            // Limpieza para modo Creación
            setName('');
            setCode('');
            setMinLevel('');
            setDescription('');
        }
    }, [initialData, isOpen]);

    /**
     * Orquestador de persistencia.
     */
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        // Reglas de Negocio: Campos obligatorios mínimos
        if (!name || !code) {
            alert("Atención: El Nombre y Código son requeridos para la indexación geográfica.");
            return;
        }

        setLoading(true);
        try {
            await onSubmit({
                name,
                code,
                nivel_min: minLevel ? parseInt(minLevel) : 0,
                description
            });
            onClose(); // Cleanup tras éxito
        } catch (error) {
            console.error("Fallo crítico en guardado de región:", error);
            alert("Error: Verifique la unicidad del código u otros parámetros técnicos.");
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-300">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-in zoom-in-95 duration-300">
                {/* CABECERA DEL MODAL */}
                <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
                    <h3 className="text-xl font-bold text-slate-800">
                        {initialData ? 'Editar Región' : 'Nueva Región'}
                    </h3>
                    <button onClick={onClose} className="p-2 hover:bg-slate-200 rounded-full transition-colors">
                        <X className="w-5 h-5 text-slate-500" />
                    </button>
                </div>

                {/* CUERPO DEL FORMULARIO */}
                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    <div>
                        <label className="block text-sm font-semibold text-slate-700 mb-1">Nombre de la Región *</label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                            placeholder="Ej. Región Andina"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-semibold text-slate-700 mb-1">Código OACI/Identificador *</label>
                        <input
                            type="text"
                            value={code}
                            onChange={(e) => setCode(e.target.value)}
                            className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                            placeholder="Ej. SKNV"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-semibold text-slate-700 mb-1">Nivel de Vuelo Mínimo (FL)</label>
                        <input
                            type="number"
                            value={minLevel}
                            onChange={(e) => setMinLevel(e.target.value)}
                            className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                            placeholder="Ej. 190"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-semibold text-slate-700 mb-1">Descripción / Notas</label>
                        <textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all min-h-[100px]"
                            placeholder="Información adicional sobre la cobertura geográfica..."
                        />
                    </div>

                    {/* ACCIONES DEL FORMULARIO */}
                    <div className="flex gap-3 pt-4 border-t border-slate-100">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-2.5 bg-slate-100 text-slate-600 font-semibold rounded-xl hover:bg-slate-200 transition-colors"
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-primary text-white font-semibold rounded-xl hover:bg-primary-dark transition-all disabled:opacity-50 shadow-lg shadow-primary/20"
                        >
                            <Save className="w-4 h-4" />
                            {loading ? 'Guardando...' : 'Guardar'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};
