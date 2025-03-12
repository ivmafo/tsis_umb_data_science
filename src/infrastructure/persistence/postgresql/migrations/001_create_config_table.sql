-- Crear tabla de configuración
CREATE TABLE IF NOT EXISTS config (
    key VARCHAR(50) PRIMARY KEY,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Función para actualizar el timestamp
CREATE OR REPLACE FUNCTION update_config_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para actualizar automáticamente updated_at
CREATE TRIGGER update_config_modtime
    BEFORE UPDATE ON config
    FOR EACH ROW
    EXECUTE FUNCTION update_config_timestamp();

-- Insertar configuración inicial para SCV y nuevos parámetros
INSERT INTO config (key, value) VALUES 
    ('factor_planeacion_scv', '1.3'),
    ('ventana_tiempo_scv', '60'),
    -- Parámetros de tiempo
    ('tiempo_mensaje_promedio', '15'),           -- Segundos por mensaje
    ('tiempo_planificacion_base', '180'),        -- Segundos por hora
    ('tiempo_deteccion_conflictos', '120'),      -- Segundos por hora
    ('factor_disponibilidad_controlador', '0.7'), -- 70% disponibilidad
    -- Factores de complejidad
    ('factor_complejidad_base', '1.0'),
    ('factor_complejidad_alta', '1.3'),
    ('factor_complejidad_baja', '0.8'),
    -- Parámetros de comunicación
    ('comunicaciones_promedio_aeronave', '8'),    -- Mensajes por aeronave
    ('tiempo_coordinacion_promedio', '30'),       -- Segundos por coordinación
    ('tiempo_tareas_observables', '300')          -- Segundos por hora
ON CONFLICT (key) DO NOTHING;