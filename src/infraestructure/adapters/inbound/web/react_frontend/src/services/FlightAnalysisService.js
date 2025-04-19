export class FlightAnalysisService {
    static async analyzeFlights(dateRanges, analysisType) {
        const endpoint = analysisType === 'destination' 
            ? '/api/flights/analyze-date-ranges-destination'
            : '/api/flights/analyze-date-ranges';

        try {
            const response = await fetch(`http://localhost:8000${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    date_ranges: dateRanges,
                    type: analysisType || 'origin' // Agregamos el campo type
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
}