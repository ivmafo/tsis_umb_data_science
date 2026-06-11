# 📙 Manual de Usuario Maestro: ATC Capacity & Analytics

Este manual proporciona una guía detallada sobre la operación del sistema, fundamentando cada acción del usuario en los principios técnicos y matemáticos que rigen el control de tráfico aéreo moderno.

---

## 🚀 1. Ciclo de Vida Operativo del Sistema

El sistema transforma datos brutos de vuelos en inteligencia operativa mediante un flujo dividido en tres etapas críticas:

```mermaid
graph LR
    A[Carga de Datos] --> B[Configuración de Sectores]
    B --> C[Análisis y Cálculo]
    C --> D[Predicción y Reporte]
```
### 🔍 Análisis Detallado: Cadena de Valor
- **Paso A**: El usuario alimenta el sistema (`UploadView`). Sin datos, no hay cálculo.
- **Paso B**: El usuario define la "física" del sector (polígonos, TFC) en `SectorConfigurationView`.
- **Paso C**: El sistema cruza A + B para generar métricas (`CalculateSectorCapacity`).
- **Paso D**: IA proyecta estas métricas al futuro.

---

## 📥 2. Ingesta de Datos (Data Ingestion)

El motor de ingesta es el primer punto de contacto. Técnica y matemáticamente, su función es la **normalización y limpieza de series temporales**.

### 📝 Procedimiento de Carga:
1.  **Acceso**: Diríjase a la sección de **Repositorio de Archivos**.
2.  **Carga masiva**: Arrastre archivos `.csv` o `.xlsx`. Internamente, el sistema activa el adaptador [`PolarsDataSource`](file:///c:/Users/LENOVO/Documents/tesis/src/infrastructure/adapters/polars/polars_data_source.py).
3.  **Validación Técnica**: El sistema verifica que el archivo contenga las columnas obligatorias (`origen`, `destino`, `fecha`, `duracion`).

**¿Qué ocurre detrás de escena?**
Al subir un archivo, se dispara el caso de uso `IngestFlightsData`, que utiliza **Evaluación Perezosa (Lazy Evaluation)** para procesar cientos de miles de filas sin saturar la memoria del servidor.

---

## 📑 3. Cálculo de Capacidad Dinámica (RAC 14 Estocástico)

A diferencia de sistemas tradicionales basados en capacidades estáticas, este módulo utiliza un ensamble de **Agentes Inteligentes** para calcular la Capacidad Estocástica RAC 14 mediante simulaciones de Montecarlo.

### 📐 Fundamentación de los Parámetros UI:
Al realizar un cálculo, usted interactúa con variables que moldean el comportamiento físico de la simulación:

1.  **TFC Dinámico (Tiempo de Funciones de Control)**: 
    - Calculado vectorialmente por el agente `Physicist`, quien evalúa la proximidad y las trayectorias de los vuelos históricos, y extrae el cuello de botella (TMA vs Pista).
2.  **Rango de Incertidumbre (Montecarlo)**:
    - El Agente `RiskManager` ejecuta miles de simulaciones para entregar un rango estadístico (ej: 40 a 45 vuelos por hora) con 95% de confianza, en vez de un solo número frágil.
3.  **Factor de Utilización (Ashford)**:
    - **Slider en Vista**: Permite inyectar estrés o pasividad en el cálculo estocástico (ej: 0.8 reduce el límite simulado). El agente `ComplianceOfficer` verifica además si la geometría viola parámetros regulativos del RAC 14.

### 🔄 Flujo de Cálculo:
```mermaid
sequenceDiagram
    participant U as Usuario
    participant V as UI: CapacityReportView
    participant BA as BackendAgent
    participant Ag as Agentes RAC 14
    participant D as DB: DuckDB

    U->>V: Selecciona Sector y Filtros
    V->>BA: Petición de Cálculo (sector_id, filters)
    BA->>Ag: Orquesta RiskManager, Physicist y ComplianceOfficer
    Ag->>D: Query SQL vectorial
    D-->>Ag: Trazas de Vuelo (DataFrame)
    Ag-->>BA: Capacidad Estocástica + Métricas Físicas
    BA-->>V: Respuesta JSON (RAC 14 Metrics + Legacy Comparison)
    V-->>U: Muestra Reporte con Gráficos
```
### 🔍 Análisis Detallado: Secuencia de Interacción
- **Actores**:
    - **Usuario**: Disparador del evento.
    - **UI**: Captura datos y valida formulario.
    - **Backend**: Ejecuta la lógica "pura" (fórmula matemática).
    - **DB**: Motor de agregación masiva.
- **Retorno Clave**: El JSON de respuesta contiene no solo el número final, sino el desglose de pasos (`metrics.calculation_steps`) para auditoría.


---

## 🔮 4. Análisis Predictivo con Inteligencia Artificial

El módulo predictivo le permite anticiparse a la demanda futura basándose en modelos de **Aprendizaje Supervisado**.

### 📊 Interpretación de Visualizaciones:
- **Daily Demand Chart**: Muestra la línea de tendencia central. El área sombreada representa el **Intervalo de Confianza**.
- **Seasonal Trend**: Visualiza la tendencia estacional basada en el calendario oficial de Colombia y eventos personalizados. Es útil para identificar si un pico de tráfico se debe a puentes festivos, Semana Santa, recesos escolares o temporadas de fin de año.
- **Sector Saturation Chart**: Compara la demanda proyectada contra la capacidad calculada en el Módulo 3. 
    - **Alerta 🟡 (80%)**: El sector se acerca a su límite operativo.
    - **Crítico 🔴 (100%)**: Se recomienda implementar medidas de control de flujo (ATFM).

---

## ⚙️ 5. Gestión de Catálogos (Configuración)

La precisión del sistema depende de la correcta definición de los activos aeronáuticos.

- **Definición de Sectores**: Un sector NO es una geometría simple para el sistema; es una **Lógica de Conectividad**. Se define por los pares Origen-Destino que lo atraviesan.
- **Mantenimiento de Aeropuertos**: Asegúrese de que los códigos ICAO sean correctos para que los uniones (JOINs) en DuckDB no fallen.

---

## 📖 Glosario Técnico-Operativo

| Término | Definición Técnica | Referencia Normativa |
| :--- | :--- | :--- |
| **SCV** | Capacidad Simultánea de Vuelos. Límite instantáneo de gestión. | OACI Doc 9689 |
| **CH** | Capacidad Horaria. Potencial de tráfico en 60 minutos. | UAEAC Circular 006 |
| **Random Forest** | Algoritmo de ensamble usado para la predicción de residuos. | Machine Learning |
| **ETL** | Siglas de Extraer, Transformar y Cargar (Proceso de datos). | Ingeniería de Datos |

---

## 📚 6. Bibliografía de Procedimientos

1.  **UAEAC**. *Manual de Procedimientos de Control de Tránsito Aéreo*.
2.  **OACI**. *Gestión del Flujo del Tránsito Aéreo (ATFM)*.
3.  **NASA**. *Human Multi-model Analysis (Workload Theory)*. [Referencia para la fundamentación del Factor de Carga Mental 1.3].

---

> [!TIP]
> **Recomendación de Uso**: Para obtener predicciones más precisas, realice una carga de datos al menos una vez por semana para que el modelo de IA se re-entrene con las tendencias más recientes.
