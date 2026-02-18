import { FileUploader } from '../components/FileUploader';

/**
 * Vista de Ingesta: Carga de Archivos de Operaciones.
 * 
 * Este componente es el punto de entrada para nuevos datos en el sistema.
 * Proporciona el contexto visual para el componente `FileUploader`, 
 * centralizando la carga de registros Excel (.xlsx) que alimentan el 
 * motor analítico.
 */
export const UploadView = ({ onSuccess }: { onSuccess: () => void }) => {
    return (
        <div className="max-w-2xl mx-auto mt-10">
            <header className="text-center mb-8">
                <h1 className="text-3xl font-bold text-slate-800">Cargar Nuevos Datos</h1>
                <p className="text-slate-500 mt-2">Sube archivos Excel (.xlsx) compatibles con el esquema SRS para indexación en DuckDB.</p>
            </header>

            {/* Componente de arrastrar y soltar con lógica de streaming al backend */}
            <FileUploader onUploadSuccess={onSuccess} />
        </div>
    );
};
