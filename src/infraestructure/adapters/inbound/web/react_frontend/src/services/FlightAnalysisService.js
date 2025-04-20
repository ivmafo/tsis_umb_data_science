export class FlightAnalysisService {
    static async analyzeFlights(dateRanges, analysisType) {
        const endpoint = analysisType === 'destination' 
            ? '/api/flights/analyze-date-ranges-destination'
            : '/api/flights/analyze-date-ranges';

        try {
            // Asegurarse que los niveles se envían como números
            const processedDateRanges = dateRanges.map(range => ({
                ...range,
                nivel_min: parseInt(range.nivel_min) || 0,
                nivel_max: parseInt(range.nivel_max) || 99999
            }));

            const response = await fetch(`http://localhost:8000${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    date_ranges: processedDateRanges,
                    type: analysisType || 'origin'
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Error response:', errorData);
                throw new Error(errorData.detail ? JSON.stringify(errorData.detail) : 'Error en la respuesta del servidor');
            }

            const data = await response.json();
            console.log('Datos recibidos:', data);
            return data;
        } catch (error) {
            console.error('Error detallado:', error);
            throw error;
        }
    }

    static async getMonthlyOriginAnalysis(dateRanges) {
        try {
            const response = await fetch('http://localhost:8000/api/flights/monthly-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    date_ranges: dateRanges,
                    type: 'origin'
                }),
            });

            if (!response.ok) {
                throw new Error('Error fetching monthly origin analysis');
            }

            const data = await response.json();
            console.log('Monthly origin data received:', data);
            return data;
        } catch (error) {
            console.error('Error in getMonthlyOriginAnalysis:', error);
            throw error;
        }
    }

    static async getMonthlyDestinationAnalysis(dateRanges) {
        try {
            const response = await fetch('http://localhost:8000/api/flights/monthly-analysis-destination', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    date_ranges: dateRanges,
                    type: 'destination'
                }),
            });

            if (!response.ok) {
                throw new Error('Error fetching monthly destination analysis');
            }

            const data = await response.json();
            console.log('Monthly destination data received:', data);
            return data;
        } catch (error) {
            console.error('Error in getMonthlyDestinationAnalysis:', error);
            throw error;
        }
    }
}