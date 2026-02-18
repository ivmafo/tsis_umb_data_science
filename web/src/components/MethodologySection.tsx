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

export const MethodologySection: React.FC<MethodologyProps> = ({
    title,
    algorithm,
    variables,
    filters,
    dataVolume,
    explanation,
    visible = true
}) => {
    if (!visible) return null;

    return (
        <div className="bg-slate-50 p-6 rounded-lg border border-slate-200 mt-8">
            <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
                📘 Metodología: {title}
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                    <div>
                        <span className="font-semibold text-slate-600 block text-sm">Algoritmo Utilizado</span>
                        <p className="text-slate-800 font-medium">{algorithm}</p>
                    </div>
                    <div>
                        <span className="font-semibold text-slate-600 block text-sm">Variables Consideradas</span>
                        <ul className="list-disc list-inside text-slate-700 text-sm mt-1">
                            {variables.map((v, i) => (
                                <li key={i}>{v}</li>
                            ))}
                        </ul>
                    </div>
                </div>

                <div className="space-y-4">
                    <div>
                        <span className="font-semibold text-slate-600 block text-sm">Filtros Aplicados</span>
                        <p className="text-slate-700 text-sm">{filters}</p>
                    </div>
                    <div>
                        <span className="font-semibold text-slate-600 block text-sm">Volumen de Datos (Muestreo)</span>
                        <p className="text-slate-700 text-sm">{dataVolume}</p>
                    </div>
                </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-200">
                <span className="font-semibold text-slate-600 block text-sm mb-2">¿Cómo funciona? (Explicación Detallada)</span>
                <p className="text-slate-700 leading-relaxed bg-blue-50 p-4 rounded-md text-sm border border-blue-100">
                    {explanation}
                </p>
            </div>
        </div>
    );
};
