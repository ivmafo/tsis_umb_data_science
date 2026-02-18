import { FileUploader } from '../components/FileUploader';

export const UploadView = ({ onSuccess }: { onSuccess: () => void }) => {
    return (
        <div className="max-w-2xl mx-auto mt-10">
            <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-slate-800">Cargar Nuevos Datos</h1>
                <p className="text-slate-500 mt-2">Sube archivos Excel (.xlsx) compatibles con el esquema SRS.</p>
            </div>

            <FileUploader onUploadSuccess={onSuccess} />
        </div>
    );
};
