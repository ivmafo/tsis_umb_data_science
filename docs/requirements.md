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

### 🧮 RF2: Cálculo de Capacidad Dinámica (RAC 14)
- **RF2.1**: El sistema debe emplear simulación Montecarlo para inferir la Capacidad Estocástica RAC 14 con un 95% de confianza.
- **RF2.2**: El sistema debe inferir tiempos operacionales reales mediante Agentes Inteligentes (`Physicist`, `ComplianceOfficer`).
- **RF2.3**: El sistema debe mantener el cálculo legado de la Circular 006 (UAEAC) para auditoría.
- **Archivo de Referencia**: [`backend_agent.py`](file:///c:/Users/LENOVO/Documents/tesis/src/application/use_cases/backend_agent.py)

### 🔮 RF3: Análisis Predictivo e IA
- **RF3.1**: El sistema debe generar predicciones de demanda diaria para un horizonte de 30 días.
- **RF3.2**: El sistema debe descomponer la demanda en componentes estacionales (Variables Dummy de Calendario de Colombia) y residuales (Random Forest).
- **RF3.3**: El sistema debe alertar visualmente cuando la demanda proyectada supere la capacidad calculada (Saturación).
- **Archivo de Referencia**: [`predict_daily_demand.py`](file:///c:/Users/LENOVO/Documents/tesis/src/application/use_cases/predict_daily_demand.py)

### ⚙️ RF4: Administración de Maestros
- **RF4.1**: El sistema debe proporcionar un CRUD (Crear, Leer, Actualizar, Borrar) para Sectores Aeronáuticos.
- **RF4.2**: El sistema debe gestionar catálogos de Regiones (FIR) y Aeropuertos (ICAO) con sus respectivas relaciones Muchos-A-Muchos.
- **RF4.3**: El sistema debe listar el historial de cargas de archivos procesados y fallidos.
- **Archivo de Referencia**: [`manage_sectors.py`](file:///c:/Users/LENOVO/Documents/tesis/src/application/use_cases/manage_sectors.py), [`manage_airports.py`](file:///c:/Users/LENOVO/Documents/tesis/src/application/use_cases/manage_airports.py)

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
| **Ingesta** | `IngestFlightsData` | `FilesView.tsx`, `UploadView.tsx` |
| **Capacidad** | `BackendAgent`| `CapacityReportView.tsx` |
| **Predicción**| `PredictDailyDemand` | `DailyDemandChart.tsx` |
| **Crecimiento**| `PredictAirlineGrowth` | `FlightDistributionView.tsx` |
| **Maestros** | `ManageSectors`, `ManageAirports`| `SectorConfigurationView.tsx`, `AirportsView.tsx`|
| **Resultados**| `Generate*Report` | Exportación PDF / Excel desde la UI |
