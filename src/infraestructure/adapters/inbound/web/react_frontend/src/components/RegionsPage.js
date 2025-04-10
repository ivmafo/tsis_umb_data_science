import React, { useState, useEffect } from 'react';
import axios from 'axios';
import RegionsList from './RegionsList';
import RegionForm from './RegionForm';

function RegionsPage() {
    const [regions, setRegions] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchRegions = async () => {
        try {
            setIsLoading(true);
            const response = await axios.get('/api/regions');
            console.log('Fetched regions:', response.data); // Debug log
            setRegions(response.data);
        } catch (error) {
            console.error('Error fetching regions:', error);
            setError('Error al cargar las regiones');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchRegions();
    }, []);

    // ... rest of the component code ...

    return (
        <div className="regions-page">
            <h2>Gestión de Regiones</h2>
            {error && <div className="alert alert-danger">{error}</div>}
            <RegionsList 
                regions={regions} 
                isLoading={isLoading}
                onEdit={handleEdit}
                onDelete={handleDelete}
            />
            {/* ... other components ... */}
        </div>
    );
}

export default RegionsPage;