# Referencia Técnica Detallada

Esta sección contiene la documentación detallada de cada clase y método del sistema, extraída prospectivamente de los docstrings del código.

## 🏛️ Gestión de Sectores (ManageSectors)

::: src.application.use_cases.manage_sectors
    options:
      members:
        - get_all
        - get_by_id
        - create
        - update
        - delete

## 📉 Modelos Predictivos (Machine Learning)

### Predicción de Demanda Diaria
::: src.application.use_cases.predict_daily_demand
    options:
      members:
        - execute
        - execute_seasonal

### Análisis de Picos y Congestión
::: src.application.use_cases.predict_peak_hours
    options:
      members:
        - execute

### Evolución de Aerolíneas
::: src.application.use_cases.predict_airline_growth
    options:
      members:
        - execute

### Tendencia Estacional (Fourier)
::: src.application.use_cases.predict_seasonal_trend
    options:
      members:
        - execute

## 🧮 Cálculos Técnicos (ATC)

::: src.application.use_cases.calculate_sector_capacity
    options:
      members:
        - execute

## 📥 Ingesta y Procesamiento (ETL)

::: src.application.use_cases.ingest_flights_data
    options:
      members:
        - execute

---

## 🖥️ Arquitectura Frontend

Esta sección detalla los componentes principales de la interfaz de usuario y su funcionamiento interno.

### Vistas Principales (Views)
Documentación de las vistas que orquestan el estado de la UI:
- **FlightDistributionView**: Dashboard de análisis espacial y temporal.
- **PredictiveView**: Centro de control de modelos de ML.
- **CapacityReportView**: Interfaz de cálculo normativo (Circular 006).

### Componentes de Visualización
- **SectorSaturationChart**: Gráfico de líneas con detección de umbrales críticos.
- **PeakHoursHeatmap**: Mapa de calor 24/7 de intensidad operativa.
- **RegionsTreemap**: Navegador dimensional de flujos de tráfico.
