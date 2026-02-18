import { FileList } from '../components/FileList';

/**
 * Vista de Gestión: Almacenamiento y Archivos de Datos.
 * 
 * Este componente es el contenedor estructural para la administración de 
 * los volúmenes de datos ingestados. Su propósito es organizar el contexto
 * visual para `FileList`, permitiendo la inspección y purga de archivos.
 */
export const FilesView = () => {
    return (
        <div className="space-y-6">
            <header className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-slate-800">Repositorio de Archivos</h1>
                    <p className="text-slate-500 mt-1">Inspección y gestión de volúmenes de datos en la base `data/metrics.duckdb`.</p>
                </div>
            </header>

            {/* Inyección del controlador de lista de archivos persistidos */}
            <FileList />
        </div>
    );
};
