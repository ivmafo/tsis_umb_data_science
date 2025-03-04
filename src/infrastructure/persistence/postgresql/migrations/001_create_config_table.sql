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

-- Insertar configuración inicial para SCV
INSERT INTO config (key, value) VALUES 
    ('factor_planeacion_scv', '1.3'),
    ('ventana_tiempo_scv', '60')
ON CONFLICT (key) DO NOTHING;