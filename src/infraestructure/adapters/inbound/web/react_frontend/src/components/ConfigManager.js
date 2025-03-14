import React, { useState, useEffect } from 'react';
import './ConfigManager.css';

const GenerarSectores = () => {
  const [sector, setSector] = useState('');

  const handleGenerarSectores = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/generar-sectores', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sector }),
      });
      if (response.ok) {
        alert('Sectores generados exitosamente');
        setSector('');
      } else {
        const error = await response.json();
        alert(`Error: ${error.message}`);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error al generar sectores');
    }
  };

  return (
    <div className="generar-sectores-card">
      <h3>Generación de Sectores</h3>
      <div className="sector-input-group">
        <input
          type="text"
          value={sector}
          onChange={(e) => setSector(e.target.value)}
          placeholder="Ingrese el sector"
          className="sector-input"
        />
        <button onClick={handleGenerarSectores} className="generate-button">
          <i className="fas fa-cog"></i>
          Generar Sectores
        </button>
      </div>
    </div>
  );
};

const ConfigManager = () => {
  const [configs, setConfigs] = useState([]);
  const [newConfig, setNewConfig] = useState({ key: '', value: '' });
  const [editingConfig, setEditingConfig] = useState(null);
  const [message, setMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    fetchConfigs();
  }, []);

  const fetchConfigs = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/config');
      const data = await response.json();
      // Ordenar alfabéticamente por key
      const sortedData = data.sort((a, b) => a.key.localeCompare(b.key));
      setConfigs(sortedData);
      setMessage('');
    } catch (error) {
      setMessage('Error al cargar configuraciones');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsProcessing(true);

    try {
      const url = editingConfig 
        ? `http://localhost:8000/api/config/${editingConfig.key}`
        : 'http://localhost:8000/api/config';
      
      const response = await fetch(url, {
        method: editingConfig ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newConfig),
      });

      const result = await response.json();
      
      if (response.ok) {
        setMessage(editingConfig ? 'Configuración actualizada' : 'Configuración creada');
        setNewConfig({ key: '', value: '' });
        setEditingConfig(null);
        fetchConfigs();
        // Remove onUpdateSuccess call as it's not defined or needed
      } else {
        setMessage(`Error: ${result.detail}`);
      }
    } catch (error) {
      setMessage('Error al procesar la configuración');
    } finally {
      setIsProcessing(false);
    }
  };

  const startEditing = (config) => {
    setEditingConfig(config);
    setNewConfig({ key: config.key, value: config.value });
  };

  const cancelEditing = () => {
    setEditingConfig(null);
    setNewConfig({ key: '', value: '' });
  };

  const handleDelete = async (key) => {
    if (window.confirm('¿Estás seguro de que deseas eliminar este parámetro?')) {
      try {
        const response = await fetch(`http://localhost:8000/api/config/${key}`, {
          method: 'DELETE',
        });
        if (response.ok) {
          setConfigs(configs.filter(config => config.key !== key));
          alert('Parámetro eliminado exitosamente');
        } else {
          const error = await response.json();
          alert(`Error: ${error.message}`);
        }
      } catch (error) {
        console.error('Error:', error);
        alert('Error al eliminar el parámetro');
      }
    }
  };

  return (
    <div className="config-manager">
      <h2>Configuración General</h2>
      <GenerarSectores />
      <form onSubmit={handleSubmit} className="config-form">
        <div className="input-group">
          <input
            className="config-input"
            type="text"
            value={newConfig.key}
            onChange={(e) => setNewConfig({ ...newConfig, key: e.target.value })}
            placeholder="Nombre del parámetro"
            disabled={editingConfig}
            required
          />
          <input
            className="config-input"
            type="text"
            value={newConfig.value}
            onChange={(e) => setNewConfig({ ...newConfig, value: e.target.value })}
            placeholder="Valor"
            required
          />
          <button type="submit" className="submit-button" disabled={isProcessing}>
            <i className="fas fa-save"></i>
            {isProcessing ? 'Procesando...' : (editingConfig ? 'Actualizar' : 'Guardar')}
          </button>
          {editingConfig && (
            <button type="button" className="cancel-button" onClick={cancelEditing}>
              <i className="fas fa-times"></i>
              Cancelar
            </button>
          )}
        </div>
      </form>

      {message && <div className="message">{message}</div>}

      <div className="configs-table">
        <table>
          <thead>
            <tr>
              <th>Parámetro</th>
              <th>Valor</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {configs.map((config) => (
              <tr key={config.key}>
                <td>{config.key}</td>
                <td>{config.value}</td>
                <td className="action-buttons">
                  <button 
                    onClick={() => startEditing(config)}
                    className="edit-button">
                    <i className="fas fa-pen"></i>
                    Editar
                  </button>
                  <button 
                    onClick={() => handleDelete(config.key)}
                    className="delete-button">
                    <i className="fas fa-trash"></i>
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ConfigManager;