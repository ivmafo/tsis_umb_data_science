import { useState } from 'react';
import { uploadFile, ingestData } from '../api';
import { UploadCloud, Loader2, Check, XCircle } from 'lucide-react';
import clsx from 'clsx';

/**
 * Componente de Entrada: Cargador de Archivos Estratégicos.
 * 
 * Proporciona una interfaz visual para la transferencia de archivos Excel (.xlsx)
 * desde la estación de trabajo local al repositorio de datos del servidor.
 * 
 * Atributos Técnicos:
 * - Automatización de Ingesta: Dispara el proceso de indexación DuckDB inmediatamente tras la carga.
 * - Validación Prematura: Captura errores de red y de formato antes de confirmar la carga.
 * - Feedback Multiestado: Gestiona estados de 'idle', 'uploading', 'success' y 'error' visualmente.
 * 
 * @param props.onUploadSuccess - Callback invocado para refrescar el inventario tras una carga exitosa.
 */
export const FileUploader = ({ onUploadSuccess }: { onUploadSuccess: () => void }) => {
    // uploading: Bloqueo de UI y activación del spinner de carga asíncrona
    const [uploading, setUploading] = useState(false);

    // status: Máquina de estados finitos para la respuesta visual del componente
    const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');

    // message: Información detallada sobre el resultado de la operación (ej: errores de esquema)
    const [message, setMessage] = useState<string | null>(null);

    /**
     * Controlador de evento de selección de archivo.
     * Ejecuta la subida binaria y el disparador ETL en secuencia.
     */
    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setUploading(true);
        setStatus('idle');
        setMessage(null);

        try {
            // Fase 1: Transferencia física del archivo al directorio /data
            await uploadFile(file);

            try {
                // Fase 2: Disparo automático del pipeline de procesamiento
                await ingestData();
                setMessage(`Archivo ${file.name} cargado. La indexación ha comenzado en segundo plano.`);
            } catch (etlErr) {
                console.error("Fallo técnico en disparo automático de ingesta:", etlErr);
                setMessage(`Carga física exitosa, pero se requiere inicio manual de procesamiento.`);
            }

            setStatus('success');
            onUploadSuccess();
            setTimeout(() => setStatus('idle'), 3000);
        } catch (err: any) {
            setStatus('error');
            setMessage(err.response?.data?.detail || "Error en la transferencia de red o formato inválido.");
        } finally {
            setUploading(false);
            e.target.value = ""; // Limpieza del buffer del input
        }
    };

    return (
        <div className="card p-8 text-center transition-all hover:shadow-md">
            <div
                className={clsx(
                    "border-2 border-dashed rounded-xl p-10 transition-colors duration-200 flex flex-col items-center justify-center min-h-[200px] cursor-pointer group",
                    status === 'error' ? "border-rose-300 bg-rose-50/50" :
                        status === 'success' ? "border-emerald-300 bg-emerald-50/50" :
                            uploading ? "border-blue-300 bg-blue-50/30 cursor-wait" :
                                "border-slate-300 hover:border-primary hover:bg-slate-50"
                )}
            >
                <label className="w-full h-full flex flex-col items-center justify-center cursor-pointer">
                    <input
                        type="file"
                        accept=".xlsx"
                        className="hidden"
                        onChange={handleFileChange}
                        disabled={uploading}
                    />

                    {uploading ? (
                        <>
                            <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mb-4 animate-pulse">
                                <Loader2 className="w-8 h-8 animate-spin" />
                            </div>
                            <h3 className="text-lg font-semibold text-slate-700">Procesando archivo...</h3>
                            <p className="text-sm text-slate-500 mt-1">Validando estructura y columnas</p>
                        </>
                    ) : status === 'success' ? (
                        <>
                            <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mb-4">
                                <Check className="w-8 h-8" />
                            </div>
                            <h3 className="text-lg font-semibold text-slate-700">¡Carga Exitosa!</h3>
                            <p className="text-sm text-emerald-600 mt-1 font-medium">{message}</p>
                        </>
                    ) : (
                        <>
                            <div className="w-16 h-16 bg-slate-100 text-slate-400 group-hover:bg-blue-100 group-hover:text-primary rounded-full flex items-center justify-center mb-4 transition-colors">
                                <UploadCloud className="w-8 h-8" />
                            </div>
                            <h3 className="text-lg font-semibold text-slate-700 group-hover:text-primary transition-colors">
                                Click para seleccionar archivo
                            </h3>
                            <p className="text-sm text-slate-500 mt-1">
                                Soporta archivos Excel (.xlsx)
                            </p>
                        </>
                    )}
                </label>
            </div>

            {status === 'error' && (
                <div className="mt-6 p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-lg text-sm flex items-center gap-3 text-left">
                    <span className="p-1 bg-white rounded-full"><XCircle className="w-4 h-4" /></span>
                    <div>
                        <span className="font-semibold block">Error de Validación:</span>
                        {message}
                    </div>
                </div>
            )}
        </div>
    );
};
