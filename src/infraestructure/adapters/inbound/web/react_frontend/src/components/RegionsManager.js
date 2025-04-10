import React, { useState, useEffect } from 'react';
import axios from 'axios';
import RegionsList from './RegionsList';
import RegionForm from './RegionForm';
import './Regions.css';

function RegionsManager() {
    const [regions, setRegions] = useState([]);
    const [selectedRegion, setSelectedRegion] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [isFormVisible, setIsFormVisible] = useState(false);

    const fetchRegions = async () => {
        setIsLoading(true);
        setError(null);
        try {
            console.log('Fetching regions...');
            const response = await axios.get('http://localhost:8000/api/regions');  // Update the URL
            console.log('Regions response:', response.data);
            setRegions(Array.isArray(response.data) ? response.data : []);
        } catch (err) {
            console.error('Error fetching regions:', err);
            setError(err.response?.data?.detail || 'Error al cargar las regiones');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchRegions();
    }, []);

    const handleCreateRegion = async (regionData) => {
        try {
            await axios.post('http://localhost:8000/api/regions', regionData);
            fetchRegions();
            setIsFormVisible(false);
        } catch (err) {
            console.error('Error creating region:', err.response?.data);
            setError(err.response?.data?.detail || 'Error al crear la región');
        }
    };

    const handleUpdateRegion = async (regionData) => {
        try {
            await axios.put(`http://localhost:8000/api/regions/${selectedRegion.id}`, regionData);
            fetchRegions();
            setIsFormVisible(false);
            setSelectedRegion(null);
        } catch (err) {
            console.error('Error updating region:', err.response?.data);
            setError(err.response?.data?.detail || 'Error al actualizar la región');
        }
    };

    const handleDeleteRegion = async (id) => {
        if (window.confirm('¿Está seguro de que desea eliminar esta región?')) {
            try {
                // Actualizar la URL para incluir el host y puerto correctos
                await axios.delete(`http://localhost:8000/api/regions/${id}`);
                fetchRegions();
            } catch (err) {
                console.error('Error deleting region:', err.response?.data);
                setError(err.response?.data?.detail || 'Error al eliminar la región');
            }
        }
    };

    const handleEdit = (region) => {
        setSelectedRegion(region);
        setIsFormVisible(true);
    };

    const handleCancel = () => {
        setSelectedRegion(null);
        setIsFormVisible(false);
    };

    return (
        <div className="regions-container">
            <div className="regions-header">
                <h2>Gestión de Regiones</h2>
                <button 
                    className="btn-primary"
                    onClick={() => setIsFormVisible(true)}
                >
                    Nueva Región
                </button>
            </div>

            {error && <div className="error-message">{error}</div>}

            {isFormVisible ? (
                <RegionForm
                    region={selectedRegion}
                    onSubmit={selectedRegion ? handleUpdateRegion : handleCreateRegion}
                    onCancel={handleCancel}
                />
            ) : (
                <RegionsList
                    regions={regions}
                    onEdit={handleEdit}
                    onDelete={handleDeleteRegion}
                    isLoading={isLoading}
                />
            )}
        </div>
    );
}

export default RegionsManager;