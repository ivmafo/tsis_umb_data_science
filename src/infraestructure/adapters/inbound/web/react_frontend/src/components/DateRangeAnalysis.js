import React, { useState, useEffect } from 'react';
import { Line } from 'recharts';
import { ResponsiveContainer, LineChart, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';
import { FlightAnalysisService } from '../services/FlightAnalysisService';
import { FlightAnalysisAdapter } from '../adapters/FlightAnalysisAdapter';
import './DateRangeAnalysis.css';

const DateRangeAnalysis = () => {
    const [dateRanges, setDateRanges] = useState([{ 
        id: 1, 
        startDate: '', 
        endDate: '',
        label: 'Rango 1',
        originAirport: '',
        destinationAirport: ''
    }]);
    const [chartData, setChartData] = useState([]);
    const [airports, setAirports] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [originChartData, setOriginChartData] = useState([]);
    const [destinationChartData, setDestinationChartData] = useState([]);

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
        const newId = Math.max(...dateRanges.map(r => r.id)) + 1;
        setDateRanges([...dateRanges, {
            id: newId,
            startDate: '',
            endDate: '',
            label: `Rango ${newId}`,
            originAirport: '',  // Añadido campo faltante
            destinationAirport: ''  // Añadido campo faltante
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

    const analyzeDateRanges = async () => {
        if (!validateDateRanges()) {
            setError('Por favor, complete todos los campos requeridos');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const dateRangesPayload = FlightAnalysisAdapter.toDateRangeDTO(dateRanges);

            const [originData, destinationData] = await Promise.all([
                FlightAnalysisService.analyzeFlights(dateRangesPayload, 'origin_analysis'),
                FlightAnalysisService.analyzeFlights(dateRangesPayload, 'destination_analysis')
            ]);

            if (!Array.isArray(originData) || !Array.isArray(destinationData)) {
                throw new Error('Invalid data format received from server');
            }

            setOriginChartData(FlightAnalysisAdapter.formatChartData(originData));
            setDestinationChartData(FlightAnalysisAdapter.formatChartData(destinationData));
        } catch (err) {
            console.error('Error:', err);
            setError('Error al analizar los datos: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="date-range-analysis">
            <div className="controls-card">
                <div className="top-controls">
                    <h2>Análisis por Rangos de Fecha</h2>
                    <div className="top-buttons">
                        <button onClick={addDateRange} className="add-range-btn">
                            <i className="fas fa-plus"></i> Agregar Rango
                        </button>
                        <button onClick={analyzeDateRanges} className="analyze-btn" disabled={loading}>
                            <i className="fas fa-chart-line"></i> {loading ? 'Analizando...' : 'Analizar'}
                        </button>
                    </div>
                </div>

                <div className="date-ranges-container">
                    {dateRanges.map((range) => (
                        <div key={range.id} className="date-range-input">
                            <div className="range-header">
                                <h4>{range.label}</h4>
                                {dateRanges.length > 1 && (
                                    <button 
                                        onClick={() => removeDateRange(range.id)}
                                        className="remove-range-btn"
                                    >
                                        <i className="fas fa-times"></i>
                                    </button>
                                )}
                            </div>
                            <div className="range-content">
                                <div className="date-inputs">
                                    <div className="input-wrapper">
                                        <label>Inicio</label>
                                        <input
                                            type="date"
                                            value={range.startDate}
                                            onChange={(e) => handleDateChange(range.id, 'startDate', e.target.value)}
                                        />
                                    </div>
                                    <div className="input-wrapper">
                                        <label>Fin</label>
                                        <input
                                            type="date"
                                            value={range.endDate}
                                            onChange={(e) => handleDateChange(range.id, 'endDate', e.target.value)}
                                        />
                                    </div>
                                </div>
                                <div className="airport-inputs">
                                    <div className="input-wrapper">
                                        <label>Origen</label>
                                        <input
                                            type="text"
                                            value={range.originAirport}
                                            onChange={(e) => handleAirportChange(range.id, 'originAirport', e.target.value)}
                                        />
                                    </div>
                                    <div className="input-wrapper">
                                        <label>Destino</label>
                                        <input
                                            type="text"
                                            value={range.destinationAirport}
                                            onChange={(e) => handleAirportChange(range.id, 'destinationAirport', e.target.value)}
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
                
                {error && <div className="error-message">{error}</div>}

                <div className="charts-grid">
                    <div className="chart">
                        <h3>
                            <i className="fas fa-plane-departure"></i>
                            {' '}Vuelos por Origen
                        </h3>
                        <ResponsiveContainer width="100%" height={400}>
                            <LineChart 
                                data={originChartData}
                                margin={{ top: 30, right: 30, left: 20, bottom: 20 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                <XAxis 
                                    dataKey="hour"
                                    label={{ value: 'Hora del día', position: 'insideBottom', offset: -10 }}
                                    tick={{ fill: '#666' }}
                                />
                                <YAxis 
                                    label={{ 
                                        value: 'Cantidad de vuelos (Origen)', 
                                        angle: -90, 
                                        position: 'insideLeft',
                                        offset: -5,
                                        style: { fill: '#666' }
                                    }}
                                    tick={{ fill: '#666' }}
                                />
                                <Legend 
                                    verticalAlign="top"
                                    align="center"
                                    height={36}
                                    wrapperStyle={{
                                        paddingTop: "20px",
                                        paddingBottom: "20px",
                                        marginBottom: "10px"
                                    }}
                                />
                                {Object.keys(originChartData[0] || {})
                                    .filter(key => key !== 'hour')
                                    .map((key, index) => (
                                        <Line
                                            key={key}
                                            type="monotone"
                                            dataKey={key}
                                            stroke={getCustomColors(index)}
                                            name={key}
                                            strokeWidth={2}
                                            dot={{ r: 4 }}
                                            activeDot={{ r: 6 }}
                                        />
                                    ))}
                            </LineChart>
                        </ResponsiveContainer>
                    </div>

                    <div className="chart">
                        <h3>
                            <i className="fas fa-plane-arrival"></i>
                            {' '}Vuelos por Destino
                        </h3>
                        <ResponsiveContainer width="100%" height={500}>
                            <LineChart 
                                data={destinationChartData}
                                margin={{ top: 40, right: 30, left: 20, bottom: 60 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                <XAxis 
                                    dataKey="hour"
                                    label={{ value: 'Hora del día', position: 'bottom', offset: 40 }}
                                    tick={{ fill: '#666' }}
                                    angle={-45}
                                    textAnchor="end"
                                    height={60}
                                />
                                <YAxis 
                                    label={{ 
                                        value: 'Cantidad de vuelos (Destino)', 
                                        angle: -90, 
                                        position: 'insideLeft',
                                        offset: -10,
                                        style: { fill: '#666' }
                                    }}
                                    tick={{ fill: '#666' }}
                                />
                                <Legend 
                                    verticalAlign="top"
                                    align="center"
                                    wrapperStyle={{
                                        paddingTop: "10px",
                                        paddingBottom: "20px"
                                    }}
                                    layout="horizontal"
                                    formatter={(value) => <span style={{ 
                                        color: '#666', 
                                        padding: '0 10px',
                                        maxWidth: '150px',
                                        whiteSpace: 'normal',
                                        wordWrap: 'break-word'
                                    }}>{value}</span>}
                                />
                                <Tooltip 
                                    contentStyle={{ 
                                        background: 'rgba(255, 255, 255, 0.95)',
                                        border: '1px solid #e0e0e0',
                                        borderRadius: '8px',
                                        boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
                                    }}
                                />
                                <Tooltip 
                                    contentStyle={{ 
                                        background: 'rgba(255, 255, 255, 0.95)',
                                        border: '1px solid #e0e0e0',
                                        borderRadius: '8px',
                                        boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
                                    }}
                                />
                                {Object.keys(destinationChartData[0] || {})
                                    .filter(key => key !== 'hour')
                                    .map((key, index) => (
                                        <Line
                                            key={key}
                                            type="monotone"
                                            dataKey={key}
                                            stroke={getCustomColors(index)}
                                            name={key}
                                            strokeWidth={2}
                                            dot={{ r: 4 }}
                                            activeDot={{ r: 6 }}
                                        />
                                    ))}
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DateRangeAnalysis;