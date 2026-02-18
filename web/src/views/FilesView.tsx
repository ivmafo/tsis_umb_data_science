import { FileList } from '../components/FileList';

export const FilesView = () => {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-slate-800">Listado de Archivos</h1>
                    <p className="text-slate-500 mt-1">Gestiona y visualiza los datos cargados en el sistema.</p>
                </div>
            </div>

            {/* Reusing existing component, modified for light theme context via props/css if needed, 
                but defaulting to existing styles which are glassmophic. 
                I might need to adjust Global CSS to support light layout background. */}
            <FileList />
        </div>
    );
};
