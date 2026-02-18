# Capa de Infraestructura (Infrastructure Layer)

La capa de infraestructura contiene las implementaciones técnicas de los puentes definidos en el dominio. Aquí es donde el sistema interactúa con el mundo exterior: bases de datos, sistemas de archivos, APIs de terceros y frameworks web.

## 🗄️ Persistencia y Repositorios

Utilizamos **DuckDB** como motor analítico principal debido a su eficiencia en el procesamiento de grandes volúmenes de datos en memoria.

### DuckDB Repository
[`duckdb_repository.py`](file:///c:/Users/LENOVO/Documents/tesis/src/infrastructure/adapters/duckdb_repository.py)
- **Función**: Traduce los objetos de dominio a esquemas relacionales y viceversa.
- **Ventaja**: Ejecuta consultas SQL complejas (JOINs, aggregaciones) con latencia mínima.

### Filesystem Repository
[`filesystem_repository.py`](file:///c:/Users/LENOVO/Documents/tesis/src/infrastructure/adapters/filesystem_repository.py)
- **Función**: Gestiona la lectura y escritura de archivos Excel/CSV para el proceso de ingesta.
- **Acceso**: Abstrae las rutas locales del sistema de archivos.

---

## 🚀 Adaptador de API (FastAPI)
El sistema expone sus capacidades a través de una API RESTful construida con **FastAPI**.

- **Ubicación**: `src/infrastructure/adapters/api/`
- **Controladores**:
    - `flights_controller.py`: Endpoints para gestión y consulta de vuelos.
    - `sectors_controller.py`: Configuración de parámetros de la Circular 006.
    - `predictions_controller.py`: Acceso a modelos de Machine Learning.

---

## ⚡ Procesamiento con Polars
Para operaciones de transformación de datos masivos (ETL), el sistema utiliza **Polars**.
- **Ventaja**: Procesamiento vectorial paralelo que supera significativamente el rendimiento de Pandas en conjuntos de datos aeronáuticos extensos.

---

## 🌐 3.6.7 Diagrama de Distribución (Deployment View)

El sistema está diseñado para ejecutarse localmente como una aplicación empaquetada o en un servidor de red interno.

```mermaid
graph TD
    subgraph "Client Tier (Browser)"
        UI["React Application (Static Assets)"]
    end

    subgraph "Application Tier (Python Engine)"
        API["FastAPI Server (Uvicorn)"]
        ML["ML Models Engine"]
    end

    subgraph "Data Tier (DuckDB)"
        DBFile[("tesis.db / metrics.duckdb")]
        SRS[("Directorio de Archivos SRS")]
    end

    UI -- HTTP/REST --> API
    API -- In-Memory Query --> DBFile
    API -- Python Calls --> ML
    API -- Read/Write --> SRS
```

---

## 📊 Diagrama de Infraestructura
... (Resto del contenido existente)

```mermaid
graph LR
    subgraph "Infrastructure Layer"
        FastAPI["FastAPI (Web Adapter)"]
        DuckDB["DuckDB (Database Adapter)"]
        Polars["Polars (ETL Adapter)"]
        FS["Filesystem (IO Adapter)"]
    end

    subgraph "External"
        HTML["Frontend Client"]
        Files["Archivos Excel/CSV"]
        DBFile["metrics.duckdb"]
    end

    HTML <--> FastAPI
    FastAPI <--> DuckDB
    Polars <--> Files
    Polars --> DuckDB
    FS <--> Files
```

> [!NOTE]
> Al estar en la capa más externa, estos archivos pueden depender de librerías de terceros (FastAPI, Polars, DuckDB) y del dominio, pero nunca de la capa de aplicación.
