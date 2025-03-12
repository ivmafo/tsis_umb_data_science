import React, { useState } from 'react';
import FlightFilter from './FlightFilter';
import TreeMapChart from './TreeMapChart';
import DestinationTreeMap from './DestinationTreeMap';
import AirlineTreeMap from './AirlineTreeMap';
import FlightTypeBarChart from './FlightTypeBarChart';
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
            <h2>Tablero</h2>
            <FlightFilter onFilterChange={handleFilterChange} />
            <div className="charts-container">
                <div className="treemaps-container">
                    <TreeMapChart filters={filters} />
                    <DestinationTreeMap filters={filters} />
                    <AirlineTreeMap filters={filters} />
                </div>
                <div className="bar-charts-container">
                    <FlightTypeBarChart filters={filters} />
                </div>
            </div>
        </div>
    );
}

export default Dashboard;