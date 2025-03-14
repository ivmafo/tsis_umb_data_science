CREATE TABLE Sectores (
  id_sector SERIAL PRIMARY KEY,
  origen VARCHAR(50),
  destino VARCHAR(50),
  nivel_min INT,
  nivel_max INT,
  ruta VARCHAR(50),
  zona VARCHAR(50)
);

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



SELECT * FROM airports ; 




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