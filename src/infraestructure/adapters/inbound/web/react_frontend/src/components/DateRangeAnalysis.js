import React, { useState, useEffect } from 'react';
import { Line } from 'recharts';
import { ResponsiveContainer, LineChart, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';
import './DateRangeAnalysis.css';

const DateRangeAnalysis = () => {
    // Initial states - remove duplicates
    const [dateRanges, setDateRanges] = useState([{ 
        id: 1, 
        startDate: '', 
        endDate: '',
        label: 'Rango 1'
    }]);
    const [selectedAirport, setSelectedAirport] = useState('');
    const [selectedDestination, setSelectedDestination] = useState('');
    const [chartData, setChartData] = useState([]);
    const [destinationChartData, setDestinationChartData] = useState([]);
    const [airports, setAirports] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchAirports();
    }, []);

    const validateDateRanges = () => {
        return dateRanges.every(range => 
            range.startDate && 
            range.endDate && 
            new Date(range.startDate) <= new Date(range.endDate)
        );
    };

    const handleDateChange = (id, field, value) => {
        setDateRanges(ranges => 
            ranges.map(range => 
                range.id === id 
                    ? { ...range, [field]: value }
                    : range
            )
        );
    };

    const addDateRange = () => {
        const newId = Math.max(...dateRanges.map(r => r.id)) + 1;
        setDateRanges([...dateRanges, {
            id: newId,
            startDate: '',
            endDate: '',
            label: `Rango ${newId}`
        }]);
    };

    const removeDateRange = (id) => {
        if (dateRanges.length > 1) {
            setDateRanges(ranges => ranges.filter(range => range.id !== id));
        }
    };

    const formatChartData = (data) => {
        if (!Array.isArray(data)) return [];
        return data.map(item => ({
            hour: `${String(item.hour).padStart(2, '0')}:00`,
            ...item.counts
        }));
    };

    const getCustomColors = (index) => {
        const colors = [
            '#2196F3', // Blue
            '#4CAF50', // Green
            '#F44336', // Red
            '#9C27B0', // Purple
            '#FF9800', // Orange
            '#795548'  // Brown
        ];
        return colors[index % colors.length];
    };

    const fetchAirports = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/flights/origins');
            if (!response.ok) {
                throw new Error('Failed to fetch airports');
            }
            const data = await response.json();
            // Ensure data is an array before setting it
            setAirports(Array.isArray(data) ? data : []);
        } catch (err) {
            console.error('Error fetching airports:', err);
            setAirports([]); // Set empty array on error
            setError('Error loading airports');
        }
    };

    const analyzeDateRanges = async () => {
        if (!validateDateRanges()) {
            setError('Por favor, ingrese rangos de fechas válidos');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const dateRangesPayload = dateRanges.map(range => ({
                id: range.id,
                start_date: range.startDate,
                end_date: range.endDate,
                label: range.label
            }));

            // Log the requests for debugging
            console.log('Origin Request:', {
                date_ranges: dateRangesPayload,
                airport: selectedAirport,
                type: 'origin'
            });
            console.log('Destination Request:', {
                date_ranges: dateRangesPayload,
                airport: selectedDestination,
                type: 'destination'
            });

            const [originResponse, destinationResponse] = await Promise.all([
                fetch('http://localhost:8000/api/flights/analyze-date-ranges', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        date_ranges: dateRangesPayload,
                        airport: selectedAirport || null,
                        type: 'origin'
                    })
                }),
                fetch('http://localhost:8000/api/flights/analyze-date-ranges', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        date_ranges: dateRangesPayload,
                        airport: selectedDestination || null,
                        type: 'destination'
                    })
                })
            ]);

            // Log responses for debugging
            const [originData, destinationData] = await Promise.all([
                originResponse.json(),
                destinationResponse.json()
            ]);

            console.log('Origin Data:', originData);
            console.log('Destination Data:', destinationData);

            const formattedOriginData = formatChartData(originData);
            const formattedDestinationData = formatChartData(destinationData);

            console.log('Formatted Origin Data:', formattedOriginData);
            console.log('Formatted Destination Data:', formattedDestinationData);

            setChartData(formattedOriginData);
            setDestinationChartData(formattedDestinationData);
        } catch (err) {
            console.error('Error in analyzeDateRanges:', err);
            setError('Error al analizar los datos: ' + err.message);
            setChartData([]);
            setDestinationChartData([]);
        } finally {
            setLoading(false);
        }
    };

    // Remove the second formatChartData function that was here
    // Add missing date range controls in return statement
    return (
        <div className="date-range-analysis">
            <h2>Análisis por Rangos de Fechas</h2>
            
            <div className="controls-card">
                <div className="airport-filters">
                    <div className="airport-filter">
                        <input
                            type="text"
                            value={selectedAirport}
                            onChange={(e) => setSelectedAirport(e.target.value)}
                            className="airport-input"
                            placeholder="Ingrese aeropuerto origen"
                        />
                    </div>
                    <div className="airport-filter">
                        <input
                            type="text"
                            value={selectedDestination}
                            onChange={(e) => setSelectedDestination(e.target.value)}
                            className="airport-input"
                            placeholder="Ingrese aeropuerto destino"
                        />
                    </div>
                </div>
                
                <div className="date-ranges-container">
                    {dateRanges.map((range) => (
                        <div key={range.id} className="date-range">
                            <span>{range.label}</span>
                            <input
                                type="date"
                                value={range.startDate}
                                onChange={(e) => handleDateChange(range.id, 'startDate', e.target.value)}
                            />
                            <input
                                type="date"
                                value={range.endDate}
                                onChange={(e) => handleDateChange(range.id, 'endDate', e.target.value)}
                            />
                            {dateRanges.length > 1 && (
                                <button onClick={() => removeDateRange(range.id)}>Eliminar</button>
                            )}
                        </div>
                    ))}
                </div>

                <div className="button-container">
                    <button onClick={addDateRange} className="add-range-btn">
                        Agregar Rango
                    </button>
                    <button onClick={analyzeDateRanges} className="analyze-btn" disabled={loading}>
                        {loading ? 'Analizando...' : 'Analizar'}
                    </button>
                </div>
            </div>

            {error && <div className="error-message">{error}</div>}

            <div className="charts-grid">
                <div className="chart-card">
                    <h3>Análisis por Aeropuerto de Origen</h3>
                    {chartData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={400}>
                            <LineChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis 
                                    dataKey="hour"
                                    label={{ value: 'Hora del día', position: 'bottom' }}
                                />
                                <YAxis 
                                    label={{ 
                                        value: 'Cantidad de vuelos (Origen)', 
                                        angle: -90, 
                                        position: 'insideLeft' 
                                    }}
                                />
                                <Tooltip />
                                <Legend />
                                {dateRanges.map((range, index) => (
                                    <Line
                                        key={range.id}
                                        type="monotone"
                                        dataKey={range.label}
                                        name={`${range.label} (${range.startDate} - ${range.endDate})`}
                                        stroke={getCustomColors(index)}
                                        strokeWidth={2}
                                        dot={false}
                                    />
                                ))}
                            </LineChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="no-data">No hay datos para mostrar</div>
                    )}
                </div>
            
                <div className="chart-card">
                    <h3>Análisis por Aeropuerto de Destino</h3>
                    {destinationChartData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={400}>
                            <LineChart data={destinationChartData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis 
                                    dataKey="hour"
                                    label={{ value: 'Hora del día', position: 'bottom' }}
                                />
                                <YAxis 
                                    label={{ 
                                        value: 'Cantidad de vuelos (Destino)', 
                                        angle: -90, 
                                        position: 'insideLeft' 
                                    }}
                                />
                                <Tooltip />
                                <Legend />
                                {dateRanges.map((range, index) => (
                                    <Line
                                        key={range.id}
                                        type="monotone"
                                        dataKey={range.label}
                                        name={`${range.label} (${range.startDate} - ${range.endDate})`}
                                        stroke={getCustomColors(index)}
                                        strokeWidth={2}
                                        dot={false}
                                    />
                                ))}
                            </LineChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="no-data">No hay datos para mostrar</div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default DateRangeAnalysis;