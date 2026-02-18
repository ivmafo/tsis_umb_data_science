import { RegionsList } from '../components/regions/RegionsList';

export const RegionsView = () => {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-slate-800">Gestión de Regiones</h1>
                    <p className="text-slate-500 mt-1">Administración de FIRs y sectores aéreos.</p>
                </div>
            </div>

            <RegionsList />
        </div>
    );
};
