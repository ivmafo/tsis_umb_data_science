import { api } from '../api';

export interface UncertaintyRange {
    lower: number;
    upper: number;
}

export interface StochasticCapacityReport {
    nominal_theoretical_capacity: number;
    ashford_baseline_capacity: number;
    stochastic_simulated_capacity: number;
    uncertainty_range: UncertaintyRange;
    applied_utilization_factor: number;
    status: string;
}

export interface PhysicistMetrics {
    dynamic_tfc: number;
    dynamic_rot: number;
    bottleneck_source: string;
}

export interface DynamicCapacityResult {
    sector_name: string;
    compliance_warnings: string[];
    physicist_metrics: PhysicistMetrics;
    stochastic_capacity_report: StochasticCapacityReport;
    legacy_nominal_comparison: any;
}

/**
 * Agente Frontend (The Visualizer)
 * Encapsula la lógica estocástica para consultar y gestionar el estado 
 * de la capacidad dinámica de un sector.
 */
export class FrontendAgent {
    /**
     * Llama al BackendAgent para computar la capacidad dinámica.
     * @param sectorId ID del sector a calcular.
     * @param filters Rango de fechas histórico.
     */
    static async calculateDynamicCapacity(
        sectorId: string,
        filters: { start_date?: string, end_date?: string }
    ): Promise<DynamicCapacityResult> {
        const response = await api.post(`/sectors/${sectorId}/calculate`, filters);
        return response.data;
    }

    /**
     * Transforma el reporte para ser inyectado en la gráfica de Echarts.
     */
    static getChartBands(report: DynamicCapacityResult) {
        if (!report?.stochastic_capacity_report) return null;

        const { nominal_theoretical_capacity, uncertainty_range } = report.stochastic_capacity_report;

        return {
            nominalLine: nominal_theoretical_capacity,
            lowerBand: uncertainty_range.lower,
            upperBand: uncertainty_range.upper
        };
    }
}
