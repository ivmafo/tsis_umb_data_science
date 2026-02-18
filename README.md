# Metrics Processing System

**Hexagonal Architecture Data Processing System with Polars and FastAPI**

A production-ready data processing system built following **Hexagonal Architecture** (Ports and Adapters) and **Clean Architecture** principles. Efficiently processes 100+ CSV/Parquet files (30MB each) using Polars' lazy evaluation and streaming capabilities, calculates aggregated metrics, and exposes them through a FastAPI REST API.

---

## 🏗️ Architecture Overview

This project implements **Hexagonal Architecture** (also known as Ports and Adapters) to achieve:

- **Dependency Inversion**: Core business logic has zero external dependencies
- **Testability**: Easy to mock and test each layer independently
- **Flexibility**: Swap implementations (e.g., PostgreSQL → DuckDB) without changing business logic
- **Maintainability**: Clear separation of concerns across layers

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                     │
│                    metrics_controller.py                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Use Cases (Orchestration)                           │   │
│  │  - GetDashboardMetrics                               │   │
│  │  - ProcessFiles                                      │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  DTOs (Pydantic v2)                                  │   │
│  │  - MetricDTO, DashboardMetricsRequest, etc.          │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ depends on (interfaces only)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Domain Layer                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Entities (Business Objects)                         │   │
│  │  - Metric                                            │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Value Objects                                       │   │
│  │  - DateRange                                         │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Repository Interfaces (PORTS)                       │   │
│  │  - MetricRepository (abstract)                       │   │
│  │  - DataSourceRepository (abstract)                   │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ implemented by
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Adapters (Concrete Implementations)                 │   │
│  │  - PolarsDataSource (streaming, lazy API)            │   │
│  │  - DuckDBMetricRepository                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
tesis/
├── src/
│   ├── domain/                          # 🔵 Core Business Logic (no dependencies)
│   │   ├── entities/
│   │   │   └── metric.py               # Metric entity with business rules
│   │   ├── value_objects/
│   │   │   └── date_range.py           # DateRange value object
│   │   └── repositories/               # Abstract interfaces (PORTS)
│   │       ├── metric_repository.py
│   │       └── data_source_repository.py
│   │
│   ├── application/                     # 🟢 Use Cases & Orchestration
│   │   ├── use_cases/
│   │   │   ├── get_dashboard_metrics.py
│   │   │   └── process_files.py
│   │   ├── dtos/
│   │   │   └── metric_dto.py           # Pydantic v2 models
│   │   └── di/
│   │       └── container.py            # Dependency Injection
│   │
│   ├── infrastructure/                  # 🟡 Adapters & External Implementations
│   │   ├── adapters/
│   │   │   ├── polars/
│   │   │   │   └── polars_data_source.py    # Polars streaming adapter
│   │   │   ├── database/
│   │   │   │   └── duckdb_metric_repository.py
│   │   │   └── api/
│   │   │       └── metrics_controller.py    # FastAPI endpoints
│   │   └── config/
│   │       └── settings.py             # Pydantic Settings
│   │
│   └── main.py                         # Application entry point
│
├── web/                                # ⚛️ Frontend React Application
├── tests/
│   ├── unit/                           # Unit tests with mocks
│   │   └── application/
│   │       └── test_get_dashboard_metrics.py
│   ├── integration/                    # Integration tests
│   │   └── test_polars_adapter.py
│   └── conftest.py                     # Pytest fixtures
│
├── data/                               # Data files directory
├── .env.example                        # Environment variables template
├── pyproject.toml                      # Project configuration
├── requirements.txt                    # Dependencies
└── README.md                           # This file
```

---

## 🎯 Key Design Decisions

### 1. **Hexagonal Architecture (Ports and Adapters)**

- **Domain Layer**: Pure business logic with zero external dependencies
- **Ports**: Abstract interfaces (`MetricRepository`, `DataSourceRepository`)
- **Adapters**: Concrete implementations (Polars, DuckDB, FastAPI)
- **Benefit**: Easy to swap Polars for Dask, or DuckDB for PostgreSQL

### 2. **Polars Lazy API for Streaming**

```python
# Efficient processing of 100+ files without loading all into memory
lazy_df = pl.scan_csv(file_paths)  # Lazy evaluation
result = lazy_df.group_by(...).agg(...).collect()  # Execute only when needed
```

### 3. **DuckDB for Analytical Queries**

- Embedded OLAP database (like SQLite but for analytics)
- Integrates seamlessly with Polars
- No separate database server needed

### 4. **Dependency Injection**

Uses `dependency-injector` to wire dependencies:

```python
container = Container()
use_case = container.get_dashboard_metrics_use_case()
```

### 5. **Pydantic v2 for Strict Typing**

All API requests/responses use Pydantic models with validation:

```python
class MetricDTO(BaseModel):
    metric_id: str = Field(..., min_length=1)
    value: Decimal = Field(..., ge=0)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Virtual environment (recommended)

### Installation

1. **Clone and navigate to the project**:
   ```bash
   cd tesis
   ```

2. **Activate virtual environment**:
   ```bash
   # Windows
   .\\venv\\Scripts\\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

---

## 📚 Documentación Técnica (NUEVO)
Este proyecto incluye documentación técnica autogenerada detallada:
1. Asegúrate de tener el entorno virtual activo.
2. Ejecuta el servidor de documentación:
   ```bash
   mkdocs serve -a localhost:9800
   ```
3. Abre en tu navegador: **http://localhost:9800**

> [!NOTE]
> La aplicación principal sigue funcionando en el puerto **8000** (`run.py`). La documentación técnica es un servicio separado para desarrollo en el puerto **9800**.

---

## 🧪 Testing

### Run All Tests
```bash
pytest
```

---

## 📝 License

This project is for educational/demonstration purposes.
