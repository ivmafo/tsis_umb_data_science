export class FlightAnalysisAdapter {
    static toDateRangeDTO(dateRanges) {
        if (!Array.isArray(dateRanges)) {
            throw new Error('Invalid date ranges format');
        }
        
        return {
            date_ranges: dateRanges.map(range => ({
                id: range.id.toString(),
                start_date: range.startDate,
                end_date: range.endDate,
                label: range.label,
                origin_airport: range.originAirport || null,
                destination_airport: range.destinationAirport || null,
                nivel_min: range.nivelMin !== undefined ? parseInt(range.nivelMin) : 0,
                nivel_max: range.nivelMax !== undefined ? parseInt(range.nivelMax) : 99999
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