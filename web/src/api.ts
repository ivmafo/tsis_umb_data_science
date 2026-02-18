import axios from 'axios';

/**
 * URL base para las peticiones al backend.
 * Se asume que el backend corre en el puerto 8000 por defecto.
 */
const API_URL = 'http://localhost:8000';

/**
 * Interfaz que representa la información de un archivo procesado.
 */
export interface FileInfo {
    filename: string;           // Nombre del archivo original
    size_bytes: number;         // Tamaño en bytes
    validation_status: boolean; // Si el archivo pasó la validación de esquema
    error_message?: string;     // Mensaje en caso de error de procesamiento
    db_status?: string;         // Estado de inserción en la base de datos
}

/**
 * Instancia configurada de Axios para realizar peticiones al backend.
 */
export const api = axios.create({
    baseURL: API_URL,
});

/**
 * Obtiene la lista de todos los archivos que han sido subidos o procesados.
 * @returns Promesa con la lista de FileInfo.
 */
export const getFiles = async (): Promise<FileInfo[]> => {
    const response = await api.get('/files/');
    return response.data;
};

/**
 * Sube un nuevo archivo al backend para su procesamiento.
 * @param file Objeto File de JavaScript obtenido de un input.
 * @returns Promesa con la información del archivo subido.
 */
export const uploadFile = async (file: File): Promise<FileInfo> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/files/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

// --- API de Regiones ---

/**
 * Interfaz que representa una Región Aeronáutica.
 */
export interface Region {
    id?: number;          // Identificador único (opcional en creación)
    name: string;        // Nombre de la región
    code: string;        // Código identificador único
    description: string; // Descripción detallada
    created_at?: string; // Fecha de creación
    updated_at?: string; // Fecha de última actualización
    nivel_min: number;   // Nivel de vuelo mínimo asociado
}

/**
 * Obtiene la lista de todas las regiones registradas.
 */
export const getRegions = async (): Promise<Region[]> => {
    const response = await api.get('/regions/');
    return response.data;
};

/**
 * Crea una nueva región en el sistema.
 * @param region Datos de la región a crear.
 */
export const createRegion = async (region: Region): Promise<Region> => {
    const response = await api.post('/regions/', region);
    return response.data;
};

/**
 * Actualiza los datos de una región existente.
 * @param id Identificador de la región.
 * @param region Datos actualizados.
 */
export const updateRegion = async (id: number, region: Region): Promise<Region> => {
    const response = await api.put(`/regions/${id}`, region);
    return response.data;
};

/**
 * Elimina una región del sistema.
 * @param id Identificador de la región.
 */
export const deleteRegion = async (id: number): Promise<void> => {
    await api.delete(`/regions/${id}`);
};

// --- API de Aeropuertos ---

/**
 * Interfaz que representa un Aeropuerto.
 */
export interface Airport {
    id: number;
    icao_code: string;      // Código OACI (ej. SKBO)
    iata_code?: string;     // Código IATA (ej. BOG)
    name: string;           // Nombre completo
    city?: string;          // Ciudad de ubicación
    country?: string;       // País
    type?: string;          // Tipo (airport, heliport, etc.)
    latitude?: number;      // Coordenadas geográficas
    longitude?: number;
    altitude?: number;      // Altitud en pies
    timezone?: number;      // GMT offset
    dst?: string;           // Daylight Savings
    source?: string;        // Fuente de datos
}

/**
 * Interfaz para respuestas paginadas estándar.
 */
export interface PaginatedResponse<T> {
    data: T[];              // Lista de elementos en la página actual
    total: number;          // Total global de elementos
    page: number;           // Número de página actual
    page_size: number;      // Tamaño de la página
}

/**
 * Obtiene una lista paginada de aeropuertos con búsqueda opcional.
 * @param page Número de página (base 1).
 * @param pageSize Elementos por página.
 * @param search Término de búsqueda (filtra por ICAO o nombre).
 */
export const getAirports = async (page = 1, pageSize = 10, search = ""): Promise<PaginatedResponse<Airport>> => {
    const response = await api.get('/airports/', {
        params: { page, page_size: pageSize, search }
    });
    return response.data;
};

/**
 * Crea un nuevo aeropuerto.
 */
export const createAirport = async (airport: Omit<Airport, 'id'>): Promise<Airport> => {
    const response = await api.post('/airports/', airport);
    return response.data;
};

/**
 * Actualiza parcialmente los datos de un aeropuerto.
 */
export const updateAirport = async (id: number, airport: Partial<Airport>): Promise<Airport> => {
    const response = await api.put(`/airports/${id}`, airport);
    return response.data;
};

/**
 * Elimina un aeropuerto.
 */
export const deleteAirport = async (id: number): Promise<void> => {
    await api.delete(`/airports/${id}`);
};

// --- API de Asignación Región-Aeropuerto ---

/**
 * Interfaz que vincula un aeropuerto con una región.
 */
export interface RegionAirport {
    id: number;
    icao_code: string;  // Código del aeropuerto
    region_id: number;  // ID de la región asociada
    created_at?: string;
}

/**
 * Obtiene la lista paginada de asociaciones región-aeropuerto.
 */
export const getRegionAirports = async (page = 1, pageSize = 10, search = ""): Promise<PaginatedResponse<RegionAirport>> => {
    const response = await api.get('/region-airports/', {
        params: { page, page_size: pageSize, search }
    });
    return response.data;
};

