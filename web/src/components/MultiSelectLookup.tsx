import { useState, useEffect, useRef } from 'react';
import { X, Search, Check, Loader2 } from 'lucide-react';

interface Option {
    /** Identificador único para reconciliación de React (Key) */
    id: number | string;
    /** Texto descriptivo (Label) visible en la UI */
    label: string;
    /** Valor subyacente (Cualquier tipo de dato de negocio) */
    value: any;
}

interface MultiSelectLookupProps {
    /** Etiqueta superior del campo de búsqueda */
    label: string;
    /** Texto de ayuda interno del input */
    placeholder: string;
    /** Colección de opciones actualmente seleccionadas (Estado controlado) */
    value: Option[];
    /** Callback de sincronización hacia el componente padre */
    onChange: (value: Option[]) => void;
    /** Inyector de dependencia para búsqueda asíncrona (API Call) */
    fetchOptions: (query: string) => Promise<Option[]>;
    /** Permite personalizar el renderizado de cada fila de resultados */
    renderOption?: (option: Option) => React.ReactNode;
}

/**
 * Componente de Infraestructura: Buscador Multinivel con Autocompletado.
 * 
 * Este componente es el motor de filtrado del Dashboard, permitiendo
 * seleccionar múltiples entidades (Aeropuertos, Aerolíneas, etc.) mediante
 * una interfaz de búsqueda asíncrona con tags.
 * 
 * Atributos Técnicos:
 * - Debounce nativo (300ms) para control de flujo de peticiones.
 * - Gestión de foco y cierre por click-outside mediante Refs.
 * - Prevención de duplicados en la colección de salida.
 * 
 * @param props - Configuración de búsqueda y estado.
 */
export const MultiSelectLookup = ({
    label,
    placeholder,
    value,
    onChange,
    fetchOptions,
    renderOption
}: MultiSelectLookupProps) => {
    // query: Término de búsqueda crudo ingresado por el operador
    const [query, setQuery] = useState('');

    // options: Pool de resultados sugeridos por el servidor para la consulta actual
    const [options, setOptions] = useState<Option[]>([]);

    // loading: Feedback visual de espera durante la resolución de la promesa de búsqueda
    const [loading, setLoading] = useState(false);

    // isOpen: Control de visibilidad del Dropdown de sugerencias
    const [isOpen, setIsOpen] = useState(false);

    const wrapperRef = useRef<HTMLDivElement>(null);

    // Mecanismo de gestión de cierre heurístico (Click fuera del área interactiva)
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    // Motor de Búsqueda Predictiva con Debounce
    useEffect(() => {
        const timeoutId = setTimeout(async () => {
            // Umbral de activación: Mínimo 2 caracteres para reducir ruido en el API
            if (query.trim().length >= 2) {
                setLoading(true);
                try {
                    const results = await fetchOptions(query);
                    setOptions(results);
                } catch (error) {
                    console.error("Fallo técnico en recuperación de opciones:", error);
                    setOptions([]);
                } finally {
                    setLoading(false);
                }
            } else if (query.trim().length === 0) {
                setOptions([]); // Limpieza de pool al vaciar el input
            }
        }, 300);

        return () => clearTimeout(timeoutId);
    }, [query, fetchOptions]);

    /**
     * Agrega un nuevo elemento al pool de selección si no existe previamente.
     * @param option - Elemento seleccionado desde el dropdown.
     */
    const handleSelect = (option: Option) => {
        if (!value.find(v => v.id === option.id)) {
            onChange([...value, option]);
        }
        setQuery('');
        setIsOpen(false);
    };

    /**
     * Elimina un tag específico del pool de selección.
     * @param id - Identificador del elemento a purgar.
     */
    const handleRemove = (id: number | string) => {
        onChange(value.filter(v => v.id !== id));
    };

    return (
        <div className="w-full" ref={wrapperRef}>
            <label className="block text-sm font-medium text-slate-700 mb-1">{label}</label>

            {/* Selected Tags */}
            {value.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-2">
                    {value.map((item) => (
                        <span key={item.id} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-100">
                            {item.label}
                            <button
                                onClick={() => handleRemove(item.id)}
                                className="hover:bg-indigo-200 rounded-full p-0.5 transition-colors"
                            >
                                <X className="w-3 h-3" />
                            </button>
                        </span>
                    ))}
                </div>
            )}

            {/* Search Input */}
            <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Search className="h-4 w-4 text-slate-400" />
                </div>
                <input
                    type="text"
                    className="block w-full pl-10 pr-3 py-2 border border-slate-300 rounded-md leading-5 bg-white placeholder-slate-400 focus:outline-none focus:placeholder-slate-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 sm:text-sm transition duration-150 ease-in-out"
                    placeholder={placeholder}
                    value={query}
                    onChange={(e) => {
                        setQuery(e.target.value);
                        setIsOpen(true);
                    }}
                    onFocus={() => setIsOpen(true)}
                />
                {loading && (
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                        <Loader2 className="h-4 w-4 text-slate-400 animate-spin" />
                    </div>
                )}
            </div>

            {/* Dropdown Results */}
            {isOpen && (query.length >= 2 || options.length > 0) && (
                <div className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm">
                    {loading ? (
                        <div className="relative cursor-default select-none py-2 px-4 text-slate-500">Buscando...</div>
                    ) : options.length === 0 ? (
                        <div className="relative cursor-default select-none py-2 px-4 text-slate-500">No se encontraron resultados</div>
                    ) : (
                        options.map((option) => {
                            const isSelected = value.some(v => v.id === option.id);
                            return (
                                <div
                                    key={option.id}
                                    className={`cursor-pointer select-none relative py-2 pl-3 pr-9 ${isSelected ? 'bg-indigo-50 text-indigo-900' : 'text-slate-900 hover:bg-slate-50'}`}
                                    onClick={() => !isSelected && handleSelect(option)}
                                >
                                    {renderOption ? renderOption(option) : <span className="block truncate">{option.label}</span>}

                                    {isSelected && (
                                        <span className="absolute inset-y-0 right-0 flex items-center pr-4 text-indigo-600">
                                            <Check className="h-4 w-4" />
                                        </span>
                                    )}
                                </div>
                            );
                        })
                    )}
                </div>
            )}
        </div>
    );
};
