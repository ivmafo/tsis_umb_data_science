# 📖 Glosario Técnico y Vocabulario

Este documento sirve como diccionario centralizado para interpretar la terminología aeronáutica, matemática y de ingeniería de software utilizada en el proyecto **ATC Capacity & Analytics**.

---

## ✈️ 1. Acrónimos Aeronáuticos

| Sigla | Significado (Español/Inglés) | Definición y Contexto en el Proyecto |
| :--- | :--- | :--- |
| **ATC** | Control de Tránsito Aéreo (*Air Traffic Control*) | Servicio que gestiona el tráfico de aeronaves para evitar colisiones. Contexto: Todo el dominio del problema. |
| **SRS** | Sistema de Radar Secundario (*Secondary Radar System*) | Fuente de datos crudos. Archivos `.csv` que contienen `lat`, `lon`, `alt` y `time` de cada vuelo. |
| **ACC** | Centro de Control de Área (*Area Control Center*) | Dependencia que gestiona vuelos en ruta (ej. BOG-ACC). |
| **FL** | Nivel de Vuelo (*Flight Level*) | Altitud en cientos de pies (ej. FL350 = 35,000 pies). Usado para definir el volumen vertical de un sector. |
| **TPS** | Tráfico Por Sector (*Traffic Per Sector*) | Métrica de conteo de aeronaves dentro de un polígono en un instante $t$. |
| **SCV** | Salidas de Capacidad declaradas | Valor máximo teórico de vuelos que un sector puede manejar por hora. |
| **CH** | Capacidad Horaria | Resultado final de la fórmula C006. |

---

## 💻 2. Vocabulario de Ingeniería de Software (Inglés -> Español)

Términos técnicos que mantienen su nombre en inglés por convención de la industria.

| Término | Traducción/Concepto | Explicación Aplicada | Ubicación |
| :--- | :--- | :--- | :--- |
| **Lazy Evaluation** | Evaluación Perezosa | Estrategia de **Polars** donde no se leen los datos del disco hasta que se pide un resultado final (`.collect()`). Permite procesar 10GB en una RAM de 4GB. | [infrastructure.md](infrastructure.md) |
| **Wiring** | Cableado / Conexión | Proceso de inyección de dependencias donde se "conectan" las interfaces con sus implementaciones concretas en el `Container`. | [architecture.md](architecture.md) |
| **Payload** | Carga Útil | El cuerpo de datos JSON que se envía en una petición HTTP (`POST` o `PUT`). Ej. Los filtros de fecha al pedir una predicción. | [application.md](application.md) |
| **Boilerplate** | Código Repetitivo | Código estándar necesario para configurar algo (ej. `FastAPI` setup), que no es lógica de negocio *per se*. | [codebase_guide.md](codebase_guide.md) |
| **Middleware** | Intermediario | Software que se ubica entre el SO y la aplicación, o entre capas de red. Aquí: `CORSMiddleware` para permitir peticiones del frontend. | [infrastructure.md](infrastructure.md) |
| **Prop Drilling** | Taladrado de Propiedades | (Antipatrón) Pasar datos de un componente padre a un nieto a través de hijos que no los usan. Aquí se evita usando Context o composición. | [frontend.md](frontend.md) |
| **DTO** | Data Transfer Object | Objeto simple sin comportamiento, usado solo para transportar datos entre procesos (Backend -> Frontend). | [application.md](application.md) |

---

## 🧮 3. Símbolos y Conceptos Matemáticos

Definición rigurosa de la notación usada en fórmulas y algoritmos.

### 3.1 Símbolos Generales

| Símbolo | Nombre | Significado Matemático | Uso en el Proyecto |
| :---: | :--- | :--- | :--- |
| $\sum$ | Sumatoria | Suma de una secuencia de números. | Cálculo del Tiempo Promedio de Ocupación ($t_{occ}$). |
| $\in$ | Pertenece a | Indica que un elemento es parte de un conjunto. | $vuelo \in Sector$ (Gometría computacional). |
| $\sigma$ | Sigma (minúscula) | Desviación Estándar. | Intervalos de confianza en la predicción de demanda. |
| $\mathbb{R}^n$ | Espacio Real n-dim | Conjunto de n-tuplas de números reales. | Los vectores de features para el modelo Random Forest. |

### 3.2 Fórmulas Específicas (Circular 006)

**Fórmula de Capacidad**:
$$ C = \frac{U}{t_{occ} \cdot (1 + B)} $$

Donde:
*   **$C$ (Capacidad)**: Vuelos por hora sostenibles.
*   **$U$ (Utilización)**: Factor de eficiencia máxima (típicamente 0.8 o 80%).
*   **$t_{occ}$ (Tiempo de Ocupación)**: Promedio ponderado de segundos que un vuelo tarda en cruzar el sector.
    $$ t_{occ} = \frac{\sum_{i=1}^{N} t_i}{N} $$
*   **$B$ (Buffer)**: Margen de seguridad para imprevistos (0.1 o 10%).

---

## 📈 4. Conceptos Estadísticos y de Machine Learning

| Concepto | Definición Simple | Interpretación en el Proyecto |
| :--- | :--- | :--- |
| **R² Score** | Coeficiente de Determinación | Mide qué tan bien el modelo replica los resultados observados. **0.89** significa que el modelo captura el 89% del comportamiento del tráfico. |
| **MAE** | Error Absoluto Medio | El error promedio en unidades reales. MAE=2.4 significa que la predicción falla por ~2.4 vuelos. |
| **Outlier** | Valor Atípico | Un dato muy alejado del promedio (ej. un día con 0 vuelos por falla de radar). Se filtran en el ETL. |
| **Feature Engineering** | Ingeniería de Características | Crear nuevas variables (ej. "Día de la semana", "Mes") a partir de la fecha para ayudar al modelo a aprender patrones. |

