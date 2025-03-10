import React, { useState, useEffect } from 'react';
import FlightFilter from './FlightFilter';
import './Dashboard.css';

function Dashboard() {
    const [stats, setStats] = useState({
        totalFiles: 0,
        processedFiles: 0,
        lastUpdate: null,
        flightStats: {
            totalFlights: 0,
            filteredFlights: 0
        }
    });
    const [filters, setFilters] = useState({});

    useEffect(() => {
        fetchDashboardData();
        if (filters.year) {
            fetchFlightStats();
        }
    }, [filters]);

    const fetchDashboardData = async () => {
        try {
            const response = await fetch('http://localhost:8000/files');
            const data = await response.json();
            setStats(prevStats => ({
                ...prevStats,
                totalFiles: data.files.length,
                processedFiles: data.files.length,
                lastUpdate: new Date().toLocaleString()
            }));
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
        }
    };

    const fetchFlightStats = async () => {
        try {
            const response = await fetch(`http://localhost:8000/api/flights/stats?year=${filters.year}`);
            const data = await response.json();
            setStats(prevStats => ({
                ...prevStats,
                flightStats: data
            }));
        } catch (error) {
            console.error('Error fetching flight stats:', error);
        }
    };

    const handleFilterChange = (newFilters) => {
        setFilters(newFilters);
    };

    return (
        <div className="dashboard">
            <h2>Tablero Principal</h2>
            <FlightFilter onFilterChange={handleFilterChange} />
            <div className="dashboard-content">
                <div className="dashboard-card">
                    <div className="card-header">
                        <i className="fas fa-file"></i>
                        <h3 className="card-title">Archivos Totales</h3>
                    </div>
                    <div className="metric">{stats.totalFiles}</div>
                    <div className="card-content">
                        Total de archivos en el sistema
                    </div>
                </div>

                <div className="dashboard-card">
                    <div className="card-header">
                        <i className="fas fa-check-circle"></i>
                        <h3 className="card-title">Archivos Procesados</h3>
                    </div>
                    <div className="metric">{stats.processedFiles}</div>
                    <div className="card-content">
                        Archivos procesados exitosamente
                    </div>
                </div>

                <div className="dashboard-card">
                    <div className="card-header">
                        <i className="fas fa-plane"></i>
                        <h3 className="card-title">Vuelos {filters.year ? `en ${filters.year}` : 'Totales'}</h3>
                    </div>
                    <div className="metric">{stats.flightStats.totalFlights}</div>
                    <div className="card-content">
                        Total de vuelos registrados
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;