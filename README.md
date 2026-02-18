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

### Running the Application

**Start the API server**:
```bash
python -m src.main
```

Or with uvicorn directly:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: **http://localhost:8000**

**API Documentation**: http://localhost:8000/docs

---

## 📡 API Endpoints

### Health Check
```http
GET /api/v1/health
```

### Get Dashboard Metrics
```http
POST /api/v1/metrics/dashboard
Content-Type: application/json

{
  "start_date": "2024-01-01T00:00:00",
  "end_date": "2024-12-31T23:59:59",
  "category": "sales",
  "use_cached": true
}
```

### Process Files
```http
POST /api/v1/metrics/process
Content-Type: application/json

{
  "file_pattern": "data/*.csv",
  "group_by": ["category", "date"],
  "clear_existing": false
}
```

### Get File Info
```http
GET /api/v1/metrics/files/info?file_pattern=data/*.csv
```

---

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Unit Tests Only
```bash
pytest tests/unit -v
```

### Run Integration Tests Only
```bash
pytest tests/integration -v
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html
```

---

## 🛠️ Development Tools

### Type Checking
```bash
mypy src/
```

### Linting
```bash
ruff check src/
```

### Auto-fix Linting Issues
```bash
ruff check src/ --fix
```

---

## 📊 Example Usage

### 1. Process CSV Files

Place your CSV files in the `data/` directory, then:

```bash
curl -X POST http://localhost:8000/api/v1/metrics/process \\
  -H "Content-Type: application/json" \\
  -d '{
    "file_pattern": "data/*.csv",
    "group_by": ["category"],
    "clear_existing": true
  }'
```

### 2. Retrieve Dashboard Metrics

```bash
curl -X POST http://localhost:8000/api/v1/metrics/dashboard \\
  -H "Content-Type: application/json" \\
  -d '{
    "category": "sales",
    "use_cached": true
  }'
```

---

## 🔧 Configuration

Edit `.env` or set environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_PATH` | `data/metrics.duckdb` | DuckDB database file path |
| `DATA_DIRECTORY` | `data` | Directory containing data files |
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8000` | API server port |
| `DEBUG` | `false` | Enable debug mode |

---

## 🏛️ Architecture Principles

### Dependency Rule

Dependencies flow **inward**:
```
Infrastructure → Application → Domain
```

The **Domain** layer never depends on outer layers.

### Ports and Adapters

- **Ports**: Interfaces defined in the domain (`MetricRepository`)
- **Adapters**: Implementations in infrastructure (`DuckDBMetricRepository`)

### Benefits

✅ **Testability**: Mock repositories easily  
✅ **Flexibility**: Swap databases without changing business logic  
✅ **Maintainability**: Clear separation of concerns  
✅ **Scalability**: Easy to add new adapters (e.g., PostgreSQL, Redis)

---

## 📝 License

This project is for educational/demonstration purposes.

---

## 👥 Contributing

This is a reference architecture. Feel free to adapt it to your needs!

---

## 🙏 Acknowledgments

- **Hexagonal Architecture**: Alistair Cockburn
- **Clean Architecture**: Robert C. Martin
- **Polars**: Ritchie Vink and contributors
- **FastAPI**: Sebastián Ramírez
