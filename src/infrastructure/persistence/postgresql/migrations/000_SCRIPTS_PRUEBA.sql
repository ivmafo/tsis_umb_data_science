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




-- Vista para análisis detallado de sectores
CREATE OR REPLACE VIEW sector_detailed_analysis AS
WITH flight_times AS (
    SELECT 
        origen AS sector,
        DATE_TRUNC('hour', fecha) AS hora,
        COUNT(*) AS num_vuelos,
        AVG(EXTRACT(EPOCH FROM (fecha_llegada - fecha_salida))) AS tps,
        COUNT(DISTINCT tipo_aeronave) AS tipos_aeronaves,
        COUNT(DISTINCT empresa) AS aerolineas,
        COUNT(DISTINCT tipo_vuelo) AS tipos_vuelo
    FROM public.fligths
    GROUP BY origen, DATE_TRUNC('hour', fecha)
)
SELECT 
    ft.*,
    -- Cálculos derivados
    CAST(cfg_msg.value AS INTEGER) * CAST(cfg_com.value AS INTEGER) * num_vuelos AS tiempo_total_comunicaciones,
    CAST(cfg_coord.value AS INTEGER) * num_vuelos AS tiempo_total_coordinacion,
    CAST(cfg_tareas.value AS INTEGER) AS tiempo_tareas_observables,
    CASE 
        WHEN tipos_aeronaves > 3 OR tipos_vuelo > 2 THEN CAST(cfg_comp_alta.value AS DECIMAL)
        WHEN tipos_aeronaves = 1 AND tipos_vuelo = 1 THEN CAST(cfg_comp_baja.value AS DECIMAL)
        ELSE CAST(cfg_comp_base.value AS DECIMAL)
    END AS factor_complejidad
FROM flight_times ft
CROSS JOIN public.config cfg_msg WHERE cfg_msg.key = 'tiempo_mensaje_promedio'
CROSS JOIN public.config cfg_com WHERE cfg_com.key = 'comunicaciones_promedio_aeronave'
CROSS JOIN public.config cfg_coord WHERE cfg_coord.key = 'tiempo_coordinacion_promedio'
CROSS JOIN public.config cfg_tareas WHERE cfg_tareas.key = 'tiempo_tareas_observables'
CROSS JOIN public.config cfg_comp_alta WHERE cfg_comp_alta.key = 'factor_complejidad_alta'
CROSS JOIN public.config cfg_comp_base WHERE cfg_comp_base.key = 'factor_complejidad_base'
CROSS JOIN public.config cfg_comp_baja WHERE cfg_comp_baja.key = 'factor_complejidad_baja';

