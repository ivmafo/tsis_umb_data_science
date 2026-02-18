# ATC Capacity & Analytics System

**Sistema de Procesamiento de Métricas y Cálculo de Capacidad con Arquitectura Hexagonal**

Este proyecto es una herramienta avanzada para el análisis de tráfico aéreo, cálculo de capacidad de sectores (Circular 006) y predicción de tendencias utilizando modelos híbridos de Machine Learning.

---

## 🏗️ Descripción General

El sistema permite la ingesta de grandes volúmenes de datos de vuelos, la generación de reportes detallados y la visualización interactiva de métricas clave para la toma de decisiones en el control de tráfico aéreo (ATC).

### Módulos Principales:
- **Gestión de Datos**: Ingesta incremental de archivos Excel/CSV/Parquet usando Polars y DuckDB.
- **Análisis de Capacidad**: Cálculo de capacidad de sectores basado en la fórmula de la Circular 006 (TFC, Factor R, Carga Mental).
- **Gestión Regional**: Administración de regiones aeronáuticas y asignación de aeropuertos.
- **Análisis Predictivo**: Predicción de demanda diaria, tendencias estacionales (Fourier), crecimiento de aerolíneas y saturación de sectores.
- **Visualización**: Dashboard interactivo construido con React, Vite y Tailwind CSS.

---

## 📁 Estructura del Proyecto

```
tesis/
├── src/                          # 🐍 Backend (Python + FastAPI)
│   ├── domain/                   # 🔵 Reglas de Negocio (Entidades, Puertos/Interfaces)
│   ├── application/              # 🟢 Casos de Uso (Orquestación, DTOs, DI)
│   │   ├── use_cases/            # Lógica de reportes, predicción y gestión
│   │   └── di/                   # Contenedor de Inyección de Dependencias
│   ├── infrastructure/           # 🟡 Adaptadores (DuckDB, Polars, FastAPI)
│   └── main.py                   # Punto de entrada del servidor
│
├── web/                          # ⚛️ Frontend (React + Vite + TS)
│   ├── src/
│   │   ├── components/           # Componentes UI reutilizables
│   │   └── views/                # Pantallas principales (Capacidad, Predictivo, etc.)
│   └── tailwind.config.js
│
├── data/                         # 📊 Almacenamiento de Datos (DuckDB y archivos crudos)
├── tests/                        # 🧪 Pruebas Unitarias e Integración
├── build.spec                    # 📦 Configuración para generar el ejecutable (.exe)
└── README.md
```

---

## 🚀 Instalación y Uso

### Requisitos
- Python 3.10+
- Node.js 18+ (para el desarrollo frontend)

### Configuración del Backend
1. Crear y activar entorno virtual:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecutar servidor:
   ```bash
   python run.py
   ```

### Configuración del Frontend
1. Navegar a la carpeta `web`:
   ```bash
   cd web
   npm install
   ```
2. Ejecutar en modo desarrollo:
   ```bash
   npm run dev
   ```

---

## 📈 Análisis Predictivo
El sistema implementa modelos avanzados para anticipar la demanda:
- **Tendencias Estacionales**: Uso de Series de Fourier (orden 10 anual, 3 semanal) combinadas con Regresión Lineal y Random Forest.
- **Saturación de Sectores**: Identificación de puntos críticos basados en la capacidad calculada vs. demanda proyectada.

---

## 📦 Generación de Ejecutable
Para generar la aplicación independiente (`.exe`) que incluye tanto el backend como el frontend compilado:
1. Compilar frontend: `cd web && npm run build`.
2. Ejecutar PyInstaller: `pyinstaller build.spec`.

---

## 🛠️ Tecnologías Principales
- **Backend**: FastAPI, Polars (procesamiento eficiente), DuckDB (base de datos OLAP), Scikit-Learn.
- **Frontend**: React, TypeScript, Tailwind CSS, Recharts (gráficos), Lucide React (iconos).
- **Arquitectura**: Clean Architecture / Hexagonal Architecture.

---

## 👥 Créditos
Desarrollado como sistema de apoyo para la gestión de capacidad en servicios de navegación aérea.
