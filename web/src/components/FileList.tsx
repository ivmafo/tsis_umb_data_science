import { useEffect, useState } from 'react';
import type { FileInfo } from '../api';
import { getFiles, deleteFile, ingestData } from '../api';
import { FileText, CheckCircle, XCircle, Trash2 } from 'lucide-react';

/**
 * Componente de Gestión: Lista de Control de Archivos.
 * 
 * Este componente es el núcleo administrativo del pipeline de datos. 
 * Permite visualizar el inventario de archivos en el servidor, monitorear 
 * su estado de validación estructural y disparar procesos de ingesta ETL.
 * 
 * Atributos Técnicos:
 * - Polling dinámico (5s) para reflejar estados de procesamiento en tiempo real.
 * - Integración con el motor de borrado físico y lógico.
 * - Feedback binario (Válido/Error) basado en validación de esquema CSV/XLS.
 */
export const FileList = () => {
    // files: Inventario de archivos con metadatos de estado (DB_STATUS, VALIDATION)
    const [files, setFiles] = useState<FileInfo[]>([]);

    // loading: Estado inicial de sincronización con la API de archivos
    const [loading, setLoading] = useState(true);

    // processingFile: Bloqueo UI para el archivo que se encuentra actualmente en el bus de ingesta
    const [processingFile, setProcessingFile] = useState<string | null>(null);

    /**
     * Sincroniza el estado local con el sistema de archivos del servidor backend.
     */
    const fetchFiles = async () => {
        try {
            const data = await getFiles();
            setFiles(data);
        } catch (error) {
            console.error("Fallo al listar archivos del repositorio:", error);
        } finally {
            setLoading(false);
        }
    };

    /**
     * Dispara el Use Case de Ingesta para un archivo específico.
     * Este proceso es asíncrono y bloquea el botón de acción para prevenir doble indexación.
     * @param filename - Identificador del archivo en el servidor.
     */
    const handleProcess = async (filename: string) => {
        setProcessingFile(filename);
        try {
            // Lógica ETL: Truncado de buffers e inserción en DuckDB
            await ingestData(false, filename);
            alert(`Proceso de indexación iniciado para: ${filename}. El estado cambiará a COMPLETED automáticamente.`);
            fetchFiles();
        } catch (error) {
            console.error("Fallo crítico en el inicio de ingesta:", error);
            alert("Error al intentar procesar el archivo. Verifique logs del servidor.");
        } finally {
            setTimeout(() => setProcessingFile(null), 2000);
        }
    };

    /**
     * Elimina el archivo del disco y purga todas sus referencias en las tablas de métricas.
     * @param filename - Archivo a eliminar.
     */
    const handleDelete = async (filename: string) => {
        if (!confirm(`ADVERTENCIA: ¿Desea eliminar permanentemente '${filename}' y todas sus métricas asociadas? Esta acción es irreversible.`)) return;

        try {
            await deleteFile(filename);
            fetchFiles(); // Refresco inmediato del inventario
        } catch (error) {
            console.error("Fallo en la purga de archivos:", error);
        }
    };

    useEffect(() => {
        fetchFiles();
        // Mecanismo de Heartbeat para monitorear procesos ETL de larga duración
        const interval = setInterval(fetchFiles, 5000);
        return () => clearInterval(interval);
    }, []);

    if (loading) return <div className="p-8 text-center text-slate-500 animate-pulse">Cargando datos...</div>;

    return (
        <div className="card overflow-hidden">
            <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex justify-between items-center">
                <h3 className="font-semibold text-slate-700">Archivos Registrados</h3>
                <span className="text-xs font-medium px-2 py-1 bg-white border border-slate-200 rounded-md text-slate-500">
                    Total: {files.length}
                </span>
            </div>

            <div className="divide-y divide-slate-100">
                {files.length === 0 ? (
                    <div className="p-12 text-center text-slate-400">
                        <FileText className="w-12 h-12 mx-auto mb-3 opacity-20" />
                        <p>No se encontraron archivos en el directorio data.</p>
                    </div>
                ) : (
                    files.map((file) => {
                        const isProcessed = file.db_status === 'COMPLETED';
                        const isProcessing = file.db_status === 'PROCESSING' || processingFile === file.filename;

                        return (
                            <div key={file.filename} className="flex items-center justify-between p-4 hover:bg-slate-50 transition-colors">
                                <div className="flex items-center gap-4">
                                    <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
                                        <FileText className="w-6 h-6" />
                                    </div>
                                    <div className="flex flex-col">
                                        <span className="font-medium text-slate-900">{file.filename}</span>
                                        <div className="flex items-center gap-2">
                                            <span className="text-xs text-slate-500">{(file.size_bytes / 1024 / 1024).toFixed(2)} MB</span>
                                            {file.db_status && (
                                                <span className={`text-[10px] px-1.5 py-0.5 rounded-full border ${file.db_status === 'COMPLETED' ? 'bg-indigo-50 text-indigo-600 border-indigo-100' :
                                                    file.db_status === 'PROCESSING' ? 'bg-amber-50 text-amber-600 border-amber-100' :
                                                        file.db_status === 'ERROR' ? 'bg-red-50 text-red-600 border-red-100' :
                                                            'bg-slate-100 text-slate-500 border-slate-200'
                                                    }`}>
                                                    {file.db_status}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-4">
                                    {file.validation_status ? (
                                        <div className="flex items-center gap-2">
                                            <button
                                                onClick={() => handleProcess(file.filename)}
                                                disabled={isProcessed || isProcessing}
                                                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${isProcessed
                                                    ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                                                    : isProcessing
                                                        ? 'bg-amber-50 text-amber-600 border border-amber-200 cursor-wait'
                                                        : 'bg-indigo-50 text-indigo-600 hover:bg-indigo-100 border border-indigo-200'
                                                    }`}
                                            >
                                                {isProcessed ? 'Procesado' : isProcessing ? 'Procesando...' : 'Procesar'}
                                            </button>
                                            <span className="flex items-center gap-1.5 text-emerald-600 text-sm bg-emerald-50 px-3 py-1 rounded-full border border-emerald-100">
                                                <CheckCircle className="w-4 h-4" /> Válido
                                            </span>
                                        </div>
                                    ) : (
                                        <span className="flex items-center gap-1.5 text-rose-600 text-sm bg-rose-50 px-3 py-1 rounded-full border border-rose-100" title={file.error_message}>
                                            <XCircle className="w-4 h-4" /> Error
                                        </span>
                                    )}
                                    <button
                                        onClick={() => handleDelete(file.filename)}
                                        className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                                        title="Eliminar archivo y datos"
                                    >
                                        <Trash2 className="w-5 h-5" />
                                    </button>
                                </div>
                            </div>
                        )
                    })
                )}
            </div>
        </div>
    );
};
