import React, { useState, useEffect } from 'react';
import './Regions.css';

function RegionForm({ region, onSubmit, onCancel }) {
    const [formData, setFormData] = useState({
        name: '',
        code: '',
        description: ''
    });
    const [formErrors, setFormErrors] = useState({});

    useEffect(() => {
        if (region) {
            setFormData({
                name: region.name || '',
                code: region.code || '',
                description: region.description || ''
            });
        }
    }, [region]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        
        // Clear error for this field
        if (formErrors[name]) {
            setFormErrors(prev => ({
                ...prev,
                [name]: null
            }));
        }
    };

    const validateForm = () => {
        const errors = {};
        
        if (!formData.name.trim()) {
            errors.name = 'El nombre es requerido';
        }
        
        if (!formData.code.trim()) {
            errors.code = 'El código es requerido';
        } else if (formData.code.length > 10) {
            errors.code = 'El código no puede tener más de 10 caracteres';
        }
        
        setFormErrors(errors);
        return Object.keys(errors).length === 0;
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }
        
        onSubmit(formData);
    };

    return (
        <div className="region-form">
            <h3>{region ? 'Editar Región' : 'Crear Nueva Región'}</h3>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="name">Nombre:</label>
                    <input
                        type="text"
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        className={formErrors.name ? 'error' : ''}
                    />
                    {formErrors.name && <span className="error-message">{formErrors.name}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="code">Código:</label>
                    <input
                        type="text"
                        id="code"
                        name="code"
                        value={formData.code}
                        onChange={handleChange}
                        className={formErrors.code ? 'error' : ''}
                    />
                    {formErrors.code && <span className="error-message">{formErrors.code}</span>}
                </div>

                <div className="form-group">
                    <label htmlFor="description">Descripción:</label>
                    <textarea
                        id="description"
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        rows="4"
                    />
                </div>

                <div className="form-actions">
                    <button type="submit" className="btn-primary">
                        {region ? 'Actualizar' : 'Crear'}
                    </button>
                    <button type="button" className="btn-secondary" onClick={onCancel}>
                        Cancelar
                    </button>
                </div>
            </form>
        </div>
    );
}

export default RegionForm;