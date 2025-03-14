import React, { useState, useEffect } from 'react';
import './LevelRangesManager.css';

function LevelRangesManager() {
    const [ranges, setRanges] = useState([]);
    const [newRange, setNewRange] = useState({
        origen: '',
        destino: '',
        nivel_min: '',
        nivel_max: '',
        ruta: '',
        zona: ''
    });
    const [editingRange, setEditingRange] = useState(null);
    const [message, setMessage] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [filteredRanges, setFilteredRanges] = useState([]);

    useEffect(() => {
        fetchRanges();
    }, []);

    const fetchRanges = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/level-ranges');
            const data = await response.json();
            
            // Validate and filter out invalid entries
            const validRanges = data.filter(range => 
                range && 
                typeof range.origen === 'string' && 
                typeof range.destino === 'string' && 
                typeof range.nivel_min === 'number' && 
                typeof range.nivel_max === 'number' && 
                typeof range.ruta === 'string' && 
                typeof range.zona === 'string'
            );
            
            setRanges(validRanges);
            if (validRanges.length < data.length) {
                setMessage('Some ranges were filtered due to invalid data');
            } else {
                setMessage('');
            }
        } catch (error) {
            console.error('Error fetching ranges:', error);
            setMessage('Error loading level ranges');
            setRanges([]);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsProcessing(true);

        // Validate data before sending
        const dataToSend = {
            ...newRange,
            nivel_min: newRange.nivel_min || 0,
            nivel_max: newRange.nivel_max || 0,
            origen: newRange.origen || '',
            destino: newRange.destino || '',
            ruta: newRange.ruta || '',
            zona: newRange.zona || ''
        };

        try {
            const url = editingRange 
                ? `http://localhost:8000/api/level-ranges/${editingRange.id}`
                : 'http://localhost:8000/api/level-ranges';
            
            const response = await fetch(url, {
                method: editingRange ? 'PUT' : 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(dataToSend),
            });

            const result = await response.json();
            
            if (response.ok) {
                setMessage(editingRange ? 'Range updated successfully' : 'Range created successfully');
                setNewRange({
                    origen: '',
                    destino: '',
                    nivel_min: '',
                    nivel_max: '',
                    ruta: '',
                    zona: ''
                });
                setEditingRange(null);
                fetchRanges();
            } else {
                setMessage(`Error: ${result.detail || 'Unknown error occurred'}`);
            }
        } catch (error) {
            console.error('Error processing range:', error);
            setMessage('Error processing range');
        } finally {
            setIsProcessing(false);
        }
    };

    const startEditing = (range) => {
        setEditingRange(range);
        setNewRange({
            origen: range.origen,
            destino: range.destino,
            nivel_min: range.nivel_min,
            nivel_max: range.nivel_max,
            ruta: range.ruta,
            zona: range.zona
        });
    };

    const cancelEditing = () => {
        setEditingRange(null);
        setNewRange({
            origen: '',
            destino: '',
            nivel_min: '',
            nivel_max: '',
            ruta: '',
            zona: ''
        });
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this range?')) {
            try {
                const response = await fetch(`http://localhost:8000/api/level-ranges/${id}`, {
                    method: 'DELETE',
                });
                if (response.ok) {
                    fetchRanges();
                    setMessage('Range successfully deleted');
                } else {
                    const error = await response.json();
                    setMessage(`Error: ${error.detail}`);
                }
            } catch (error) {
                setMessage('Error deleting range');
            }
        }
    };

    const handleSearch = (e) => {
        const term = e.target.value.toLowerCase();
        setSearchTerm(term);
        
        const filtered = ranges.filter(range => 
            range.origen.toLowerCase().includes(term) ||
            range.destino.toLowerCase().includes(term) ||
            range.ruta.toLowerCase().includes(term) ||
            range.zona.toLowerCase().includes(term) ||
            range.nivel_min.toString().includes(term) ||
            range.nivel_max.toString().includes(term)
        );
        setFilteredRanges(filtered);
    };

    return (
        <div className="level-ranges-manager">
            <h2>Level Range Management</h2>
            <form onSubmit={handleSubmit} className="range-form">
                <div className="input-group">
                    <input
                        type="text"
                        value={newRange.origen}
                        onChange={(e) => setNewRange({ ...newRange, origen: e.target.value })}
                        placeholder="Origin"
                    />
                    <input
                        type="text"
                        value={newRange.destino}
                        onChange={(e) => setNewRange({ ...newRange, destino: e.target.value })}
                        placeholder="Destination"
                    />
                    <input
                        type="number"
                        value={newRange.nivel_min}
                        onChange={(e) => setNewRange({ ...newRange, nivel_min: parseInt(e.target.value) })}
                        placeholder="Minimum Level"
                    />
                    <input
                        type="number"
                        value={newRange.nivel_max}
                        onChange={(e) => setNewRange({ ...newRange, nivel_max: parseInt(e.target.value) })}
                        placeholder="Maximum Level"
                    />
                    <input
                        type="text"
                        value={newRange.ruta}
                        onChange={(e) => setNewRange({ ...newRange, ruta: e.target.value })}
                        placeholder="Route"
                    />
                    <input
                        type="text"
                        value={newRange.zona}
                        onChange={(e) => setNewRange({ ...newRange, zona: e.target.value })}
                        placeholder="Zone"
                    />
                    <button type="submit" className="submit-button" disabled={isProcessing}>
                        {isProcessing ? 'Processing...' : (editingRange ? 'Update' : 'Save')}
                    </button>
                    {editingRange && (
                        <button type="button" className="cancel-button" onClick={cancelEditing}>
                            Cancel
                        </button>
                    )}
                </div>
            </form>

            <div className="search-container">
                <input
                    type="text"
                    placeholder="Buscar rangos..."
                    value={searchTerm}
                    onChange={handleSearch}
                    className="search-input"
                />
            </div>

            <div className="ranges-table">
                <table>
                    <thead>
                        <tr>
                            <th>Origen</th>
                            <th>Destino</th>
                            <th>Min Nivel</th>
                            <th>Max Nivel</th>
                            <th>Ruta</th>
                            <th>Zona</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {(searchTerm ? filteredRanges : ranges).map(range => (
                            <tr key={range.id}>
                                <td>{range.origen}</td>
                                <td>{range.destino}</td>
                                <td>{range.nivel_min}</td>
                                <td>{range.nivel_max}</td>
                                <td>{range.ruta}</td>
                                <td>{range.zona}</td>
                                <td>
                                    <button onClick={() => startEditing(range)} className="edit-button">
                                        Editar
                                    </button>
                                    <button onClick={() => handleDelete(range.id)} className="delete-button">
                                        Eliminar
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            {message && <div className="message">{message}</div>}
        </div>
    );
}

export default LevelRangesManager;