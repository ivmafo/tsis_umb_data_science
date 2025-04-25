import React, { useState, useEffect } from 'react';
import { Line } from 'recharts';
import { ResponsiveContainer, LineChart, XAxis, YAxis, Tooltip, Legend, CartesianGrid, BarChart, Bar } from 'recharts';
import { FlightAnalysisService } from '../services/FlightAnalysisService';
import { FlightAnalysisAdapter } from '../adapters/FlightAnalysisAdapter';
import './DateRangeAnalysis.css';

import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
            
import * as turf from '@turf/turf';

// At the top of the file, add these imports
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png')
});

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
    const [firData, setFirData] = useState([]);

    const generateColorFromString = (str) => {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = str.charCodeAt(i) + ((hash << 5) - hash);
        }
        const c = (hash & 0x00FFFFFF)
            .toString(16)
            .toUpperCase();
        return '#' + '00000'.substring(0, 6 - c.length) + c;
    };
    
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

    // Agregar después de los estados existentes
    const [yearlyOriginData, setYearlyOriginData] = useState([]);
    const [yearlyDestinationData, setYearlyDestinationData] = useState([]);
    
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
    
            // Inside analyzeDateRanges function, add to the Promise.all array:
            // In analyzeDateRanges function, remove the duplicate line and extra bracket
            const [originData, destinationData, monthlyOrigin, monthlyDestination, yearlyOrigin, yearlyDestination, firResults] = await Promise.all([
            FlightAnalysisService.analyzeFlights(dateRangesPayload, ''),
            FlightAnalysisService.analyzeFlights(dateRangesPayload, 'destination'),
            FlightAnalysisService.getMonthlyOriginAnalysis(dateRangesPayload),
            FlightAnalysisService.getMonthlyDestinationAnalysis(dateRangesPayload),
            FlightAnalysisService.getYearlyOriginAnalysis(dateRangesPayload),
            FlightAnalysisService.getYearlyDestinationAnalysis(dateRangesPayload),
            FlightAnalysisService.getFlightCountsByFir(dateRangesPayload)
            ]);
    
            
    
            // After other state updates, add:
            setFirData(firResults);
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
    
            // Format yearly data
            const formattedYearlyOrigin = yearlyOrigin.map(item => ({
                year: item.year,
                ...dateRanges.reduce((acc, range) => ({
                    ...acc,
                    [range.label]: item[range.label] || 0
                }), {})
            }));
    
            const formattedYearlyDestination = yearlyDestination.map(item => ({
                year: item.year,
                ...dateRanges.reduce((acc, range) => ({
                    ...acc,
                    [range.label]: item[range.label] || 0
                }), {})
            }));
    
            // Update all states including yearly data
            setOriginChartData(formattedOriginData);
            setDestinationChartData(formattedDestinationData);
            setMonthlyOriginData(formattedMonthlyOrigin);
            setMonthlyDestinationData(formattedMonthlyDestination);
            setYearlyOriginData(formattedYearlyOrigin);
            setYearlyDestinationData(formattedYearlyDestination);
    
            // Add debug logs for yearly data
            console.log('Datos anuales origen:', formattedYearlyOrigin);
            console.log('Datos anuales destino:', formattedYearlyDestination);
    
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

            <div className="charts-grid">
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

                {yearlyOriginData.length > 0 && (
                    <div className="chart-container">
                        <h3>Análisis Anual por Origen</h3>
                        <ResponsiveContainer width="100%" height={400}>
                            <BarChart data={yearlyOriginData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="year" />
                                <YAxis />
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

                {yearlyDestinationData.length > 0 && (
                    <div className="chart-container">
                        <h3>Análisis Anual por Destino</h3>
                        <ResponsiveContainer width="100%" height={400}>
                            <BarChart data={yearlyDestinationData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="year" />
                                <YAxis />
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
            
            
            
            
            <div className="table-container">
                <h3>Análisis por FIR y Coordenadas</h3>
                <div className="table-wrapper">
                    <table className="fir-table">
                        <thead>
                            <tr>
                                <th>Etiqueta</th>
                                <th>Origen</th>
                                <th>Destino</th>
                                <th>FIR</th>
                                <th>Coordenadas Origen</th>
                                <th>Coordenadas Destino</th>
                                <th>Cantidad</th>
                            </tr>
                        </thead>
                        <tbody>
                            {firData.map((row, index) => (
                                <tr key={index}>
                                    <td>{row.label || 'N/A'}</td>
                                    <td>{row.origen || row.origin || 'N/A'}</td>
                                    <td>{row.destino || row.destination || 'N/A'}</td>
                                    <td>{row.fir || 'N/A'}</td>
                                    <td>{`(${row.latitude_origen || row.latitude_origin || 'N/A'}, ${row.longitude_origen || row.longitude_origin || 'N/A'})`}</td>
                                    <td>{`(${row.latitude_destino || row.latitude_destination || 'N/A'}, ${row.longitude_destino || row.longitude_destination || 'N/A'})`}</td>
                                    <td>{row.count || 0}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
            

            
            
        
            // Reemplazar la sección del mapa
            <div className="map-container" style={{ height: '500px', marginTop: '20px' }}>
                <h3>Mapa de Rutas de Vuelo</h3>
                {firData && firData.length > 0 && (
                    <MapContainer
                        center={[4.6097, -74.0817]}
                        zoom={5}
                        style={{ height: '100%', width: '100%' }}
                    >
                        <TileLayer
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        />
                        {firData.map((flight, index) => {
                            const originPosition = [
                                parseFloat(flight.latitude_origen || flight.latitude_origin) || 0,
                                parseFloat(flight.longitude_origen || flight.longitude_origin) || 0
                            ];
                            const destPosition = [
                                parseFloat(flight.latitude_destino || flight.latitude_destination) || 0,
                                parseFloat(flight.longitude_destino || flight.longitude_destination) || 0
                            ];
        
                            const start = turf.point([originPosition[1], originPosition[0]]);
                            const end = turf.point([destPosition[1], destPosition[0]]);
                            const greatCircle = turf.greatCircle(start, end, {
                                npoints: 200,
                                offset: 20
                            });
        
                            const arcCoords = greatCircle.geometry.coordinates.map(coord => [coord[1], coord[0]]);
                            // Usar el mismo color que en las gráficas basado en el índice del rango
                            const rangeIndex = dateRanges.findIndex(range => range.label === flight.label);
                            const routeColor = getCustomColors(rangeIndex);
        
                            return (
                                <React.Fragment key={index}>
                                    <Marker position={originPosition}>
                                        <Popup>
                                            Origen: {flight.origen || flight.origin}<br />
                                            FIR: {flight.fir}<br />
                                            No Vuelos: {flight.count}
                                        </Popup>
                                    </Marker>
                                    <Marker position={destPosition}>
                                        <Popup>
                                            Destino: {flight.destino || flight.destination}<br />
                                            FIR: {flight.fir}<br />
                                            No Vuelos: {flight.count}
                                        </Popup>
                                    </Marker>
                                    <Polyline
                                        positions={arcCoords}
                                        color={routeColor}
                                        weight={2}
                                        opacity={0.7}
                                    />
                                </React.Fragment>
                            );
                        })}
                    </MapContainer>
                )}
            </div>
        </div>
    );
};

export default DateRangeAnalysis;