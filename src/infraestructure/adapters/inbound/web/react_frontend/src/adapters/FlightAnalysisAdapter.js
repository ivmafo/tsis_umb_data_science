export class FlightAnalysisAdapter {
    static toDateRangeDTO(dateRanges) {
        if (!Array.isArray(dateRanges)) {
            throw new Error('Invalid date ranges format');
        }
        
        return {
            date_ranges: dateRanges.map(range => ({
                id: range.id.toString(), // Aseguramos que sea string
                start_date: range.startDate,
                end_date: range.endDate,
                label: range.label,
                origin_airport: range.originAirport || null,
                destination_airport: range.destinationAirport || null,
                nivel_min: range.nivelMin ? parseInt(range.nivelMin) : null,
                nivel_max: range.nivelMax ? parseInt(range.nivelMax) : null
            }))
        };
    }

    static formatChartData(data) {
        if (!Array.isArray(data)) {
            console.error('Invalid data format received:', data);
            return [];
        }
        
        return data.map(item => ({
            hour: `${String(item.hour).padStart(2, '0')}:00`,
            ...item.counts
        }));
    }
}