import React, { useState, useEffect } from 'react';
import { Line } from 'recharts';
import { ResponsiveContainer, LineChart, XAxis, YAxis, Tooltip, Legend, CartesianGrid, BarChart, Bar } from 'recharts';
import { FlightAnalysisService } from '../services/FlightAnalysisService';
import { FlightAnalysisAdapter } from '../adapters/FlightAnalysisAdapter';
import './DateRangeAnalysis.css';

const DateRangeAnalysis = () => {
    const [dateRanges, setDateRanges] = useState([{
        id: '1',
        startDate: '',
        endDate: '',
        label: 'Range 1',
        originAirport: '',
        destinationAirport: '',
        nivelMin: '',
        nivelMax: ''
    }]);
    const [chartData, setChartData] = useState([]);
    const [airports, setAirports] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [originChartData, setOriginChartData] = useState([]);
    const [destinationChartData, setDestinationChartData] = useState([]);
    const [monthlyOriginData, setMonthlyOriginData] = useState([]);
    const [monthlyDestinationData, setMonthlyDestinationData] = useState([]);

    useEffect(() => {
        fetchAirports();
    }, []);

    const validateDateRanges = () => {
        for (const range of dateRanges) {
            if (!range.startDate || !range.endDate) {
                setError('Por favor, complete las fechas de inicio y fin');
                return false;
            }
            if (!range.originAirport || !range.destinationAirport) {
                setError('Por favor, complete los aeropuertos de origen y destino');
                return false;
            }
            if (new Date(range.startDate) > new Date(range.endDate)) {
                setError('La fecha de inicio no puede ser posterior a la fecha de fin');
                return false;
            }
        }
        return true;
    };

    const addDateRange = () => {
        const newId = String(Math.max(...dateRanges.map(r => parseInt(r.id))) + 1);
        setDateRanges([...dateRanges, {
            id: newId,
            startDate: '',
            endDate: '',
            label: `Rango ${newId}`,
            originAirport: '',
            destinationAirport: '',
            nivelMin: '',
            nivelMax: ''
        }]);
    };

    const removeDateRange = (id) => {
        if (dateRanges.length > 1) {
            setDateRanges(ranges => ranges.filter(range => range.id !== id));
        }
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

    const formatChartData = (data) => {
        if (!Array.isArray(data)) {
            console.error('Invalid data format received:', data);
            return [];
        }
        
        return data.map(item => ({
            hour: `${String(item.hour).padStart(2, '0')}:00`,
            ...item.counts
        }));
    };

    const fetchAirports = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/flights/origins');
            if (!response.ok) {
                throw new Error('Failed to fetch airports');
            }
            const data = await response.json();
            setAirports(Array.isArray(data) ? data : []);
        } catch (err) {
            console.error('Error fetching airports:', err);
            setAirports([]);
            setError('Error loading airports');
        }
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

    const handleAirportChange = (id, field, value) => {
        setDateRanges(ranges => 
            ranges.map(range => 
                range.id === id 
                    ? { ...range, [field]: value }
                    : range
            )
        );
    };

    const handleLevelChange = (id, field, value) => {
        setDateRanges(ranges => 
            ranges.map(range => 
                range.id === id 
                    ? { ...range, [field]: value }
                    : range
            )
        );
    };

    const analyzeDateRanges = async () => {
        if (!validateDateRanges()) return;
    
        setLoading(true);
        setError('');
    
        try {
            const dateRangesPayload = dateRanges.map(range => ({
                id: String(range.id),
                start_date: range.startDate,
                end_date: range.endDate,
                label: range.label,
                origin_airport: range.originAirport,
                destination_airport: range.destinationAirport,
                nivel_min: parseInt(range.nivelMin) || 0,
                nivel_max: parseInt(range.nivelMax) || 99999
            }));
    
            console.log('Payload enviado:', dateRangesPayload);
    
            const [originData, destinationData, monthlyOrigin, monthlyDestination] = await Promise.all([
                FlightAnalysisService.analyzeFlights(dateRangesPayload, ''),
                FlightAnalysisService.analyzeFlights(dateRangesPayload, 'destination'),
                FlightAnalysisService.getMonthlyOriginAnalysis(dateRangesPayload),
                FlightAnalysisService.getMonthlyDestinationAnalysis(dateRangesPayload)
            ]);
    
            // Format hourly data
            const formattedOriginData = originData.map(item => ({
                hour: `${String(item.hour).padStart(2, '0')}:00`,
                ...dateRanges.reduce((acc, range) => ({
                    ...acc,
                    [range.label]: item[range.label] || 0
                }), {})
            }));
    
            const formattedDestinationData = destinationData.map(item => ({
                hour: `${String(item.hour).padStart(2, '0')}:00`,
                ...dateRanges.reduce((acc, range) => ({
                    ...acc,
                    [range.label]: item[range.label] || 0
                }), {})
            }));
    
            // Format monthly data
            const formattedMonthlyOrigin = monthlyOrigin.map(item => {
                const monthYear = `${item.year}-${String(item.month).padStart(2, '0')}`;
                const data = {
                    period: monthYear
                };
                
                // Add data for each range
                dateRanges.forEach(range => {
                    data[range.label] = item[range.label] || 0;
                });
                
                return data;
            });
    
            const formattedMonthlyDestination = monthlyDestination.map(item => {
                const monthYear = `${item.year}-${String(item.month).padStart(2, '0')}`;
                const data = {
                    period: monthYear
                };
                
                // Add data for each range
                dateRanges.forEach(range => {
                    data[range.label] = item[range.label] || 0;
                });
                
                return data;
            });
    
            // Update state
            setOriginChartData(formattedOriginData);
            setDestinationChartData(formattedDestinationData);
            setMonthlyOriginData(formattedMonthlyOrigin);
            setMonthlyDestinationData(formattedMonthlyDestination);
    
            // Debug logs
            console.log('Datos formateados origen:', formattedOriginData);
            console.log('Datos formateados destino:', formattedDestinationData);
            console.log('Datos mensuales origen:', formattedMonthlyOrigin);
            console.log('Datos mensuales destino:', formattedMonthlyDestination);
    
        } catch (error) {
            console.error('Error en el análisis:', error);
            setError('Error al analizar los datos: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    // En la parte del renderizado de las gráficas
    return (
        <div className="date-range-analysis-card">
            <div className="date-ranges-container">
                {dateRanges.map((range, index) => (
                    <div key={range.id} className="date-range-card">
                        <h3>{range.label}</h3>
                        <div className="date-inputs">
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
                        </div>
                        <div className="airport-inputs">
                            <input
                                type="text"
                                placeholder="Aeropuerto de origen"
                                value={range.originAirport}
                                onChange={(e) => handleAirportChange(range.id, 'originAirport', e.target.value)}
                            />
                            <input
                                type="text"
                                placeholder="Aeropuerto de destino"
                                value={range.destinationAirport}
                                onChange={(e) => handleAirportChange(range.id, 'destinationAirport', e.target.value)}
                            />
                        </div>
                        <div className="level-inputs">
                            <input
                                type="number"
                                placeholder="Nivel mínimo"
                                value={range.nivelMin}
                                onChange={(e) => handleLevelChange(range.id, 'nivelMin', e.target.value)}
                            />
                            <input
                                type="number"
                                placeholder="Nivel máximo"
                                value={range.nivelMax}
                                onChange={(e) => handleLevelChange(range.id, 'nivelMax', e.target.value)}
                            />
                        </div>
                        {dateRanges.length > 1 && (
                            <button onClick={() => removeDateRange(range.id)}>Eliminar</button>
                        )}
                    </div>
                ))}
                <button onClick={addDateRange}>Agregar Rango</button>
                <button onClick={analyzeDateRanges} disabled={loading}>
                    {loading ? 'Analizando...' : 'Analizar'}
                </button>
            </div>

            {error && <div className="error-message">{error}</div>}

            {originChartData.length > 0 && (
                <div className="chart-container">
                    <h3>Análisis por Origen</h3>
                    <ResponsiveContainer width="100%" height={400}>
                        <LineChart data={originChartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="hour" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            {dateRanges.map((range, index) => (
                                <Line
                                    key={range.id}
                                    type="monotone"
                                    dataKey={range.label}
                                    stroke={getCustomColors(index)}
                                    dot={true}
                                />
                            ))}
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            )}

            {destinationChartData.length > 0 && (
                <div className="chart-container">
                    <h3>Análisis por Destino</h3>
                    <ResponsiveContainer width="100%" height={400}>
                        <LineChart data={destinationChartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="hour" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            {dateRanges.map((range, index) => (
                                <Line
                                    key={range.id}
                                    type="monotone"
                                    dataKey={range.label}
                                    stroke={getCustomColors(index)}
                                    dot={true}
                                />
                            ))}
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            )}


            {/* Monthly Analysis by Origin */}
            {monthlyOriginData.length > 0 && (
                <div className="chart-container">
                    <h3>Análisis Mensual por Origen</h3>
                    <ResponsiveContainer width="100%" height={400}>
                        <BarChart data={monthlyOriginData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis 
                                dataKey="period" 
                                label={{ value: 'Mes/Año', position: 'bottom' }}
                            />
                            <YAxis label={{ value: 'Cantidad de Vuelos', angle: -90, position: 'left' }} />
                            <Tooltip />
                            <Legend />
                            {dateRanges.map((range, index) => (
                                <Bar
                                    key={range.id}
                                    dataKey={range.label}
                                    fill={getCustomColors(index)}
                                />
                            ))}
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            )}

            {monthlyDestinationData.length > 0 && (
                <div className="chart-container">
                    <h3>Análisis Mensual por Destino</h3>
                    <ResponsiveContainer width="100%" height={400}>
                        <BarChart data={monthlyDestinationData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis 
                                dataKey="period" 
                                label={{ value: 'Mes/Año', position: 'bottom' }}
                            />
                            <YAxis label={{ value: 'Cantidad de Vuelos', angle: -90, position: 'left' }} />
                            <Tooltip />
                            <Legend />
                            {dateRanges.map((range, index) => (
                                <Bar
                                    key={range.id}
                                    dataKey={range.label}
                                    fill={getCustomColors(index)}
                                />
                            ))}
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            )}



        </div>
    );
};

export default DateRangeAnalysis;