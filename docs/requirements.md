# Requerimientos Funcionales y No Funcionales

Este documento detalla las especificaciones técnicas y operativas del sistema ATC Capacity & Analytics, categorizadas según el estándar de ingeniería de requisitos.

---

## 🎯 1. Requerimientos Funcionales (RF)

Los requerimientos funcionales definen los servicios que el sistema debe proporcionar y cómo debe reaccionar a entradas particulares.

### 📥 RF1: Gestión de Ingesta de Datos
- **RF1.1**: El sistema debe permitir la carga masiva de archivos en formato `.csv` y `.xlsx`.
- **RF1.2**: El sistema debe validar el esquema de datos (presencia de columnas como `origen`, `destino`, `fecha`) antes de persistir.
- **RF1.3**: El sistema debe permitir la recarga forzada de datos, eliminando duplicados mediante un identificador de archivo (`file_id`).
- **Archivo de Referencia**: [`ingest_flights_data.py`](file:///c:/Users/LENOVO/Documents/tesis/src/application/use_cases/ingest_flights_data.py)

### 🧮 RF2: Cálculo de Capacidad Técnica
- **RF2.1**: El sistema debe calcular el Tiempo de Permanencia en Sector (TPS) basándose en la historia de vuelos.
- **RF2.2**: El sistema debe aplicar la fórmula de la Circular 006 (UAEAC) para derivar la Capacidad Simultánea (SCV) y Horaria (CH).
- **RF2.3**: El sistema debe permitir el ajuste manual de parámetros técnicos (TFC y Factor R).
- **Archivo de Referencia**: [`calculate_sector_capacity.py`](file:///c:/Users/LENOVO/Documents/tesis/src/application/use_cases/calculate_sector_capacity.py)

### 🔮 RF3: Análisis Predictivo e IA
- **RF3.1**: El sistema debe generar predicciones de demanda diaria para un horizonte de 30 días.
- **RF3.2**: El sistema debe descomponer la demanda en componentes estacionales (Fourier) y residuales (Random Forest).
- **RF3.3**: El sistema debe alertar visualmente cuando la demanda proyectada supere la capacidad calculada (Saturación).
- **Archivo de Referencia**: [`predict_daily_demand.py`](file:///c:/Users/LENOVO/Documents/tesis/src/application/use_cases/predict_daily_demand.py)

### ⚙️ RF4: Administración de Maestros
- **RF4.1**: El sistema debe proporcionar un CRUD (Crear, Leer, Actualizar, Borrar) para Sectores Aeronáuticos.
- **RF4.2**: El sistema debe gestionar catálogos de Regiones (FIR) y Aeropuertos (ICAO).
- **Archivo de Referencia**: [`manage_sectors.py`](file:///c:/Users/LENOVO/Documents/tesis/src/application/use_cases/manage_sectors.py)

---

## 🛠️ 2. Requerimientos No Funcionales (RNF)

Los requerimientos no funcionales definen restricciones sobre los servicios o funciones ofrecidos por el sistema.

### 🚀 RNF1: Rendimiento y Escalabilidad
- **RNF1.1**: El sistema debe procesar datasets de tráfico aéreo de gran volumen utilizando ejecución paralela y SIMD vía **Polars**.
- **RNF1.2**: Las consultas analíticas sobre millones de registros deben resolverse en menos de 500ms utilizando **DuckDB**.
- **RNF1.3**: La interfaz de usuario debe ser una Single Page Application (SPA) reactiva para visualización de alta frecuencia.

### 🛡️ RNF2: Confiabilidad y Seguridad
- **RNF2.1**: El sistema debe garantizar la integridad de los datos mediante validaciones estrictas en la capa de Aplicación (Pydantic).
- **RNF2.2**: La base de datos DuckDB debe operar en modo `read_only` para múltiples procesos de consulta cuando no hay ingesta activa.

### 🧩 RNF3: Mantenibilidad y Arquitectura
- **RNF3.1**: El código debe seguir los principios de **Arquitectura Limpia (Clean Architecture)** para permitir el reemplazo de componentes de infraestructura sin afectar el dominio.
- **RNF3.2**: El sistema debe implementar **Inyección de Dependencias** para facilitar la automatización de pruebas unitarias y de integración.

### 🌐 RNF4: Usabilidad
- **RNF4.1**: La visualización de datos debe utilizar semántica visual consistente (colores de alerta para saturación) mediante ApexCharts.
- **RNF4.2**: El sistema debe ser compatible con navegadores modernos (Chrome, Edge, Firefox).

---

## 📊 Matriz de Trazabilidad Técnica

| Requerimiento | Módulo Backend | Componente Frontend |
| :--- | :--- | :--- |
| **Ingesta** | `IngestFlightsData` | `FilesView.tsx` |
| **Capacidad** | `CalculateSectorCapacity`| `CapacityReportView.tsx` |
| **Predicción**| `PredictDailyDemand` | `DailyDemandChart.tsx` |
| **Maestros** | `ManageSectors` | `SectorConfigurationView.tsx`|
