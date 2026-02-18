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

---

## 👨‍💻 5. Vocabulario del Código Fuente (Backend & Frontend)

Términos específicos encontrados en `src/` y `web/src/`.

### 5.1 Backend (Python / FastAPI)
| Término | Definición Simplificada | Ejemplo de Código |
| :--- | :--- | :--- |
| **Decorator** | Función que modifica a otra función sin cambiar su código interno. Se usa el símbolo `@`. | `@router.get("/metrics")` le dice a FastAPI que esa función responde a peticiones Web. |
| **Pydantic Model** | Clase que valida datos automáticamente. Si el tipo de dato es incorrecto, lanza error. | `class SectorConfig(BaseModel): ...` asegura que la configuración del sector tenga el formato correcto. |
| **Dependency Injection (DI)** | Técnica para pasar objetos ("servicios") a una función en lugar de crearlos dentro. Facilita el cambio de piezas. | `container.wire(modules=[...])` conecta los repositorios con los casos de uso. |
| **Yield** | Palabra clave en Python para generar valores uno a uno (generador), ahorrando memoria. | `def read_chunks(): yield chunk` procesa archivos gigantes por partes. |

### 5.2 Frontend (React / TypeScript)
| Término | Definición Simplificada | Ejemplo de Código |
| :--- | :--- | :--- |
| **Hook** | Función especial de React (empieza con `use`) para "engancharse" al ciclo de vida del componente. | `useEffect(() => { ... }, [])` ejecuta código cuando la pantalla se carga por primera vez. |
| **Props** | Argumentos que recibe un componente UI. Son de solo lectura. | `<Chart data={vuelos} />`. `data` es una prop. |
| **State** | Memoria interna de un componente. Si cambia, la pantalla se redibuja automáticamente. | `const [loading, setLoading] = useState(false)` guarda si está cargando. |
| **Interface** | Contrato en TypeScript que define la forma obligatoria de un objeto. | `interface Flight { id: string; ... }` obliga a que todo vuelo tenga ID. |

---

## 🧮 6. Desglose Matemático "Para Humanos"

Aquí explicamos las fórmulas con peras y manzanas (ejemplos numéricos).

### 6.1 Fórmula de Capacidad (C006) Explicada

$$ C = \frac{U}{t_{occ} \cdot (1 + B)} $$

**Traducción**:
> "La capacidad es qué tan lleno queremos el sector ($U$), dividido por cuánto se demora cada avión en cruzarlo ($t_{occ}$), dejándole un espacito extra por si acaso ($B$)."

**Ejemplo Paso a Paso**:
Imagina un sector (pedazo de cielo) llamado "BOG-NORTE".

1.  **Datos de Entrada**:
    *   Queremos usar el sector al **80%** de eficiencia ($U = 0.80$).
    *   Los aviones tardan en promedio **45 segundos** en cruzarlo ($t_{occ} = 45$).
    *   Dejamos un margen de seguridad del **10%** ($B = 0.10$).

2.  **Cálculo**:
    *   *Paso A (Denominador)*: Multiplicamos el tiempo por el margen.
        $$ 45 \text{ seg} \times (1 + 0.10) = 45 \times 1.10 = \mathbf{49.5} \text{ segundos ajustados} $$
        *(Esto significa que cada avión "ocupa" teóricamente 49.5 segundos)*.
    *   *Paso B (División)*: Dividimos la eficiencia por el tiempo ajustado.
        $$ C = \frac{0.80}{49.5} = \mathbf{0.01616} \text{ vuelos por segundo} $$

3.  **Conversión a Horas**:
    *   Una hora tiene 3600 segundos.
        $$ 0.01616 \times 3600 = \mathbf{58.18} \text{ vuelos por hora} $$

**Resultado Final**: El sector BOG-NORTE puede manejar máximo **58 aviones por hora**. Si entran 60, se satura.

---

### 6.2 Regresión Lineal (Tendencia) Explicada

$$ y = mx + b $$

**Traducción**:
> "Predecimos el tráfico futuro ($y$) asumiendo que crece o decrece a un ritmo constante ($m$) desde un punto de partida ($b$)."

**Ejemplo**:
Queremos predecir el tráfico para el año 2026.

1.  **Datos**:
    *   $x$: Año (2026).
    *   $m$ (Pendiente): Crecimiento de **200 vuelos extra por año** (calculado históricamente).
    *   $b$ (Intersección): En el año 0 (base), había teóricamente **5000 vuelos**.

2.  **Cálculo**:
    $$ \text{Tráfico} = (200 \times 2026) + 5000 $$
    $$ \text{Tráfico} = 405,200 + 5,000 = \mathbf{410,200} \text{ vuelos} $$

**Nota**: Nuestro sistema usa esto + *Random Forest* (que corrige el error de esta línea recta usando patrones complejos).

### 6.3 Intervalo de Confianza (Predicción)

$$ \text{Rango} = \hat{y} \pm (1.96 \times \sigma) $$

**Traducción**:
> "El valor más probable es $\hat{y}$, pero estamos 95% seguros de que el valor real caerá entre un mínimo y un máximo definidos por qué tan volátiles son los datos ($\sigma$)."

**Ejemplo**:
El modelo predice que mañana a las 8:00 AM habrá **100 vuelos** ($\hat{y}=100$).
La volatilidad histórica (desviación estándar) a esa hora es de **5 vuelos** ($\sigma=5$).

1.  **Cálculo del Margen**:
    $$ 1.96 \times 5 = \mathbf{9.8} \text{ vuelos} $$
    *(Usamos 1.96 porque eso cubre el 95% de la curva normal)*.

2.  **Rango**:
    *   Mínimo: $100 - 9.8 = 90.2$
    *   Máximo: $100 + 9.8 = 109.8$

**Interpretación**: "Esperamos 100 vuelos, pero prepárese para tener entre **90 y 110**."


