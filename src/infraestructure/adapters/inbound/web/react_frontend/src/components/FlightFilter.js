/**
 * Módulo que implementa los filtros de búsqueda para vuelos,
 * siguiendo los principios de arquitectura hexagonal y clean architecture.
 * 
 * Este componente actúa como un adaptador de interfaz de usuario en la capa
 * de infraestructura, gestionando los criterios de filtrado y comunicándose
 * con los puertos primarios para obtener las opciones disponibles.
 */

import React, { useState, useEffect } from 'react';
import './FlightFilter.css';

/**
 * Componente para filtrado de vuelos.
 * 
 * Implementa la interfaz de usuario para la selección de múltiples criterios
 * de filtrado, actuando como un adaptador primario que obtiene las opciones
 * disponibles a través de la API REST y comunica los cambios al componente padre.
 * 
 * @component
 * @param {Object} props - Propiedades del componente
 * @param {Function} props.onFilterChange - Callback para notificar cambios en los filtros
 */
function FlightFilter({ onFilterChange }) {
    // Add monthNames array definition
    const monthNames = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];
    
    // State declarations (keep only one of each)
    const [levelRange, setLevelRange] = useState({
        min: 0,
        max: 100000
    });
    const [levelRanges, setLevelRanges] = useState([]);
    const [selectedLevelRanges, setSelectedLevelRanges] = useState([]);
    const [airlines, setAirlines] = useState([]);
    const [selectedAirlines, setSelectedAirlines] = useState([]);
    const [flightTypes, setFlightTypes] = useState([]);
    const [selectedFlightTypes, setSelectedFlightTypes] = useState([]);
    const [destinations, setDestinations] = useState([]);
    const [selectedDestinations, setSelectedDestinations] = useState([]);
    const [years, setYears] = useState([]);
    const [months, setMonths] = useState([]);
    const [origins, setOrigins] = useState([]);
    const [selectedYears, setSelectedYears] = useState([]);
    const [selectedMonths, setSelectedMonths] = useState([]);
    const [selectedOrigins, setSelectedOrigins] = useState([]);
    const [aircraftTypes, setAircraftTypes] = useState([]);
    const [selectedAircraftTypes, setSelectedAircraftTypes] = useState([]);

    // Remove duplicate levelRange declaration and update useEffect
    useEffect(() => {
        fetchYears();
        fetchMonths();
        fetchOrigins();
        fetchDestinations();
        fetchFlightTypes();
        fetchAirlines();
        fetchAircraftTypes();
        fetchLevelRanges();
    }, []);

    // Combined handler for both numeric inputs and graph selection
    // Remove the duplicate handleLevelRangeChange and keep only this version
    const handleLevelRangeChange = (typeOrEvent, value) => {
        if (typeof typeOrEvent === 'object' && typeOrEvent.target.tagName === 'SELECT') {
            // Handle select input for graph
            const selectedOptions = Array.from(typeOrEvent.target.selectedOptions, option => option.value);
            setSelectedLevelRanges(selectedOptions);
            onFilterChange({ 
                years: selectedYears, 
                months: selectedMonths,
                origins: selectedOrigins,
                destinations: selectedDestinations,
                flightTypes: selectedFlightTypes,
                airlines: selectedAirlines,
                aircraftTypes: selectedAircraftTypes,
                levelRanges: selectedOptions,
                level_min: levelRange.min,
                level_max: levelRange.max
            });
        } else {
            // Handle numeric input
            const type = typeOrEvent; // 'min' or 'max'
            const newValue = value === '' ? (type === 'min' ? 0 : 100000) : parseInt(value);
            setLevelRange(prev => ({
                ...prev,
                [type]: newValue
            }));
            onFilterChange({ 
                years: selectedYears, 
                months: selectedMonths,
                origins: selectedOrigins,
                destinations: selectedDestinations,
                flightTypes: selectedFlightTypes,
                airlines: selectedAirlines,
                aircraftTypes: selectedAircraftTypes,
                levelRanges: selectedLevelRanges,
                level_min: type === 'min' ? newValue : levelRange.min,
                level_max: type === 'max' ? newValue : levelRange.max
            });
        }
    };

    // Remove the duplicate handleYearChange and keep only one version
    const handleYearChange = (e) => {
        const selectedOptions = Array.from(e.target.selectedOptions, option => option.value);
        setSelectedYears(selectedOptions);
        onFilterChange({ 
            years: selectedOptions, 
            months: selectedMonths,
            origins: selectedOrigins,
            destinations: selectedDestinations,
            flightTypes: selectedFlightTypes,
            airlines: selectedAirlines,
            aircraftTypes: selectedAircraftTypes,
            levelRanges: selectedLevelRanges,
            level_min: levelRange.min,
            level_max: levelRange.max
        });
    };

    const fetchLevelRanges = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/level-ranges');
            const data = await response.json();
            setLevelRanges(data || []);
        } catch (error) {
            console.error('Error fetching level ranges:', error);
        }
    };


    
    const fetchAircraftTypes = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/flights/aircraft-types');
            const data = await response.json();
            setAircraftTypes(data.aircraftTypes || []);
        } catch (error) {
            console.error('Error fetching aircraft types:', error);
        }
    };

    const fetchAirlines = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/flights/airlines');
            const data = await response.json();
            setAirlines(data.airlines || []);
        } catch (error) {
            console.error('Error fetching airlines:', error);
        }
    };


    // Update all existing handlers to include airlines in onFilterChange
    const fetchYears = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/flights/years');
            const data = await response.json();
            setYears(data.years || []);
        } catch (error) {
            console.error('Error fetching years:', error);
        }
    };

    const fetchMonths = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/flights/months');
            const data = await response.json();
            setMonths(data.months || []);
        } catch (error) {
            console.error('Error fetching months:', error);
        }
    };

    const fetchOrigins = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/flights/origins');
            const data = await response.json();
            setOrigins(data.origins || []);
        } catch (error) {
            console.error('Error fetching origins:', error);
        }
    };

    const fetchDestinations = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/flights/destinations');
            const data = await response.json();
            setDestinations(data.destinations || []);
        } catch (error) {
            console.error('Error fetching destinations:', error);
        }
    };

    const fetchFlightTypes = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/flights/flight-types');
            const data = await response.json();
            setFlightTypes(data.flightTypes || []);
        } catch (error) {
            console.error('Error fetching flight types:', error);
        }
    };



    const handleMonthChange = (e) => {
        const selectedOptions = Array.from(e.target.selectedOptions, option => option.value);
        setSelectedMonths(selectedOptions);
        onFilterChange({ 
            years: selectedYears, 
            months: selectedOptions,
            origins: selectedOrigins,
            destinations: selectedDestinations,
            flightTypes: selectedFlightTypes,
            airlines: selectedAirlines,
            aircraftTypes: selectedAircraftTypes,
            levelRanges: selectedLevelRanges,
            level_min: levelRange.min,
            level_max: levelRange.max
        });
    };

    // Make sure all handlers include levelRanges in addition to level_min and level_max
    const handleOriginChange = (e) => {
        const selectedOptions = Array.from(e.target.selectedOptions, option => option.value);
        setSelectedOrigins(selectedOptions);
        onFilterChange({ 
            years: selectedYears, 
            months: selectedMonths,
            origins: selectedOptions,
            destinations: selectedDestinations,
            flightTypes: selectedFlightTypes,
            airlines: selectedAirlines,
            aircraftTypes: selectedAircraftTypes,
            levelRanges: selectedLevelRanges,
            level_min: levelRange.min,
            level_max: levelRange.max
        });
    };

    const handleDestinationChange = (e) => {
        const selectedOptions = Array.from(e.target.selectedOptions, option => option.value);
        setSelectedDestinations(selectedOptions);
        onFilterChange({ 
            years: selectedYears, 
            months: selectedMonths,
            origins: selectedOrigins,
            destinations: selectedOptions,
            flightTypes: selectedFlightTypes,
            airlines: selectedAirlines,
            aircraftTypes: selectedAircraftTypes,
            levelRanges: selectedLevelRanges,
            level_min: levelRange.min,
            level_max: levelRange.max
        });
    };

    const handleFlightTypeChange = (e) => {
        const selectedOptions = Array.from(e.target.selectedOptions, option => option.value);
        setSelectedFlightTypes(selectedOptions);
        onFilterChange({ 
            years: selectedYears, 
            months: selectedMonths,
            origins: selectedOrigins,
            destinations: selectedDestinations,
            flightTypes: selectedOptions,
            airlines: selectedAirlines,
            aircraftTypes: selectedAircraftTypes,
            levelRanges: selectedLevelRanges,
            level_min: levelRange.min,
            level_max: levelRange.max
        });
    };

    const handleAirlineChange = (e) => {
        const selectedOptions = Array.from(e.target.selectedOptions, option => option.value);
        setSelectedAirlines(selectedOptions);
        onFilterChange({ 
            years: selectedYears, 
            months: selectedMonths,
            origins: selectedOrigins,
            destinations: selectedDestinations,
            flightTypes: selectedFlightTypes,
            airlines: selectedOptions,
            aircraftTypes: selectedAircraftTypes,
            levelRanges: selectedLevelRanges,
            level_min: levelRange.min,
            level_max: levelRange.max
        });
    };

    const handleAircraftTypeChange = (e) => {
        const selectedOptions = Array.from(e.target.selectedOptions, option => option.value);
        setSelectedAircraftTypes(selectedOptions);
        onFilterChange({ 
            years: selectedYears, 
            months: selectedMonths,
            origins: selectedOrigins,
            destinations: selectedDestinations,
            flightTypes: selectedFlightTypes,
            airlines: selectedAirlines,
            aircraftTypes: selectedOptions,
            levelRanges: selectedLevelRanges,
            level_min: levelRange.min,
            level_max: levelRange.max
        });
    };

        // In the return statement, add this new filter group before the helper text
    return (
        <div className="flight-filter">
            <div className="filter-group">
                <label>Años:</label>
                <select multiple value={selectedYears} onChange={handleYearChange} className="multiple-select">
                    {years.map(year => (
                        <option key={year} value={year}>{year}</option>
                    ))}
                </select>
            </div>

            <div className="filter-group">
                <label>Meses:</label>
                <select multiple value={selectedMonths} onChange={handleMonthChange} className="multiple-select">
                    {months.map(month => (
                        <option key={month} value={month}>{monthNames[month-1]}</option>
                    ))}
                </select>
            </div>

            <div className="filter-group">
                <label>Origen:</label>
                <select multiple value={selectedOrigins} onChange={handleOriginChange} className="multiple-select">
                    {origins.map(origin => (
                        <option key={origin} value={origin}>{origin}</option>
                    ))}
                </select>
            </div>

            <div className="filter-group">
                <label>Destino:</label>
                <select multiple value={selectedDestinations} onChange={handleDestinationChange} className="multiple-select">
                    {destinations.map(destination => (
                        <option key={destination} value={destination}>{destination}</option>
                    ))}
                </select>
            </div>

            <div className="filter-group">
                <label>Tipo de Vuelo:</label>
                <select multiple value={selectedFlightTypes} onChange={handleFlightTypeChange} className="multiple-select">
                    {flightTypes.map(type => (
                        <option key={type} value={type}>{type}</option>
                    ))}
                </select>
            </div>

            <div className="filter-group">
                <label>Empresa:</label>
                <select multiple value={selectedAirlines} onChange={handleAirlineChange} className="multiple-select">
                    {airlines.map(airline => (
                        <option key={airline} value={airline}>{airline}</option>
                    ))}
                </select>
            </div>

            <div className="filter-group">
                <label>Tipo de Aeronave:</label>
                <select multiple value={selectedAircraftTypes} onChange={handleAircraftTypeChange} className="multiple-select">
                    {aircraftTypes.map(type => (
                        <option key={type} value={type}>{type}</option>
                    ))}
                </select>
            </div>

            <div className="filter-group">
                <label>Nivel de Vuelo</label>
                <div className="level-range-inputs">
                    <input
                        type="number"
                        placeholder="Desde"
                        value={levelRange.min}
                        onChange={(e) => handleLevelRangeChange('min', e.target.value)}
                        min="0"
                        className="level-input"
                    />
                    <input
                        type="number"
                        placeholder="Hasta"
                        value={levelRange.max}
                        onChange={(e) => handleLevelRangeChange('max', e.target.value)}
                        min="0"
                        className="level-input"
                    />
                </div>
            </div>

            <small className="helper-text">
                Mantén presionado Ctrl (Cmd en Mac) para seleccionar múltiples opciones
            </small>
        </div>
    );
}

export default FlightFilter;