# 📘 Manual Técnico Maestro: ATC Capacity & Analytics

Este documento constituye la referencia técnica definitiva y exhaustiva del sistema. Ha sido diseñado para proporcionar una visibilidad total sobre los fundamentos arquitectónicos, algoritmos matemáticos y decisiones de ingeniería que sustentan la plataforma, con un rigor académico y técnico de nivel doctoral.

---

## 🏗️ 1. Arquitectura del Sistema: Estabilidad y Desacoplamiento

El sistema implementa una **Arquitectura de Cebolla (Onion Architecture)** fusionada con el patrón de **Puertos y Adaptadores (Hexagonal Architecture)**. Esta estructura prioriza la **Inversión de Dependencias (DIP)**, asegurando que el centro del "Hexágono" sea inmune a cambios tecnológicos externos.

### 🧩 1.1 Jerarquía de Capas y Flujo de Dependencias

```mermaid
graph TD
    subgraph "Capa de Infraestructura (Adaptadores)"
        API[FastAPI Controllers / REST API]
        DB[DuckDB Columnar Storage]
        PLAD[Polars Parallel Loader]
        UI[React v18 SPA]
    end

    subgraph "Capa de Aplicación (Casos de Uso)"
        BA[BackendAgent Orchestrator]
        UC_CAP[CalculateSectorCapacity (Legacy C006)]
        UC_PRED[PredictDailyDemand]
        UC_INGEST[IngestFlightsData]
        DI_C[Dependency Injection Container]
    end

    subgraph "Capa de Dominio (Entidades y Agentes)"
        E_SECTOR[Entity: Sector]
        AG_RAC[Agents: Physicist, ComplianceOfficer, RiskManager]
        P_REPO[Port: IMetricRepository]
        P_AIRPORT[Port: IAirportRepository]
    end

    UI -- "JSON/HTTP" --> API
    API -- "Inyecta" --> BA
    BA -- "Delega FísicaRAC14" --> AG_RAC
    BA -- "Ejecuta Comparación" --> UC_CAP
    AG_RAC -- "Contrato" --> P_REPO
    P_REPO -- "Implementación" --> DB
    UC_INGEST -- "IO/Parallel" --> PLAD
```
### 🔍 Análisis Detallado: Jerarquía de Capas
- **Explicación del Gráfico**: Mapa completo de dependencias del sistema, mostrando cómo la interfaz de usuario y la persistencia son meros detalles para la lógica de negocio.
- **Componente por Componente**:
    - **UI (React)**: Consume el API JSON. No conoce la lógica de negocio, solo muestra datos.
    - **API (FastAPI)**: "Enrutador". Recibe JSON, valida con Pydantic y llama al Caso de Uso.
    - **UC (Caso de Uso)**: El "Cerebro". Orquesta la validación de negocio y llama a los Puertos.
    - **Port (Interfaz)**: El "Contrato". `IMetricRepository` dice *qué* necesitamos guardar.
    - **Adapter (DuckDB)**: El "Mecanismo". Implementa el contrato usando SQL.
- **Flujo de Retorno**:
    - `DB` retorna `Row` -> `Adapter` convierte a `Dict` -> `UC` convierte a `DTO` -> `API` convierte a `JSON` -> `UI` renderiza `Chart`.