-- Función para calcular capacidad detallada del sector
CREATE OR REPLACE FUNCTION calculate_detailed_sector_capacity(
    p_sector VARCHAR,
    p_hora TIMESTAMP
)
RETURNS TABLE (
    sector VARCHAR,
    hora TIMESTAMP,
    tps DECIMAL,              -- Tiempo Promedio en Sector
    tfc DECIMAL,              -- Tiempo Funciones Control
    tm DECIMAL,               -- Tiempo Comunicaciones
    tc DECIMAL,               -- Tiempo Coordinación
    tt DECIMAL,               -- Tiempo Tareas Observables
    factor_complejidad DECIMAL,
    scv DECIMAL,              -- Sector Capacity Value
    capacidad_horaria INTEGER,
    carga_trabajo_total DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    WITH sector_metrics AS (
        SELECT 
            sda.*,
            sda.tiempo_total_comunicaciones AS tm,
            sda.tiempo_total_coordinacion AS tc,
            sda.tiempo_tareas_observables AS tt,
            (sda.tiempo_total_comunicaciones + 
             sda.tiempo_total_coordinacion + 
             sda.tiempo_tareas_observables) AS tfc
        FROM sector_detailed_analysis sda
        WHERE sda.sector = p_sector
        AND sda.hora = p_hora
    )
    SELECT 
        sm.sector,
        sm.hora,
        ROUND(sm.tps::DECIMAL, 2),
        ROUND(sm.tfc::DECIMAL, 2),
        ROUND(sm.tm::DECIMAL, 2),
        ROUND(sm.tc::DECIMAL, 2),
        ROUND(sm.tt::DECIMAL, 2),
        sm.factor_complejidad,
        ROUND((sm.tfc * 1.3 / NULLIF(sm.tps, 0))::DECIMAL, 2) as scv,
        ROUND(((3600 / NULLIF(sm.tps, 0)) * (sm.tfc * 1.3 / NULLIF(sm.tps, 0)))::DECIMAL, 0)::INTEGER as capacidad_horaria,
        ROUND((sm.tfc * sm.factor_complejidad)::DECIMAL, 2) as carga_trabajo_total
    FROM sector_metrics sm;
END;
$$ LANGUAGE plpgsql;


























CREATE OR REPLACE VIEW sector_detailed_analysis AS
WITH flight_times AS (
    SELECT 
        origen AS sector,
        DATE_TRUNC('hour', fecha) AS hora,
        COUNT(*) AS num_vuelos,
        AVG(EXTRACT(EPOCH FROM (fecha_llegada - fecha_salida))) AS tps,
        COUNT(DISTINCT tipo_aeronave) AS tipos_aeronaves,
        COUNT(DISTINCT empresa) AS aerolineas,
        COUNT(DISTINCT tipo_vuelo) AS tipos_vuelo
    FROM public.fligths
    GROUP BY origen, DATE_TRUNC('hour', fecha)
)
SELECT 
    ft.*,
    -- Cálculos derivados
    CAST(cfg_msg.value AS INTEGER) * CAST(cfg_com.value AS INTEGER) * num_vuelos AS tiempo_total_comunicaciones,
    CAST(cfg_coord.value AS INTEGER) * num_vuelos AS tiempo_total_coordinacion,
    CAST(cfg_tareas.value AS INTEGER) AS tiempo_tareas_observables,
    CASE 
        WHEN tipos_aeronaves > 3 OR tipos_vuelo > 2 THEN CAST(cfg_comp_alta.value AS DECIMAL)
        WHEN tipos_aeronaves = 1 AND tipos_vuelo = 1 THEN CAST(cfg_comp_baja.value AS DECIMAL)
        ELSE CAST(cfg_comp_base.value AS DECIMAL)
    END AS factor_complejidad
FROM flight_times ft
CROSS JOIN public.config cfg_msg ON cfg_msg.key = 'tiempo_mensaje_promedio'
CROSS JOIN public.config cfg_com ON cfg_com.key = 'comunicaciones_promedio_aeronave'
CROSS JOIN public.config cfg_coord ON cfg_coord.key = 'tiempo_coordinacion_promedio'
CROSS JOIN public.config cfg_tareas ON cfg_tareas.key = 'tiempo_tareas_observables'
CROSS JOIN public.config cfg_comp_alta ON cfg_comp_alta.key = 'factor_complejidad_alta'
CROSS JOIN public.config cfg_comp_base ON cfg_comp_base.key = 'factor_complejidad_base'
CROSS JOIN public.config cfg_comp_baja ON cfg_comp_baja.key = 'factor_complejidad_baja';









-- Vista para análisis detallado de sectores
CREATE OR REPLACE VIEW sector_detailed_analysis AS
WITH flight_times AS (
    SELECT 
        origen AS sector,
        DATE_TRUNC('hour', fecha) AS hora,
        COUNT(*) AS num_vuelos,
        AVG(EXTRACT(EPOCH FROM (fecha_llegada - fecha_salida))) AS tps,
        COUNT(DISTINCT tipo_aeronave) AS tipos_aeronaves,
        COUNT(DISTINCT empresa) AS aerolineas,
        COUNT(DISTINCT tipo_vuelo) AS tipos_vuelo
    FROM public.fligths
    GROUP BY origen, DATE_TRUNC('hour', fecha)
)
SELECT 
    ft.*,
    -- Cálculos derivados
    CAST(cfg_msg.value AS INTEGER) * CAST(cfg_com.value AS INTEGER) * num_vuelos AS tiempo_total_comunicaciones,
    CAST(cfg_coord.value AS INTEGER) * num_vuelos AS tiempo_total_coordinacion,
    CAST(cfg_tareas.value AS INTEGER) AS tiempo_tareas_observables,
    CASE 
        WHEN tipos_aeronaves > 3 OR tipos_vuelo > 2 THEN CAST(cfg_comp_alta.value AS DECIMAL)
        WHEN tipos_aeronaves = 1 AND tipos_vuelo = 1 THEN CAST(cfg_comp_baja.value AS DECIMAL)
        ELSE CAST(cfg_comp_base.value AS DECIMAL)
    END AS factor_complejidad
FROM flight_times ft
CROSS JOIN public.config cfg_msg ON cfg_msg.key = 'tiempo_mensaje_promedio'
CROSS JOIN public.config cfg_com ON cfg_com.key = 'comunicaciones_promedio_aeronave'
CROSS JOIN public.config cfg_coord ON cfg_coord.key = 'tiempo_coordinacion_promedio'
CROSS JOIN public.config cfg_tareas ON cfg_tareas.key = 'tiempo_tareas_observables'
CROSS JOIN public.config cfg_comp_alta ON cfg_comp_alta.key = 'factor_complejidad_alta'
CROSS JOIN public.config cfg_comp_base ON cfg_comp_base.key = 'factor_complejidad_base'
CROSS JOIN public.config cfg_comp_baja ON cfg_comp_baja.key = 'factor_complejidad_baja';










CREATE OR REPLACE VIEW sector_detailed_analysis AS
WITH flight_times AS (
    SELECT 
        origen AS sector,
        DATE_TRUNC('hour', fecha) AS hora,
        COUNT(*) AS num_vuelos,
        AVG(EXTRACT(EPOCH FROM (fecha_llegada - fecha_salida))) AS tps,
        COUNT(DISTINCT tipo_aeronave) AS tipos_aeronaves,
        COUNT(DISTINCT empresa) AS aerolineas,
        COUNT(DISTINCT tipo_vuelo) AS tipos_vuelo
    FROM public.fligths
    GROUP BY origen, DATE_TRUNC('hour', fecha)
)
SELECT 
    ft.*,
    -- Cálculos derivados
    CAST(cfg_msg.value AS INTEGER) * CAST(cfg_com.value AS INTEGER) * num_vuelos AS tiempo_total_comunicaciones,
    CAST(cfg_coord.value AS INTEGER) * num_vuelos AS tiempo_total_coordinacion,
    CAST(cfg_tareas.value AS INTEGER) AS tiempo_tareas_observables,
    CASE 
        WHEN tipos_aeronaves > 3 OR tipos_vuelo > 2 THEN CAST(cfg_comp_alta.value AS DECIMAL)
        WHEN tipos_aeronaves = 1 AND tipos_vuelo = 1 THEN CAST(cfg_comp_baja.value AS DECIMAL)
        ELSE CAST(cfg_comp_base.value AS DECIMAL)
    END AS factor_complejidad
FROM flight_times ft
JOIN public.config cfg_msg ON cfg_msg.key = 'tiempo_mensaje_promedio'
JOIN public.config cfg_com ON cfg_com.key = 'comunicaciones_promedio_aeronave'
JOIN public.config cfg_coord ON cfg_coord.key = 'tiempo_coordinacion_promedio'
JOIN public.config cfg_tareas ON cfg_tareas.key = 'tiempo_tareas_observables'
JOIN public.config cfg_comp_alta ON cfg_comp_alta.key = 'factor_complejidad_alta'
JOIN public.config cfg_comp_base ON cfg_comp_base.key = 'factor_complejidad_base'
JOIN public.config cfg_comp_baja ON cfg_comp_baja.key = 'factor_complejidad_baja';

















-- Vista para análisis detallado de sectores
CREATE OR REPLACE VIEW sector_detailed_analysis AS
WITH flight_times AS (
    SELECT 
        origen AS sector,
        DATE_TRUNC('hour', fecha) AS hora,
        COUNT(*) AS num_vuelos,
        AVG(EXTRACT(EPOCH FROM (fecha_llegada - fecha_salida)::interval)) AS tps,
        COUNT(DISTINCT tipo_aeronave) AS tipos_aeronaves,
        COUNT(DISTINCT empresa) AS aerolineas,
        COUNT(DISTINCT tipo_vuelo) AS tipos_vuelo
    FROM public.fligths
    GROUP BY origen, DATE_TRUNC('hour', fecha)
)
SELECT 
    ft.*,
    -- Cálculos derivados
    CAST(cfg_msg.value AS INTEGER) * CAST(cfg_com.value AS INTEGER) * num_vuelos AS tiempo_total_comunicaciones,
    CAST(cfg_coord.value AS INTEGER) * num_vuelos AS tiempo_total_coordinacion,
    CAST(cfg_tareas.value AS INTEGER) AS tiempo_tareas_observables,
    CASE 
        WHEN tipos_aeronaves > 3 OR tipos_vuelo > 2 THEN CAST(cfg_comp_alta.value AS DECIMAL)
        WHEN tipos_aeronaves = 1 AND tipos_vuelo = 1 THEN CAST(cfg_comp_baja.value AS DECIMAL)
        ELSE CAST(cfg_comp_base.value AS DECIMAL)
    END AS factor_complejidad
FROM flight_times ft
JOIN public.config cfg_msg ON cfg_msg.key = 'tiempo_mensaje_promedio'
JOIN public.config cfg_com ON cfg_com.key = 'comunicaciones_promedio_aeronave'
JOIN public.config cfg_coord ON cfg_coord.key = 'tiempo_coordinacion_promedio'
JOIN public.config cfg_tareas ON cfg_tareas.key = 'tiempo_tareas_observables'
JOIN public.config cfg_comp_alta ON cfg_comp_alta.key = 'factor_complejidad_alta'
JOIN public.config cfg_comp_base ON cfg_comp_base.key = 'factor_complejidad_base'
JOIN public.config cfg_comp_baja ON cfg_comp_baja.key = 'factor_complejidad_baja';





































select * from fligths ; 


WITH flight_times AS (
    SELECT 
        fligths.origen AS sector,
        date_trunc('hour', fligths.fecha) AS hora,
        count(*) AS num_vuelos,
        count(DISTINCT fligths.tipo_aeronave) AS tipos_aeronaves,
        count(DISTINCT fligths.empresa) AS aerolineas,
        count(DISTINCT fligths.tipo_vuelo) AS tipos_vuelo
    FROM fligths
    GROUP BY fligths.origen, date_trunc('hour', fligths.fecha)
)
SELECT 
    ft.sector,
    ft.hora,
    ft.num_vuelos,
    ft.tipos_aeronaves,
    ft.aerolineas,
    ft.tipos_vuelo,
    -- Tiempo de comunicaciones (Tm) = tiempo promedio mensaje * comunicaciones promedio * número de vuelos
    (cfg_msg.value::integer * cfg_com.value::integer * ft.num_vuelos) AS tiempo_total_comunicaciones,
    -- Tiempo de coordinación (Tc) = tiempo coordinación promedio * número de vuelos
    (cfg_coord.value::integer * ft.num_vuelos) AS tiempo_total_coordinacion,
    -- Tiempo de tareas observables (Tt) = valor constante
    cfg_tareas.value::integer AS tiempo_tareas_observables,
    -- Factor de complejidad basado en tipos de aeronaves y vuelos
    CASE 
        WHEN ft.tipos_aeronaves > 3 OR ft.tipos_vuelo > 2 THEN cfg_comp_alta.value::numeric
        WHEN ft.tipos_aeronaves = 1 AND ft.tipos_vuelo = 1 THEN cfg_comp_baja.value::numeric
        ELSE cfg_comp_base.value::numeric
    END AS factor_complejidad,
    -- Carga de trabajo total = (Tm + Tc + Tt) * Factor de complejidad
    (
        (cfg_msg.value::integer * cfg_com.value::integer * ft.num_vuelos) + 
        (cfg_coord.value::integer * ft.num_vuelos) + 
        cfg_tareas.value::integer
    ) * 
    CASE 
        WHEN ft.tipos_aeronaves > 3 OR ft.tipos_vuelo > 2 THEN cfg_comp_alta.value::numeric
        WHEN ft.tipos_aeronaves = 1 AND ft.tipos_vuelo = 1 THEN cfg_comp_baja.value::numeric
        ELSE cfg_comp_base.value::numeric
    END AS carga_trabajo_total
FROM flight_times ft
JOIN config cfg_msg ON cfg_msg.key = 'tiempo_mensaje_promedio'
JOIN config cfg_com ON cfg_com.key = 'comunicaciones_promedio_aeronave'
JOIN config cfg_coord ON cfg_coord.key = 'tiempo_coordinacion_promedio'
JOIN config cfg_tareas ON cfg_tareas.key = 'tiempo_tareas_observables'
JOIN config cfg_comp_alta ON cfg_comp_alta.key = 'factor_complejidad_alta'
JOIN config cfg_comp_base ON cfg_comp_base.key = 'factor_complejidad_base'
JOIN config cfg_comp_baja ON cfg_comp_baja.key = 'factor_complejidad_baja';
































select min(nivel) , max(nivel) from fligths ; 

WITH OrigenDestino AS (
  SELECT DISTINCT origen, destino
  FROM fligths
  WHERE origen = 'SKBO' OR destino = 'SKBO'
),
NivelesAleatorios AS (
  SELECT 
    origen,
    destino,
    FLOOR(RANDOM() * 25000) AS nivel_min,
    FLOOR(RANDOM() * 25000 + 25001) AS nivel_max,
    'Sector_' || origen || '_' || destino AS nombre_sector
  FROM OrigenDestino
)
--INSERT INTO Sectores (origen, destino, nivel_min, nivel_max, nombre_sector)
SELECT origen, destino, nivel_min, nivel_max, nombre_sector
FROM NivelesAleatorios
WHERE nivel_min < nivel_max
ORDER BY nivel_min, nombre_sector;







drop table sectores ; 

CREATE TABLE Sectores (
  id_sector SERIAL PRIMARY KEY,
  origen VARCHAR(50),
  destino VARCHAR(50),
  nivel_min INT,
  nivel_max INT,
  ruta VARCHAR(50),
  zona VARCHAR(50)
);


truncate  Sectores ; 



WITH OrigenDestino AS (
  SELECT DISTINCT origen, destino
  FROM fligths
  WHERE origen = 'SKBO' OR destino = 'SKBO'
),
Niveles AS (
  SELECT 
    origen,
    destino,
    nivel_min,
    nivel_max,
    CASE 
      WHEN nivel_min BETWEEN 1 AND 18750 THEN 'Nororiente'
      WHEN nivel_min BETWEEN 18751 AND 37500 THEN 'Noroccidente'
      WHEN nivel_min BETWEEN 37501 AND 56250 THEN 'Suroriente'
      WHEN nivel_min BETWEEN 56251 AND 75000 THEN 'Suroccidente'
    END AS zona
  FROM (
    SELECT 
      origen,
      destino,
      GENERATE_SERIES(1, 75000, 18750) AS nivel_min,
      GENERATE_SERIES(18750, 75000, 18750) AS nivel_max
    FROM OrigenDestino
  ) AS niveles
)
INSERT INTO Sectores (origen, destino, nivel_min, nivel_max, nombre_sector, zona)
SELECT 
  origen, 
  destino, 
  nivel_min, 
  nivel_max, 
  'Sector_' || origen || '_' || destino || '_' || zona AS nombre_sector, 
  zona
FROM Niveles
WHERE nivel_min < nivel_max;






select count(1) , zona from sectores group by zona  ; 




select * from sectores where zona = 'Nororiente'





-- Insertar registros donde SKRG es destino
INSERT INTO Sectores (origen, destino, nivel_min, nivel_max, ruta, zona)
SELECT DISTINCT
    origen,
    'SKRG',
    0,
    0,
    NULL,
    NULL
FROM fligths
WHERE destino = 'SKRG'
AND NOT EXISTS (
    SELECT 1 FROM Sectores s 
    WHERE s.origen = fligths.origen 
    AND s.destino = 'SKRG'
);

-- Insertar registros donde SKRG es origen
INSERT INTO Sectores (origen, destino, nivel_min, nivel_max, ruta, zona)
SELECT DISTINCT
    'SKRG',
    destino,
    0,
    0,
    NULL,
    NULL
FROM fligths
WHERE origen = 'SKRG'
AND NOT EXISTS (
    SELECT 1 FROM Sectores s 
    WHERE s.origen = 'SKRG' 
    AND s.destino = fligths.destino
);






















WITH niveles AS (
    SELECT 
        nivel_min,
        nivel_max
    FROM (
        SELECT 
            GENERATE_SERIES(1, 75000, 15000) AS nivel_min,
            GENERATE_SERIES(15000, 75000, 15000) AS nivel_max
    ) n
    WHERE nivel_min < nivel_max
)
UPDATE Sectores
SET 
    nivel_min = (SELECT nivel_min FROM niveles ORDER BY random() LIMIT 1),
    nivel_max = (SELECT nivel_max FROM niveles ORDER BY random() LIMIT 1)
WHERE nivel_min = 0 AND nivel_max = 0;

-- Asegurar que nivel_min siempre sea menor que nivel_max
UPDATE Sectores
SET 
    nivel_min = LEAST(nivel_min, nivel_max),
    nivel_max = GREATEST(nivel_min, nivel_max)
WHERE nivel_min > nivel_max;    


-- select * from sectores WHERE Ruta = 'RUTASKRGSKBO' ; 
SELECT * FROM SECTORES WHERE ZONA IS NULL ; 



select COUNT(1) , ZONA FROM sectores GROUP BY ZONA ; 

SELECT COUNT(1), RUTA FROM SECTORES GROUP BY RUTA ;

update sectores set nivel_min = 0 ;

UPDATE Sectores
SET nivel_min = (
    SELECT nivel * 15000
    FROM (
        SELECT FLOOR(random() * 5)  AS nivel
    ) AS random_level
    WHERE Sectores.id_sector = Sectores.id_sector
)
WHERE nivel_min = 0;



UPDATE Sectores
SET nivel_max = nivel_min +15000 ; 




UPDATE Sectores
SET ruta = CASE 
    WHEN origen = 'SKRG' THEN 'RUTASKRG' || destino
    WHEN destino = 'SKRG' THEN 'RUTASKRG' || origen
END
WHERE origen = 'SKRG' OR destino = 'SKRG';





select * from airports where icao_code = 'SKBO' ; 





   SELECT *
    FROM airports
    WHERE icao_code = 'SKMA'

SELECT * FROM SECTORES WHERE ZONA IS NULL ORDER BY RUTA ; 




WITH skrg_coords AS (
    SELECT latitude as ref_lat, longitude as ref_long
    FROM airports
    WHERE icao_code = 'SKRG'
),
airport_directions AS (
    SELECT 
        a.icao_code,
        a.name,
        a.latitude,
        a.longitude,
        CASE
            WHEN a.latitude > skrg_coords.ref_lat AND a.longitude > skrg_coords.ref_long THEN 'NORORIENTE'
            WHEN a.latitude > skrg_coords.ref_lat AND a.longitude < skrg_coords.ref_long THEN 'NOROCCIDENTE'
            WHEN a.latitude < skrg_coords.ref_lat AND a.longitude > skrg_coords.ref_long THEN 'SURORIENTE'
            WHEN a.latitude < skrg_coords.ref_lat AND a.longitude < skrg_coords.ref_long THEN 'SUROCCIDENTE'
        END as direccion
    FROM airports a
    CROSS JOIN skrg_coords
    WHERE a.icao_code != 'SKRG'
)
UPDATE Sectores s
SET zona = ad.direccion
FROM airport_directions ad
WHERE 
    (CASE 
        WHEN s.origen = 'SKRG' THEN s.destino
        WHEN s.destino = 'SKRG' THEN s.origen
    END) = ad.icao_code
AND (s.origen = 'SKRG' OR s.destino = 'SKRG');

-- Actualizar la ruta con la nueva clasificación
UPDATE Sectores
SET ruta = zona || 
    CASE 
        WHEN origen = 'SKRG' THEN destino
        WHEN destino = 'SKRG' THEN origen
    END
WHERE origen = 'SKRG' OR destino = 'SKRG';