/**
 * Crea una nueva vinculación entre región y aeropuerto.
 */
export const createRegionAirport = async (item: Omit<RegionAirport, 'id' | 'created_at'>): Promise<RegionAirport> => {
    const response = await api.post('/region-airports/', item);
    return response.data;
};

/**
 * Actualiza una vinculación existente.
 */
export const updateRegionAirport = async (id: number, item: Partial<RegionAirport>): Promise<RegionAirport> => {
    const response = await api.put(`/region-airports/${id}`, item);
    return response.data;
};

/**
 * Elimina una vinculación.
 */
export const deleteRegionAirport = async (id: number): Promise<void> => {
    await api.delete(`/region-airports/${id}`);
};

// --- API de ETL (Extracción, Transformación y Carga) ---

/**
 * Inicia el proceso de ingesta de datos de vuelos.
 * @param forceReload Si es true, limpia los datos existentes antes de cargar.
 * @param filename Opcional: Nombre de un archivo específico para cargar.
 */
export const ingestData = async (forceReload: boolean = false, filename?: string): Promise<{ status: string; message: string }> => {
    const params: any = { force_reload: forceReload };
    if (filename) params.filename = filename;

    const response = await api.post('/etl/ingest', null, {
        params: params
    });
    return response.data;
};

/**
 * Elimina un archivo del registro y sus datos asociados.
 */
export const deleteFile = async (filename: string): Promise<void> => {
    await api.delete(`/etl/files/${filename}`);
};

/**
 * Reinicia completamente la base de datos de vuelos y control.
 */
export const resetDatabase = async (): Promise<void> => {
    await api.post('/etl/reset');
};

// --- API de Filtros ---

export interface FilterValue {
    id: number;
    value: string;
}

/**
 * Refresca la caché de filtros en el backend basada en los datos cargados.
 */
export const refreshFilters = async (): Promise<{ status: string, total_records: number }> => {
    const response = await api.post('/filters/refresh');
    return response.data;
};

/**
 * Busca valores de filtros (como aeropuertos o aerolíneas) dinámicamente.
 * @param parentId ID de la categoría de filtro.
 * @param query Texto a buscar.
 */
export const searchFilterValues = async (parentId: number, query: string = ""): Promise<FilterValue[]> => {
    const response = await api.get(`/filters/${parentId}/search`, {
        params: { q: query }
    });
    return response.data;
};

// --- API de Reportes ---

/**
 * Exporta datos crudos basados en filtros a formato CSV.
 */
export const exportRawData = async (filters: any): Promise<Blob> => {
    const response = await api.post('/reports/raw/csv', filters, {
        responseType: 'blob'
    });
    return response.data;
};

/**
 * Descarga el reporte ejecutivo consolidado en PDF o Excel.
 */
export const downloadExecutiveReport = async (filters: any, type: 'pdf' | 'excel'): Promise<Blob> => {
    const endpoint = `/reports/executive/${type}`;
    const response = await api.post(endpoint, filters, {
        responseType: 'blob'
    });
    return response.data;
};

// --- Filtros Predictivos y API de Análisis ---

/**
 * Estructura estándar para filtros aplicados a modelos predictivos.
 */
export interface PredictiveFilters {
    sector_id?: string;     // ID del sector configurado
    airport?: string;       // Código de aeropuerto (origen/destino)
    route?: string;         // Ruta específica (ej. SKBO-SKRG)
    min_level?: number;     // Nivel de vuelo mínimo
    max_level?: number;     // Nivel de vuelo máximo
    start_date?: string;    // Fecha de inicio (YYYY-MM-DD)
    end_date?: string;      // Fecha de fin (YYYY-MM-DD)
    aggregation?: 'avg' | 'sum';
}

/**
 * Obtiene el pronóstico de demanda diaria (corto plazo - 30 días).
 */
export const getDailyDemandForecast = async (days: number = 30, filters: PredictiveFilters = {}) => {
    const response = await api.get(`/predictive/daily-demand`, {
        params: { days, ...filters }
    });
    return response.data;
};

/**
 * Obtiene el mapa de calor de horas pico proyectado.
 */
export const getPeakHoursForecast = async (filters: PredictiveFilters = {}) => {
    const response = await api.get('/predictive/peak-hours', {
        params: filters
    });
    return response.data;
};

/**
 * Obtiene la proyección de crecimiento de aerolíneas principales.
 */
export const getAirlineGrowthForecast = async (months: number = 12, filters: PredictiveFilters = {}) => {
    const response = await api.get(`/predictive/airline-growth`, {
        params: { months, ...filters }
    });
    return response.data;
};

/**
 * Evalúa la saturación proyectada de un sector basada en su capacidad calculada.
 * @param filters Filtros aplicados incluyendo sector_id.
 * @param days Días a proyectar (def: 30).
 */
export const getSectorSaturationForecast = async (filters: PredictiveFilters, days: number = 30) => {
    const sectorId = filters.sector_id;
    if (!sectorId) throw new Error("ID de Sector es requerido para el pronóstico de saturación");

    const response = await api.get(`/predictive/sector-saturation/${sectorId}`, {
        params: { days, ...filters }
    });
    return response.data;
};

/**
 * Obtiene la tendencia estacional de largo plazo mediante descomposición de Fourier.
 */
export const getSeasonalTrendForecast = async (filters: PredictiveFilters) => {
    const response = await api.get(`/predictive/seasonal-trend`, {
        params: filters
    });
    return response.data;
};
