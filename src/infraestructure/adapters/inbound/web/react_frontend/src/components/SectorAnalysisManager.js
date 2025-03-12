import React, { useState, useEffect } from 'react';
import './SectorAnalysisManager.css';

const SectorAnalysisManager = () => {
    const [sectors, setSectors] = useState([]);
    const [selectedSector, setSelectedSector] = useState('');
    const [dateRange, setDateRange] = useState({
        startDate: '',
        endDate: ''
    });
    const [analysisData, setAnalysisData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchSectors();
    }, []);

    const fetchSectors = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/sector-analysis/sectors');
            const data = await response.json();
            setSectors(data);
        } catch (error) {
            setError('Error al cargar sectores');
        }
    };

    // Add these state variables at the beginning of the component
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const pageSize = 10000;
    
    // Update the fetchAnalysisData function
    const fetchAnalysisData = async () => {
        if (!selectedSector || !dateRange.startDate || !dateRange.endDate) return;
        
        setLoading(true);
        try {
            console.log('Fetching data with params:', {
                sector: selectedSector,
                startDate: dateRange.startDate,
                endDate: dateRange.endDate,
                currentPage,
                pageSize
            });

            const response = await fetch(
                `http://localhost:8000/api/sector-analysis/${selectedSector}?start_date=${dateRange.startDate}&end_date=${dateRange.endDate}&page=${currentPage}&page_size=${pageSize}`
            );
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Received data:', data);
            
            setAnalysisData(data.items || []);
            setTotalPages(Math.ceil(data.total / pageSize));
            setError('');
        } catch (error) {
            console.error('Error fetching data:', error);
            setError('Error al cargar datos de análisis: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (selectedSector && dateRange.startDate && dateRange.endDate) {
            fetchAnalysisData();
        }
    }, [selectedSector, dateRange.startDate, dateRange.endDate]);

    const formatDecimal = (value) => {
        return typeof value === 'number' ? value.toFixed(2) : value;
    };

    return (
        <div className="sector-analysis-manager">
            <h2>Análisis Detallado de Sectores</h2>
            
            <div className="controls">
                <input 
                    type="text"
                    value={selectedSector}
                    onChange={(e) => setSelectedSector(e.target.value)}
                    placeholder="Ingrese el sector"
                    className="sector-input"
                />

                <input
                    type="date"
                    value={dateRange.startDate}
                    onChange={(e) => setDateRange({...dateRange, startDate: e.target.value})}
                    className="date-input"
                />

                <input
                    type="date"
                    value={dateRange.endDate}
                    onChange={(e) => setDateRange({...dateRange, endDate: e.target.value})}
                    className="date-input"
                />
            </div>

            {error && <div className="error-message">{error}</div>}
            {loading && <div className="loading">Cargando datos...</div>}

            {analysisData.length > 0 && (
                <>
                    <div className="pagination-controls">
                        <button 
                            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                            disabled={currentPage === 1}
                        >
                            Anterior
                        </button>
                        <span>Página {currentPage} de {totalPages}</span>
                        <button 
                            onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                            disabled={currentPage === totalPages}
                        >
                            Siguiente
                        </button>
                    </div>

                    <div className="analysis-table">
                        <table>
                            <thead>
                                <tr>
                                    <th>Hora</th>
                                    <th>Número de Vuelos</th>
                                    <th>TPS</th>
                                    <th>Tipos de Aeronaves</th>
                                    <th>Aerolíneas</th>
                                    <th>Tipos de Vuelo</th>
                                    <th>Tiempo Comunicaciones</th>
                                    <th>Tiempo Coordinación</th>
                                    <th>Tiempo Tareas</th>
                                    <th>Factor Complejidad</th>
                                </tr>
                            </thead>
                            <tbody>
                                {analysisData.map((analysis, index) => (
                                    <tr key={index}>
                                        <td>{new Date(analysis.hora).toLocaleString()}</td>
                                        <td>{analysis.num_vuelos}</td>
                                        <td>{formatDecimal(analysis.tps)}</td>
                                        <td>{analysis.tipos_aeronaves}</td>
                                        <td>{analysis.aerolineas}</td>
                                        <td>{analysis.tipos_vuelo}</td>
                                        <td>{formatDecimal(analysis.tiempo_total_comunicaciones)}</td>
                                        <td>{formatDecimal(analysis.tiempo_total_coordinacion)}</td>
                                        <td>{formatDecimal(analysis.tiempo_tareas_observables)}</td>
                                        <td>{formatDecimal(analysis.factor_complejidad)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </>
            )}
        </div>
    );
};

export default SectorAnalysisManager;