- **Referencias Críticas**:
    - Definición de Puertos: [`src/domain/repositories/`](file:///c:/Users/LENOVO/Documents/tesis/src/domain/repositories/)
    - Implementación de Adaptadores: [`src/infrastructure/adapters/`](file:///c:/Users/LENOVO/Documents/tesis/src/infrastructure/adapters/)


---

## 🏛️ 2. Fundamentación Teórica por Capas

### 📦 2.1 Capa de Dominio (Domain Layer)
Representa la verdad absoluta del negocio. No depende de ninguna librería de terceros (excepto tipado estático).
- **Entidades de Identidad**: `Sector`, `Airport` y `Region`.
- **Value Objects**: `DateRange`, garantizando la invariante matemática de que un fin de rango nunca precede al inicio.
- **Principio de Diseño**: Asegurar que la lógica de la **Circular 006** sea expresable mediante objetos de dominio antes de tocar el código.

### 🧠 2.2 Capa de Aplicación (Application Layer)
Orquesta el tráfico de datos. Implementa el patrón **Dependency Injection (DI)** para centralizar la configuración del sistema.
- **DTOs (Data Transfer Objects)**: Utilizan Pydantic para la validación estricta de esquemas antes de la ejecución del caso de uso.
- **Casos de Uso**: Clases puras que ejecutan un único flujo de negocio (ej. `IngestFlightsData`).

### ⚡ 2.3 Capa de Infraestructura (Infrastructure Layer)
Configuración técnica de alto rendimiento.
- **DuckDB**: Base de datos **OLAP** in-process. Utiliza ejecución vectorial para agregaciones analíticas de milisegundos.
- **Polars**: Motor de procesamiento basado en **Rust**. Implementa **Evaluación Perezosa (Lazy Evaluation)** para minimizar el uso de RAM durante la ingesta de GBs de datos SRS.

---

## 🧮 3. Derivaciones Matemáticas Exhaustivas

### 📐 3.1 Modelo Normativo Circular 006 (UAEAC)

La capacidad técnica de un sector ATC se fundamenta en la cuantificación de la carga de trabajo cognitiva del controlador.

#### A. Cálculo del TPS (Time in Sector)
Dada una partición del espacio aéreo $S$, el TPS es la esperanza matemática de la duración de los tránsitos:

$$
\text{TPS} = \frac{1}{N} \sum_{i=1}^{N} (t_{\text{out}, i} - t_{\text{in}, i})
$$

Implementado en `CalculateSectorCapacity._get_tps()` mediante agregaciones SQL en DuckDB.

#### B. Capacidad Simultánea de Vuelos (SCV)
Representa el límite de saturación instantánea:

$$
\text{SCV} = \frac{\text{TPS}}{\text{TFC} \times 1.3}
$$

Donde **TFC** es la suma de Transferencia, Comunicación, Separación y Coordinación. El factor **1.3** es el **Margen de Seguridad Cognitiva** (30% de reserva).

#### C. Capacidad Horaria (CH)

$$
\text{CH} = \left( \frac{3600 \times \text{SCV}}{\text{TPS}} \right) \times R
$$

**R** es el **Factor de Ajuste de Resiliencia** (0.1 - 1.0), penalizando la capacidad teórica según condiciones meteorológicas o técnicas.

---

### 🤖 3.2 Motor Predictivo: Híbrido de Variables Dummy de Calendario y Ensamble Residual

El sistema utiliza un ensamble híbrido para capturar la tendencia a largo plazo, la ciclicidad estacional y las anomalías de tráfico usando variables binarias (dummies) de calendario.

#### A. Componente de Calendario (Variables Dummy)
En lugar de una descomposición armónica pura (Fourier), la cual difumina picos bruscos de tráfico turístico, se modelan las dinámicas nacionales de forma determinista mediante variables binarias:

$$
S_t = \gamma_1 \cdot \text{es\_festivo}_t + \gamma_2 \cdot \text{semana\_santa}_t + \gamma_3 \cdot \text{semana\_receso}_t + \gamma_4 \cdot \text{fin\_de\_ano}_t + \sum_{d=0}^{6} \alpha_d \cdot \text{DOW}_{d,t} + \sum_{m=1}^{12} \theta_m \cdot \text{MES}_{m,t}
$$

Donde:
- `es_festivo`: Indica si la fecha corresponde a un festivo nacional en Colombia (calculado vía `holidays.Colombia` con traslados por Ley Emiliani, o de la base de datos).
- `semana_santa`: Semana de festividades móviles calculada mediante el algoritmo de Pascua.
- `semana_receso`: Receso escolar oficial de Colombia en octubre (semana previa al puente de la Diversidad).
- `fin_de_ano`: Temporada alta vacacional (del 15 de diciembre al 15 de enero).

#### B. Predicción de Demanda Diaria (Random Forest)
El volumen diario de vuelos se predice entrenando un ensamble sobre las variables de calendario y retardos históricos (Lags):

$$
\hat{Y}_{t+1} = \frac{1}{100} \sum_{m=1}^{100} T_{m}(DOW, MES, L_{1}, L_{7}, L_{14}, L_{28}, \text{es\_festivo}, \text{semana\_santa}, \text{semana\_receso}, \text{fin\_de\_ano})
$$

Donde $L_{n}$ son los **Lags** de la serie de tiempo. Las predicciones futuras de demanda se restringen en tiempo de ejecución mediante el validador físico de capacidad (*Techo Operativo*): $\min(\hat{Y}_t, \text{Capacidad\_Maxima\_ATC})$.

---

## 🏛️ 4. Mapeo Técnico y Taxonomía de Código

| Componente | Archivo Fuente | Método Crítico | Teoría Aplicada |
| :--- | :--- | :--- | :--- |
| **Ingesta ETL** | `ingest_flights_data.py` | `execute()` | Parallel I/O & SIMD |
| **Orquestador RAC 14**| `backend_agent.py` | `calculate_dynamic_capacity()`| Agentes Inteligentes |
| **Simulador Montecarlo**| `risk_manager.py` | `monte_carlo_simulation()` | Inferencia Estocástica |
| **Cálculo C006** | `calculate_sector_capacity.py` | `execute()` | Sliding Window Analytic |
| **IA Predicción** | `predict_daily_demand.py` | `_train_model()` | Bootstrap Aggregation |
| **IA Estacional** | `predict_seasonal_trend.py` | `add_calendar_features()` | Colombia Calendar Dummies |
| **Proyector Crecimiento**| `predict_airline_growth.py` | `LinearRegression` | Regresión Lineal OLS |
| **Reportes Analíticos** | `generate_*_report.py` | `execute()` | Procesamiento de Pandas a PDF/Excel |
| **Repositorio** | `duckdb_repository.py` | `get_metrics()` | Columnar Storage (OLAP) |

---

## 📚 5. Bibliografía Consolidada y Referencias

### 📑 Documentación Académica
1.  **Breiman, L. (2001)**. *Random Forests*. Machine Learning, 45, 5-32.
2.  **Hyndman, R.J. (2018)**. *Forecasting: Principles and Practice*. OTexts.
3.  **Raasveldt, M. (2019)**. *DuckDB: an Embeddable Analytical Database*. SIGMOD.

### ✈️ Normativa Aeronáutica
4.  **OACI (ICAO)**. *Manual on ATS Ground Capacity Planning (Doc 9689)*.
5.  **UAEAC (Aerocivil)**. *Circular Informativa No. 006 - Determinación de Capacidad*.

### 🌐 Fuentes de Internet Técnica
6.  **FastAPI Docs**. *Dependency Injection and Async Performance*. [fastapi.tiangolo.com](https://fastapi.tiangolo.com).
7.  **Polars Dev**. *Lazy Execution and memory-mapped files*. [pola.rs](https://pola.rs).

---

> [!IMPORTANT]
> **Aviso de Integridad**: Este manual debe actualizarse tras cada cambio en el motor matemático de `src/application/use_cases` para asegurar la paridad entre la teoría y la implementación.
