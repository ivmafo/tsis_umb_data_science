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
        NULL,
        NULL,
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
        NULL,
        NULL,
        NULL,
        NULL
    FROM fligths
    WHERE origen = 'SKRG'
    AND NOT EXISTS (
        SELECT 1 FROM Sectores s 
        WHERE s.origen = 'SKRG' 
        AND s.destino = fligths.destino
    );