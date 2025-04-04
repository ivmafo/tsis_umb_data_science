export class FlightAnalysisAdapter {
    static toDateRangeDTO(dateRanges) {
        if (!Array.isArray(dateRanges)) {
            throw new Error('Invalid date ranges format');
        }
        
        return dateRanges.map(range => ({
            id: range.id,
            start_date: range.startDate,
            end_date: range.endDate,
            label: range.label,
            origin_airport: range.originAirport,
            destination_airport: range.destinationAirport
        }));
    }

    static formatChartData(data) {
        if (!Array.isArray(data)) {
            console.error('Invalid data format received:', data);
            return [];
        }
        
        return data.map(item => {
            if (!item || typeof item.hour === 'undefined') {
                console.error('Invalid item format:', item);
                return null;
            }
            
            return {
                hour: `${String(item.hour).padStart(2, '0')}:00`,
                ...item.counts
            };
        }).filter(item => item !== null);
    }
}