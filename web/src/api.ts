import axios from 'axios';

const API_URL = 'http://localhost:8000';

export interface FileInfo {
    filename: string;
    size_bytes: number;
    validation_status: boolean;
    error_message?: string;
    db_status?: string;
}

export const api = axios.create({
    baseURL: API_URL,
});

export const getFiles = async (): Promise<FileInfo[]> => {
    const response = await api.get('/files/');
    return response.data;
};

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

// Regions API
export interface Region {
    id?: number;
    name: string;
    code: string;
    description: string;
    created_at?: string;
    updated_at?: string;
    nivel_min: number;
}

export const getRegions = async (): Promise<Region[]> => {
    const response = await api.get('/regions/');
    return response.data;
};

export const createRegion = async (region: Region): Promise<Region> => {
    const response = await api.post('/regions/', region);
    return response.data;
};

export const updateRegion = async (id: number, region: Region): Promise<Region> => {
    const response = await api.put(`/regions/${id}`, region);
    return response.data;
};

export const deleteRegion = async (id: number): Promise<void> => {
    await api.delete(`/regions/${id}`);
};

// Airports API
export interface Airport {
    id: number;
    icao_code: string;
    iata_code?: string; // Optional
    name: string;
    city?: string; // Optional
    country?: string; // Optional
    type?: string; // Optional
    // Optional fields for creation
    latitude?: number;
    longitude?: number;
    altitude?: number;
    timezone?: number;
    dst?: string;
    source?: string;
}

export interface PaginatedResponse<T> {
    data: T[];
    total: number;
    page: number;
    page_size: number;
}

export const getAirports = async (page = 1, pageSize = 10, search = ""): Promise<PaginatedResponse<Airport>> => {
    const response = await api.get('/airports/', {
        params: { page, page_size: pageSize, search }
    });
    return response.data;
};

export const createAirport = async (airport: Omit<Airport, 'id'>): Promise<Airport> => {
    const response = await api.post('/airports/', airport);
    return response.data;
};

export const updateAirport = async (id: number, airport: Partial<Airport>): Promise<Airport> => {
    const response = await api.put(`/airports/${id}`, airport);
    return response.data;
};

export const deleteAirport = async (id: number): Promise<void> => {
    await api.delete(`/airports/${id}`);
};

// Region-Airport API
export interface RegionAirport {
    id: number;
    icao_code: string;
    region_id: number;
    created_at?: string;
}

export const getRegionAirports = async (page = 1, pageSize = 10, search = ""): Promise<PaginatedResponse<RegionAirport>> => {
    const response = await api.get('/region-airports/', {
        params: { page, page_size: pageSize, search }
    });
    return response.data;
};

export const createRegionAirport = async (item: Omit<RegionAirport, 'id' | 'created_at'>): Promise<RegionAirport> => {
    const response = await api.post('/region-airports/', item);
    return response.data;
};

export const updateRegionAirport = async (id: number, item: Partial<RegionAirport>): Promise<RegionAirport> => {
    const response = await api.put(`/region-airports/${id}`, item);
    return response.data;
};

export const deleteRegionAirport = async (id: number): Promise<void> => {
    await api.delete(`/region-airports/${id}`);
};

// ETL API
export const ingestData = async (forceReload: boolean = false, filename?: string): Promise<{ status: string; message: string }> => {
    const params: any = { force_reload: forceReload };
    if (filename) params.filename = filename;

    const response = await api.post('/etl/ingest', null, {
        params: params
    });
    return response.data;
};

export const deleteFile = async (filename: string): Promise<void> => {
    await api.delete(`/etl/files/${filename}`);
};

export const resetDatabase = async (): Promise<void> => {
    await api.post('/etl/reset');
};

// Filters API
export interface FilterValue {
    id: number;
    value: string;
}

export const refreshFilters = async (): Promise<{ status: string, total_records: number }> => {
    const response = await api.post('/filters/refresh');
    return response.data;
};

export const searchFilterValues = async (parentId: number, query: string = ""): Promise<FilterValue[]> => {
    const response = await api.get(`/filters/${parentId}/search`, {
        params: { q: query }
    });
    return response.data;
};

export const exportRawData = async (filters: any): Promise<Blob> => {
    const response = await api.post('/reports/raw/csv', filters, {
        responseType: 'blob'
    });
    return response.data;
};

export const downloadExecutiveReport = async (filters: any, type: 'pdf' | 'excel'): Promise<Blob> => {
    const endpoint = `/reports/executive/${type}`;
    const response = await api.post(endpoint, filters, {
        responseType: 'blob'
    });
    return response.data;
};

// Predictive Reports
export interface PredictiveFilters {
    sector_id?: string;
    airport?: string;
    route?: string;
    min_level?: number;
    max_level?: number;
    start_date?: string;
    end_date?: string;
    aggregation?: 'avg' | 'sum';
}

export const getDailyDemandForecast = async (days: number = 30, filters: PredictiveFilters = {}) => {
    const response = await api.get(`/predictive/daily-demand`, {
        params: { days, ...filters }
    });
    return response.data;
};

export const getPeakHoursForecast = async (filters: PredictiveFilters = {}) => {
    const response = await api.get('/predictive/peak-hours', {
        params: filters
    });
    return response.data;
};

export const getAirlineGrowthForecast = async (months: number = 12, filters: PredictiveFilters = {}) => {
    const response = await api.get(`/predictive/airline-growth`, {
        params: { months, ...filters }
    });
    return response.data;
};

export const getSectorSaturationForecast = async (filters: PredictiveFilters, days: number = 30) => {
    const sectorId = filters.sector_id;
    if (!sectorId) throw new Error("Sector ID is required for saturation forecast");

    // Pass all filters as query params
    const response = await api.get(`/predictive/sector-saturation/${sectorId}`, {
        params: { days, ...filters }
    });
    return response.data;
};

export const getSeasonalTrendForecast = async (filters: PredictiveFilters) => {
    const response = await api.get(`/predictive/seasonal-trend`, {
        params: filters
    });
    return response.data;
};
