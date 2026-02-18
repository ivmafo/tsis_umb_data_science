# 📙 Manual de Usuario: ATC Capacity & Analytics

Bienvenido a la plataforma líder para el análisis de capacidad y proyecciones de tráfico aéreo. Este manual le guiará a través de todas las funcionalidades del sistema para maximizar su eficiencia operativa.

---

## 🚀 1. Introducción y Acceso

El sistema está diseñado para ser intuitivo y reactivo. Tras iniciar la aplicación, se encontrará con un Dashboard principal que resume el estado actual del tráfico ingestatdo.

### 🧭 Navegación Principal
Utilice la barra lateral para acceder a los módulos:
- **📊 Distribución**: Análisis geográfico y estadístico actual.
- **📑 Capacidad**: Cálculo normativo Circular 006.
- **🔮 Predicción**: Pronóstico de demanda con Inteligencia Artificial.
- **⚙️ Configuración**: Catálogos de aeropuertos, regiones y sectores.

---

## 📊 2. Análisis de Distribución de Vuelos

Este módulo le permite entender **quién, por dónde y cuándo** está volando.

### 📁 Widgets de Visualización
- **Vuelos por Región**: Identifique qué FIR (Región de Información de Vuelo) tiene mayor carga.
- **Evolución Temporal**: Vea el crecimiento del tráfico por mes y año.
- **Tipo de Vuelo**: Clasificación entre vuelos Nacionales e Internacionales.
- **Principales Aerolíneas**: Conozca a los operadores dominantes en su entorno.

---

## 📑 3. Cálculo de Capacidad (Circular 006)

Es el núcleo técnico para la planificación de recursos ATC.

### 📝 Cómo realizar un cálculo:
1.  **Seleccione un Sector**: Elija un sector configurado (ej: Sector Bogota-Cali).
2.  **Defina el Rango de Fechas**: El sistema analizará la historia para calcular el **TPS** (Tiempo promedio en sector).
3.  **Revise los Parámetros**: Asegúrese de que el **TFC** (Tiempo de Funciones de Control) sea acorde a la realidad operativa del día.
4.  **Ajuste el Factor R**: Utilice el slider para aplicar factores de ruido (clima, degradación de equipos).
5.  **Generar Reporte**: Obtenga la Capacidad Horaria Teórica y Ajustada.

---

## 🔮 4. Centro de Análisis Predictivo (IA)

Vea el futuro de la demanda aérea utilizando modelos avanzados de Machine Learning.

### 🤖 Modelos Disponibles:
- **Predicción 30 Días (Random Forest)**: Proyecta la demanda diaria. Si ve una banda de color claro alrededor de la línea, representa el margen de incertidumbre.
- **Saturación de Sectores**: Identifica momentos críticos donde la demanda superará la capacidad declarada.
- **Crecimiento de Aerolíneas**: Proyecta qué empresas aumentarán sus operaciones.
- **Tendencia Estacional**: Visualiza cómo se repetirá el tráfico en temporadas altas (fin de año, semana santa).

---

## ⚙️ 5. Gestión y Configuración

El sistema requiere de catálogos actualizados para funcionar correctamente.

### 🏷️ Maestros de Datos
- **Sectores**: Aquí se definen los límites de un sector. Debe especificar qué aeropuertos de origen y destino "pertenecen" a la lógica de ese sector.
- **Regiones**: Administración de FIRs.
- **Aeropuertos**: Mantenga actualizado el catálogo ICAO de aeródromos.

### 📥 Ingesta de Datos (Carga de Archivos)
1.  Vaya a la sección **"Repositorio de Archivos"**.
2.  Utilice el portal de carga para arrastrar sus archivos `.xlsx` o `.csv`.
3.  El sistema validará el esquema. Si hay errores, aparecerá un mensaje en rojo indicando la fila o columna inválida.
4.  Una vez cargado, los gráficos se actualizarán automáticamente.

---

## ❓ 6. Solución de Problemas y Preguntas Frecuentes

**P: Los gráficos aparecen en blanco.**
*R: Verifique que haya cargado datos para el periodo de tiempo seleccionado en los filtros. Asegúrese de que el servidor DuckDB esté conectado.*

**P: ¿Qué es el Factor R?**
*R: Es un factor de ajuste del 0.1 al 1.0 que permite al jefe de tráfico reducir la capacidad teórica por condiciones como fallas técnicas o meteorología adversa.*

**P: El modelo de IA dice "Datos Insuficientes".**
*R: Para realizar predicciones confiables, el sistema requiere al menos 14 días de historia previa en la base de datos.*

---

## 📖 Glosario de Términos
- **ATC**: Air Traffic Control.
- **TFC**: Tiempo de Funciones de Control (minutos que un controlador invierte por vuelo).
- **TPS**: Tiempo de Permanencia en Sector.
- **SCV**: Capacidad Simultánea de Vuelos (cuántos vuelos hay al mismo tiempo en el aire).
- **CH**: Capacidad Horaria (vuelos por hora).
- **R²**: Indicador de precisión del modelo de IA (entre 0 y 100%).
