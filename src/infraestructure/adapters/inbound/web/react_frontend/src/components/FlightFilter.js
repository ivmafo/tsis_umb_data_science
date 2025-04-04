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
    /**
     * Obtiene las opciones disponibles para cada criterio de filtrado.
     * 
     * @async
     * @function
     * @throws {Error} Error en la obtención de datos
     */
    const fetchOptions = async () => {
        // Agrupa todas las funciones fetch
        await Promise.all([
            fetchYears(),
            fetchMonths(),
            fetchOrigins(),
            fetchDestinations(),
            fetchFlightTypes(),
            fetchAirlines(),
            fetchAircraftTypes(),
            fetchLevelRanges()
        ]);
    };

    /**
     * Maneja los cambios en cualquier filtro y notifica al componente padre.
     * 
     * @function
     * @param {string} filterType - Tipo de filtro modificado
     * @param {Array} selectedOptions - Opciones seleccionadas
     */
    const handleFilterChange = (filterType, selectedOptions) => {
        // Las funciones handle*Change existentes implementan esta lógica
    };

    // State declarations
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

    const monthNames = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    };

    // Add these state declarations with the other states at the top
    // State declarations for level ranges
    const [levelRanges, setLevelRanges] = useState([]);
    const [selectedLevelRanges, setSelectedLevelRanges] = useState([]);
    
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
    
    const fetchLevelRanges = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/level-ranges');
            const data = await response.json();
            setLevelRanges(data || []);
        } catch (error) {
            console.error('Error fetching level ranges:', error);
        }
    };
    
    const handleLevelRangeChange = (e) => {
        const selectedOptions = Array.from(e.target.selectedOptions, option => option.value);
        setSelectedLevelRanges(selectedOptions);
        onFilterChange({ 
            years: selectedYears, 
            months: selectedMonths, 
            origins: selectedOrigins,
            destinations: selectedDestinations,
            flightTypes: selectedFlightTypes,
            airlines: selectedAirlines,
            aircraftTypes: selectedAircraftTypes,
            levelRanges: selectedOptions
        });
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
            levelRanges: selectedLevelRanges  // Agregar esta línea
        });
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
            levelRanges: selectedLevelRanges
        });
    };

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
            levelRanges: selectedLevelRanges
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
            levelRanges: selectedLevelRanges
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
            levelRanges: selectedLevelRanges
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
            levelRanges: selectedLevelRanges
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
            levelRanges: selectedLevelRanges
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
                        <option key={month} value={month}>{monthNames[month]}</option>
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
                <label>Rango de Nivel:</label>
                <select multiple value={selectedLevelRanges} onChange={handleLevelRangeChange} className="multiple-select">
                    {levelRanges.map(range => (
                        <option key={range.id} value={range.id}>
                            {range.alias} ({range.min_level} - {range.max_level})
                        </option>
                    ))}
                </select>
            </div>
            {/* Remove the entire level ranges filter group that was here */}

            <small className="helper-text">
                Mantén presionado Ctrl (Cmd en Mac) para seleccionar múltiples opciones
            </small>
        </div>
    );
}

export default FlightFilter;
