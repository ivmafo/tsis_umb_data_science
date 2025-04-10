import React, { useState } from 'react';
import { FaEdit, FaTrash, FaPlane } from 'react-icons/fa';
import './Regions.css';

function RegionsList({ regions, onEdit, onDelete, isLoading }) {
    const [expandedRegion, setExpandedRegion] = useState(null);

    if (isLoading) {
        return <div className="loading">Cargando regiones...</div>;
    }

    return (
        <div className="regions-list">
            <table>
                <thead>
                    <tr>
                        <th>Nombre</th>
                        <th>Código</th>
                        <th>Descripción</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {regions.map(region => (
                        <React.Fragment key={region.id}>
                            <tr>
                                <td>{region.name}</td>
                                <td>{region.code}</td>
                                <td>{region.description || '-'}</td>
                                <td>
                                    <button 
                                        className="btn-icon"
                                        onClick={() => onEdit(region)}
                                        title="Editar"
                                    >
                                        <FaEdit />
                                    </button>
                                    <button 
                                        className="btn-icon"
                                        onClick={() => onDelete(region.id)}
                                        title="Eliminar"
                                    >
                                        <FaTrash />
                                    </button>
                                </td>
                            </tr>
                        </React.Fragment>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default RegionsList;