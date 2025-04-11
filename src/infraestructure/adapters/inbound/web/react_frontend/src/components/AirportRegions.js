import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AirportRegions.css';

function AirportRegions() {
    const [airportRegions, setAirportRegions] = useState([]);
    const [regions, setRegions] = useState([]);
    const [formData, setFormData] = useState({
        icao_code: '',
        region_id: ''
    });
    const [editingId, setEditingId] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchAirportRegions();
        fetchRegions();
    }, []);

    const fetchAirportRegions = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/airport-regions');
            setAirportRegions(response.data);
            setIsLoading(false);
        } catch (err) {
            setError('Error fetching airport regions');
            setIsLoading(false);
        }
    };

    const fetchRegions = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/regions');
            setRegions(response.data);
        } catch (err) {
            setError('Error fetching regions');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editingId) {
                await axios.put(`http://localhost:8000/api/airport-regions/${editingId}`, formData);
            } else {
                await axios.post('http://localhost:8000/api/airport-regions', formData);
            }
            fetchAirportRegions();
            resetForm();
        } catch (err) {
            setError(err.response?.data?.detail || 'Error saving airport region');
        }
    };

    const handleEdit = (airportRegion) => {
        setFormData({
            icao_code: airportRegion.icao_code,
            region_id: airportRegion.region_id
        });
        setEditingId(airportRegion.id);
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this airport region?')) {
            try {
                await axios.delete(`http://localhost:8000/api/airport-regions/${id}`);
                fetchAirportRegions();
            } catch (err) {
                setError('Error deleting airport region');
            }
        }
    };

    const resetForm = () => {
        setFormData({
            icao_code: '',
            region_id: ''
        });
        setEditingId(null);
    };

    if (isLoading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;

    return (
        <div className="airport-regions-container">
            <div className="airport-regions-header">
                <h2>Airport Regions Management</h2>
            </div>

            <form className="airport-regions-form" onSubmit={handleSubmit}>
                <div className="form-group">
                    <input
                        type="text"
                        placeholder="ICAO Code"
                        value={formData.icao_code}
                        onChange={(e) => setFormData({...formData, icao_code: e.target.value})}
                        maxLength={10}
                        required
                    />
                    <select
                        value={formData.region_id}
                        onChange={(e) => setFormData({...formData, region_id: e.target.value})}
                        required
                    >
                        <option value="">Select Region</option>
                        {regions.map(region => (
                            <option key={region.id} value={region.id}>
                                {region.name}
                            </option>
                        ))}
                    </select>
                </div>
                <div className="button-group">
                    <button type="submit" className="btn btn-primary">
                        {editingId ? 'Update' : 'Create'} Airport Region
                    </button>
                    {editingId && (
                        <button type="button" className="btn btn-secondary" onClick={resetForm}>
                            Cancel
                        </button>
                    )}
                </div>
            </form>

            <table className="airport-regions-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>ICAO Code</th>
                        <th>Region</th>
                        <th>Created At</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {airportRegions.map(airportRegion => (
                        <tr key={airportRegion.id}>
                            <td>{airportRegion.id}</td>
                            <td>{airportRegion.icao_code}</td>
                            <td>
                                {regions.find(r => r.id === airportRegion.region_id)?.name || 
                                 airportRegion.region_id}
                            </td>
                            <td>
                                {new Date(airportRegion.created_at).toLocaleString()}
                            </td>
                            <td className="action-buttons">
                                <button 
                                    className="btn btn-secondary"
                                    onClick={() => handleEdit(airportRegion)}
                                >
                                    Edit
                                </button>
                                <button 
                                    className="btn btn-danger"
                                    onClick={() => handleDelete(airportRegion.id)}
                                >
                                    Delete
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default AirportRegions;