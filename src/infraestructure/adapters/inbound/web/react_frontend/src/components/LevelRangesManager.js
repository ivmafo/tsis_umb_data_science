import React, { useState, useEffect } from 'react';
import './LevelRangesManager.css';

function LevelRangesManager() {
    const [ranges, setRanges] = useState([]);
    const [newRange, setNewRange] = useState({ min_level: '', max_level: '', alias: '' });
    const [editingRange, setEditingRange] = useState(null);
    const [message, setMessage] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);

    useEffect(() => {
        fetchRanges();
    }, []);

    const fetchRanges = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/level-ranges');
            const data = await response.json();
            setRanges(data);
            setMessage('');
        } catch (error) {
            setMessage('Error al cargar rangos de nivel');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsProcessing(true);

        try {
            const url = editingRange 
                ? `http://localhost:8000/api/level-ranges/${editingRange.id}`
                : 'http://localhost:8000/api/level-ranges';
            
            const response = await fetch(url, {
                method: editingRange ? 'PUT' : 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(newRange),
            });

            const result = await response.json();
            
            if (response.ok) {
                setMessage(editingRange ? 'Rango actualizado' : 'Rango creado');
                setNewRange({ min_level: '', max_level: '', alias: '' });
                setEditingRange(null);
                fetchRanges();
            } else {
                setMessage(`Error: ${result.detail}`);
            }
        } catch (error) {
            setMessage('Error al procesar el rango');
        } finally {
            setIsProcessing(false);
        }
    };

    const startEditing = (range) => {
        setEditingRange(range);
        setNewRange({
            min_level: range.min_level,
            max_level: range.max_level,
            alias: range.alias
        });
    };

    const cancelEditing = () => {
        setEditingRange(null);
        setNewRange({ min_level: '', max_level: '', alias: '' });
    };

    const handleDelete = async (id) => {
        if (window.confirm('¿Estás seguro de que deseas eliminar este rango?')) {
            try {
                const response = await fetch(`http://localhost:8000/api/level-ranges/${id}`, {
                    method: 'DELETE',
                });
                if (response.ok) {
                    fetchRanges();
                    setMessage('Rango eliminado exitosamente');
                } else {
                    const error = await response.json();
                    setMessage(`Error: ${error.detail}`);
                }
            } catch (error) {
                setMessage('Error al eliminar el rango');
            }
        }
    };

    return (
        <div className="level-ranges-manager">
            <h2>Gestión de Rangos de Nivel</h2>
            <form onSubmit={handleSubmit} className="range-form">
                <div className="input-group">
                    <input
                        type="number"
                        value={newRange.min_level}
                        onChange={(e) => setNewRange({ ...newRange, min_level: parseInt(e.target.value) })}
                        placeholder="Nivel mínimo"
                        required
                    />
                    <input
                        type="number"
                        value={newRange.max_level}
                        onChange={(e) => setNewRange({ ...newRange, max_level: parseInt(e.target.value) })}
                        placeholder="Nivel máximo"
                        required
                    />
                    <input
                        type="text"
                        value={newRange.alias}
                        onChange={(e) => setNewRange({ ...newRange, alias: e.target.value })}
                        placeholder="Alias"
                        required
                    />
                    <button type="submit" className="submit-button" disabled={isProcessing}>
                        {isProcessing ? 'Procesando...' : (editingRange ? 'Actualizar' : 'Guardar')}
                    </button>
                    {editingRange && (
                        <button type="button" className="cancel-button" onClick={cancelEditing}>
                            Cancelar
                        </button>
                    )}
                </div>
            </form>

            <div className="ranges-table">
                <table>
                    <thead>
                        <tr>
                            <th>Nivel Mínimo</th>
                            <th>Nivel Máximo</th>
                            <th>Alias</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {ranges.map(range => (
                            <tr key={range.id}>
                                <td>{range.min_level}</td>
                                <td>{range.max_level}</td>
                                <td>{range.alias}</td>
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