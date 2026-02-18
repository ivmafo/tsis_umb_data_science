import React from 'react';

interface MethodologyProps {
    title: string;
    algorithm: string;
    variables: string[];
    filters: string;
    dataVolume: string;
    explanation: string;
    visible?: boolean;
}

interface MethodologyProps {
    /** Título descriptivo del análisis (ej: "Saturación de Sector") */
    title: string;
    /** Nombre del algoritmo o modelo matemático (ej: "Fourier", "Random Forest") */
    algorithm: string;
    /** Lista de parámetros de entrada considerados en el cálculo */
    variables: string[];
    /** Resumen textual de los filtros activos en la UI */
    filters: string;
    /** Descripción de la muestra de datos (ej: "3 años de historia") */
    dataVolume: string;
    /** Narrativa detallada sobre el funcionamiento interno de la lógica */
    explanation: string;
    /** Control de visibilidad condicional */
    visible?: boolean;
}

/**
 * Componente Educativo: Sección de Metodología.
 * 
 * Este componente es fundamental para la transparencia técnica del sistema.
 * Desglosa el 'cómo' y el 'por qué' de los datos visualizados, permitiendo
 * que el analista de ATC comprenda el rigor detrás de cada métrica.
 * 
 * @param props - Metadatos técnicos del cálculo actual.
 */
export const MethodologySection: React.FC<MethodologyProps> = ({
    title,
    algorithm,
    variables,
    filters,
    dataVolume,
    explanation,
    visible = true
}) => {
    // Si no es visible (ej: en carga o error grave), no renderiza nada para limpiar la UI
    if (!visible) return null;

    return (
        <div className="bg-slate-50 p-6 rounded-lg border border-slate-200 mt-8 shadow-inner">
            <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
                <span className="text-blue-500">📘</span> Metodología: {title}
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Columna de Lógica Algorítmica */}
                <div className="space-y-4">
                    <div>
                        <span className="font-semibold text-slate-600 block text-xs uppercase tracking-wider">Algoritmo / Modelo</span>
                        <p className="text-slate-800 font-medium text-sm">{algorithm}</p>
                    </div>
                    <div>
                        <span className="font-semibold text-slate-600 block text-xs uppercase tracking-wider">Dimensión de Datos</span>
                        <ul className="list-disc list-inside text-slate-700 text-sm mt-2 space-y-1">
                            {variables.map((v, i) => (
                                <li key={i}>{v}</li>
                            ))}
                        </ul>
                    </div>
                </div>

                {/* Columna de Contexto Operativo */}
                <div className="space-y-4">
                    <div>
                        <span className="font-semibold text-slate-600 block text-xs uppercase tracking-wider">Filtros Activos</span>
                        <p className="text-slate-700 text-sm italic">"{filters}"</p>
                    </div>
                    <div>
                        <span className="font-semibold text-slate-600 block text-xs uppercase tracking-wider">Volumen de Muestra</span>
                        <p className="text-slate-700 text-sm font-medium">{dataVolume}</p>
                    </div>
                </div>
            </div>

            {/* Bloque de Explicación técnica descriptiva */}
            <div className="mt-6 pt-4 border-t border-slate-200">
                <span className="font-semibold text-slate-600 block text-xs uppercase tracking-wider mb-3">Descripción Funcional</span>
                <p className="text-slate-700 leading-relaxed bg-white p-4 rounded-md text-sm border border-slate-100 italic">
                    {explanation}
                </p>
            </div>
        </div>
    );
};
