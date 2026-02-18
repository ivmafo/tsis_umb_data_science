import { RegionsList } from '../components/regions/RegionsList';

/**
 * Vista de Gestión: Regiones Aeronáuticas (FIR).
 * 
 * Este componente actúa como el contenedor principal para la administración de 
 * regiones. Su rol es estructural, proporcionando el contexto de cabecera y 
 * delegando la complejidad del CRUD al componente de bajo nivel `RegionsList`.
 */
export const RegionsView = () => {
    return (
        <div className="space-y-6">
            <header className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-slate-800">Maestro de Regiones</h1>
                    <p className="text-slate-500 mt-1">Configuración de FIRs y polígonos de responsabilidad aérea.</p>
                </div>
            </header>

            {/* Inyección del controlador de lista reactiva */}
            <RegionsList />
        </div>
    );
};
