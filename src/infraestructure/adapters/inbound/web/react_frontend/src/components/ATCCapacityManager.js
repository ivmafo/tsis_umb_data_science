import React, { useState, useEffect } from 'react';
import './ATCCapacityManager.css';

function ATCCapacityManager() {
    const [sectorData, setSectorData] = useState(null);
    const [selectedSector, setSelectedSector] = useState('');
    const [selectedDate, setSelectedDate] = useState('');
    const [sectors, setSectors] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchSectors();
    }, []);

    const fetchSectors = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/sector-capacity/sectors');
            const data = await response.json();
            setSectors(data.sectors || []);
        } catch (error) {
            setError('Error fetching sectors');
            console.error('Error:', error);
        }
    };

    const fetchSectorCapacity = async () => {
        if (!selectedSector || !selectedDate) return;
        
        setLoading(true);
        setError('');
        try {
            const dateOnly = selectedDate.split('T')[0];
            const formattedDate = `${dateOnly} 00:00:00`;
            
            const response = await fetch(
                `http://localhost:8000/api/sector-capacity/${selectedSector}?date=${formattedDate}`
            );
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Server error: ${response.status}`);
            }
            
            const data = await response.json();
            if (!data) throw new Error('No data received');
            
            setSectorData(data);
        } catch (error) {
            setError(`Error: ${error.message}`);
            console.error('Request failed:', error);
            setSectorData(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (selectedSector && selectedDate) {
            fetchSectorCapacity();
        }
    }, [selectedSector, selectedDate]);

    const renderResults = () => {
        if (!sectorData) return null;
        
        const formatNumber = (value) => {
            if (value === null || value === undefined) return '-';
            const num = parseFloat(value);
            return isNaN(num) ? '-' : num.toFixed(2);
        };
        
        return (
            <div className="detailed-results">
                <div className="metric-section">
                    <h3>Métricas Principales</h3>
                    <div className="metrics-grid">
                        <div className="metric-item">
                            <h4>TPS</h4>
                            <p>{formatNumber(sectorData.tps)}</p>
                        </div>
                        <div className="metric-item">
                            <h4>TFC</h4>
                            <p>{formatNumber(sectorData.tfc)}</p>
                        </div>
                        <div className="metric-item">
                            <h4>Tiempo Comunicaciones</h4>
                            <p>{formatNumber(sectorData.tm)}</p>
                        </div>
                        <div className="metric-item">
                            <h4>Tiempo Coordinación</h4>
                            <p>{formatNumber(sectorData.tc)}</p>
                        </div>
                        <div className="metric-item">
                            <h4>Tiempo Tareas</h4>
                            <p>{formatNumber(sectorData.tt)}</p>
                        </div>
                        <div className="metric-item">
                            <h4>Factor Complejidad</h4>
                            <p>{formatNumber(sectorData.factor_complejidad)}</p>
                        </div>
                        <div className="metric-item">
                            <h4>SCV</h4>
                            <p>{formatNumber(sectorData.scv)}</p>
                        </div>
                        <div className="metric-item">
                            <h4>Capacidad Horaria</h4>
                            <p>{sectorData.capacidad_horaria || '-'}</p>
                        </div>
                        <div className="metric-item">
                            <h4>Carga de Trabajo Total</h4>
                            <p>{formatNumber(sectorData.carga_trabajo_total)}</p>
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="atc-capacity-manager">
            <h2>ATC Analisis de Capacidad de Sector</h2>
            
            <div className="control-panel">
                <input
                    type="text"
                    value={selectedSector}
                    onChange={(e) => setSelectedSector(e.target.value)}
                    placeholder="Ingrese codigo de Sector"
                />

                <input
                    type="date"
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                />
            </div>

            {error && <div className="error-message">{error}</div>}
            {loading && <div className="loading">Loading...</div>}
            {renderResults()}
        </div>
    );
}

export default ATCCapacityManager;