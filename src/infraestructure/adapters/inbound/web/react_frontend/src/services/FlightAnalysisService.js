export class FlightAnalysisService {
    static async analyzeFlights(dateRanges, analysisType) {
        try {
            const endpoint = analysisType === 'destination_analysis' 
                ? 'http://localhost:8000/api/flights/analyze-date-ranges-destination'
                : 'http://localhost:8000/api/flights/analyze-date-ranges';

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    type: analysisType,
                    date_ranges: dateRanges
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (!Array.isArray(data)) {
                throw new Error('Invalid data format received from server');
            }

            return data;
        } catch (error) {
            console.error('Error in analyzeFlights:', error);
            throw error;
        }
    }
}