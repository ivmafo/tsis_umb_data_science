import React, { useState } from 'react';
import FlightFilter from './FlightFilter';
import TreeMapChart from './TreeMapChart';
import DestinationTreeMap from './DestinationTreeMap';
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
            <div className="treemaps-container">
                <TreeMapChart filters={filters} />
                <DestinationTreeMap filters={filters} />
            </div>
        </div>
    );
}

export default Dashboard;