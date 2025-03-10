import React, { useState, useEffect } from 'react';
import FlightFilter from './FlightFilter';
import TreeMapChart from './TreeMapChart';
import './Dashboard.css';

function Dashboard() {
    const [filters, setFilters] = useState({
        years: [],
        months: [],
        origins: [],
        destinations: [],
        flightTypes: [],
        airlines: [],
        aircraftTypes: [],
        levelRanges: []
    });

    const handleFilterChange = (newFilters) => {
        setFilters(newFilters);
    };

    return (
        <div className="dashboard">
            <h2>Dashboard</h2>
            <FlightFilter onFilterChange={handleFilterChange} />
            <TreeMapChart filters={filters} />
        </div>
    );
}

export default Dashboard;