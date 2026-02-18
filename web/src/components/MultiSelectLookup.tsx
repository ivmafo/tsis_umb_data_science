import { useState, useEffect, useRef } from 'react';
import { X, Search, Check, Loader2 } from 'lucide-react';

interface Option {
    id: number | string;
    label: string;
    value: any;
}

interface MultiSelectLookupProps {
    label: string;
    placeholder: string;
    value: Option[];
    onChange: (value: Option[]) => void;
    fetchOptions: (query: string) => Promise<Option[]>;
    renderOption?: (option: Option) => React.ReactNode;
}

export const MultiSelectLookup = ({
    label,
    placeholder,
    value,
    onChange,
    fetchOptions,
    renderOption
}: MultiSelectLookupProps) => {
    const [query, setQuery] = useState('');
    const [options, setOptions] = useState<Option[]>([]);
    const [loading, setLoading] = useState(false);
    const [isOpen, setIsOpen] = useState(false);
    const wrapperRef = useRef<HTMLDivElement>(null);

    // Click outside to close
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    // Debounced search
    useEffect(() => {
        const timeoutId = setTimeout(async () => {
            if (query.trim().length >= 2) {
                setLoading(true);
                try {
                    const results = await fetchOptions(query);
                    setOptions(results);
                } catch (error) {
                    console.error("Error fetching options:", error);
                    setOptions([]);
                } finally {
                    setLoading(false);
                }
            } else if (query.trim().length === 0) {
                setOptions([]);
            }
        }, 300);

        return () => clearTimeout(timeoutId);
    }, [query, fetchOptions]);

    const handleSelect = (option: Option) => {
        if (!value.find(v => v.id === option.id)) {
            onChange([...value, option]);
        }
        setQuery('');
        setIsOpen(false);
    };

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
