# 📐 Fundamentación Teórica y Matemática

Este documento detalla los principios matemáticos, estadísticos y algorítmicos que sustentan los módulos de **"Predictiva AI"** y **"Reporte de Capacidad"**, proporcionando una base rigurosa independiente de la implementación en código.

---

## 1. Definición de Sector: Heurística de Conectividad

A diferencia de los enfoques tradicionales basados en geometría computacional (e.g., Ray Casting), el sistema implementa una **Heurística de Conectividad** para determinar la pertenencia de un vuelo a un sector. Este modelo define un sector no como un polígono en el espacio, sino como un conjunto de reglas lógicas sobre el grafo de rutas aeroportuarias.

### 1.1 Definición Formal (Teoría de Conjuntos)

Sea $S$ un sector definido por la tupla $(O_S, D_S)$, donde:

*   $O_S$: Conjunto de aeropuertos de origen permitidos (e.g., $\{SKBO, SKRG\}$).
*   $D_S$: Conjunto de aeropuertos de destino permitidos.

Sea $f$ un vuelo caracterizado por el par ordenado $(o_f, d_f)$, correspondiente a sus aeropuertos de origen y destino reales.

La función de pertenencia $\mathbb{I}(f, S)$ se define mediante la intersección de condiciones lógicas:

$$
f \in S \iff (O_S = \emptyset \lor o_f \in O_S) \land (D_S = \emptyset \lor d_f \in D_S)
$$

### 1.2 Justificación de Implementación

Esta aproximación reduce la complejidad computacional de $O(N \cdot K)$ a $O(1)$ mediante búsquedas hash, optimizando el procesamiento de Big Data.

---

## 2. Reporte de Capacidad (Cálculo ATM)

El cálculo de capacidad sigue la metodología de la **Circular Reglamentaria 006** (Aerocivil, 2015) y el Doc 9971 de la OACI, pero implementa una derivación específica basada en la carga de trabajo del controlador ($TFC$).

### 2.1 Variables Fundamentales

**TPS (Tiempo Promedio en Sector)**: Equivalente al tiempo de residencia ($t_{occ}$). Se calcula como la media aritmética de la duración de todos los vuelos $N$ en la muestra histórica.

$$
TPS = \frac{1}{N} \sum_{i=1}^{N} \text{duracion}_i
$$

**TFC (Tiempo de Funciones de Control)**: Es la suma de los tiempos manuales requeridos por el controlador para gestionar un vuelo típico.

$$
TFC = t_{transfer} + t_{comms} + t_{sep} + t_{coord}
$$

### 2.2 Capacidad Simultánea de Vuelos (SCV)

Representa el número máximo de aeronaves que pueden ser atendidas simultáneamente bajo una carga de trabajo segura. Se introduce un factor de buffer de seguridad ($\beta = 1.3$) para evitar la saturación cognitiva.

$$
SCV = \frac{TPS}{TFC \cdot \beta}
$$

### 2.3 Capacidad Horaria (CH)

Es la métrica final de flujo, proyectando el SCV a una ventana de una hora (3600 segundos).

$$
CH = \frac{3600 \cdot SCV}{TPS}
$$

### 2.4 Capacidad Ajustada ($CH_{adj}$)

Se aplica un factor de reducción $R$ (típicamente 0.8 a 1.0) para tener en cuenta la complejidad del sector o contingencias externas.

$$
CH_{adj} = CH \cdot R
$$

---

## 3. Predicción Estacional: Descomposición de Fourier

Para el módulo de **Predicción Estacional**, el sistema utiliza un modelo híbrido que combina Regresión Lineal para la tendencia secular y **Series de Fourier** para modelar la ciclicidad compleja (anual y semanal).

### 3.1 Modelo Aditivo

La demanda $y(t)$ se modela como:

$$
y(t) = T(t) + S_{anual}(t) + S_{semanal}(t) + \epsilon
$$

Donde $T(t)$ es la tendencia lineal y $S(t)$ son los componentes estacionales.

### 3.2 Series de Fourier (Estacionalidad)

Para capturar la periodicidad anual ($P \approx 365.25$) y semanal ($P=7$), se utilizan sumas de senos y cosenos.

$$
S(t) = \sum_{n=1}^{N} \left( a_n \cos\left(\frac{2\pi n t}{P}\right) + b_n \sin\left(\frac{2\pi n t}{P}\right) \right)
$$

*   **Ciclo Anual**: Se utilizan $N=10$ armónicos para capturar picos finos (e.g., temporada alta decembrina).
*   **Ciclo Semanal**: Se utilizan $N=3$ armónicos para diferenciar patrones de fin de semana.

Este enfoque permite proyectar patrones repetitivos suaves hacia el futuro, superando las limitaciones de los promedios simples.

---

## 4. Predicción de Demanda Diaria: Random Forest

El sistema emplea un algoritmo de **Random Forest Regressor** (Bosque Aleatorio) para estimar la demanda futura. Este método no paramétrico es ideal para series temporales complejas porque captura interacciones no lineales entre variables (ej. "el tráfico aumenta los viernes, pero solo si no es feriado") sin requerir supuestos de normalidad en los datos (Breiman, 2001).

### 4.1 Formulación Matemática del Modelo

Un Random Forest es un ensamble de $K$ árboles de regresión $\{T_1, T_2, ..., T_K\}$.

Para un vector de entrada $X$ (las características del día a predecir), la predicción final $\hat{y}$ es el promedio de las predicciones de todos los árboles individuales:

$$
\hat{y} = \frac{1}{K} \sum_{k=1}^{K} T_k(X)
$$

### 4.2 Construcción de los Árboles (Entrenamiento)

Cada árbol $T_k$ se entrena con una muestra aleatoria del dataset original (Bootstrap). En cada nodo del árbol, se selecciona un subconjunto de variables candidatas para encontrar el mejor corte.

El criterio para dividir un nodo y crear ramas es la minimización de la **Impureza** (Impurity), que para tareas de regresión es el **Error Cuadrático Medio (MSE)**.

Si un nodo $m$ contiene un conjunto de muestras $Q_m$ con $N_m$ observaciones, buscamos dividirlo en dos subconjuntos $Q_{left}$ y $Q_{right}$ mediante un umbral $\theta$. La función de costo $H$ que minimizamos es:

$$
H(Q_m) = \sum_{y \in Q_{left}} (y - \bar{y}_{left})^2 + \sum_{y \in Q_{right}} (y - \bar{y}_{right})^2
$$

*   **Donde**:
    *   $\bar{y}_{left}$ es el promedio de la demanda en el hijo izquierdo.
    *   $\bar{y}_{right}$ es el promedio de la demanda en el hijo derecho.

El algoritmo busca iterativamente el corte que reduce la varianza interna de los nodos resultantes, agrupando días con comportamientos similares.

### 4.3 Variables de Entrada (Features)

El vector de características $X_t$ para un día $t$ se construye mediante ingeniería de variables para capturar la autocorrelación (dependencia temporal):

$$
X_t = [ DOW_t, MES_t, Lag_1, Lag_7, Lag_{14}, Lag_{28} ]
$$

**Definición de Variables**:

1.  **Variables Calendario**:
    *   $DOW_t$: Día de la semana (0=Lunes ... 6=Domingo). Captura el ciclo semanal.
    *   $MES_t$: Mes del año (1..12). Captura la estacionalidad anual macro.

2.  **Lags Temporales (Autocorrelación)**:
    *   $Lag_1 = y_{t-1}$: Demanda del día anterior (Inercia inmediata).
    *   $Lag_7 = y_{t-7}$: Demanda del mismo día la semana pasada (Patrón semanal).
    *   $Lag_{14} = y_{t-14}$ y $Lag_{28}$: Tendencias quincenales y mensuales.

### 4.4 Cálculo de Incertidumbre y Confianza

A diferencia de los modelos estadísticos clásicos que proporcionan un único valor futuro, en nuestro proyecto aprovechamos la estructura del Random Forest para estimar qué tan seguros estamos de una predicción.

En la implementación actual (`predict_daily_demand.py`), no usamos fórmulas paramétricas tradicionales para el intervalo de confianza. Lo que hacemos es pedirle una predicción a cada uno de los 100 árboles del ensamble y medir qué tanto difieren entre sí sus respuestas.

1. Primero, calculamos la desviación estándar ($\sigma_{pred}$) de estas 100 predicciones individuales:

$$
\sigma_{pred} = \sqrt{ \frac{1}{K-1} \sum_{k=1}^{K} (T_k(X) - \hat{y})^2 }
$$

2. Luego, apoyándonos en el Teorema del Límite Central, construimos el intervalo de confianza del 95% ($IC_{95}$) usando la aproximación normal ($Z=1.96$):

$$
IC_{upper} = \hat{y} + 1.96 \cdot \sigma_{pred}
$$

$$
IC_{lower} = \max(0, \hat{y} - 1.96 \cdot \sigma_{pred})
$$

El uso de `max(0, ...)` en el código simplemente evita proyectar valores de tráfico negativos. Lo interesante de este enfoque es que la incertidumbre se vuelve dinámica: si intentamos predecir un día históricamente inestable, los árboles no se pondrán de acuerdo, la desviación estándar crecerá, y nuestra banda de confianza será mucho más ancha, alertándonos del riesgo.

---

## 5. Regresión Lineal: Crecimiento de Aerolíneas

Para analizar el crecimiento del mercado, decidimos aislar el "ruido" diario (como picos por festivos o variaciones semanales) y enfocarnos exclusivamente en la tendencia macroeconómica mensual o anual de cada operador. Para esto, implementamos una Regresión Lineal Simple usando el método de Mínimos Cuadrados Ordinarios (OLS).

La ecuación base es la estándar:

$$
y = \beta_0 + \beta_1 \cdot t
$$

Donde $t$ es el índice temporal (el mes o año a evaluar) e $y$ es la cantidad de vuelos operados.

### 5.1 Interpretación de la Pendiente ($\beta_1$) en el Negocio

En el submódulo `predict_airline_growth.py`, lo que realmente nos interesa extraer tras entrenar el modelo es el valor de $\beta_1$ (accesible vía `model.coef_[0]`). Esta pendiente nos da directamente la **Tasa de Crecimiento** de la aerolínea (cuántos vuelos adicionales agrega por cada mes que pasa).

Para facilitar el análisis en la interfaz, el sistema clasifica automáticamente a las aerolíneas basándose en este valor estadístico:

* **Expansión Positiva ($\beta_1 > 0.5$):** La compañía está en crecimiento comprobable (suma en promedio más de medio vuelo base cada mes).
* **Contracción Negativa ($\beta_1 < -0.5$):** El operador está reduciendo su oferta.
* **Estable ($-0.5 \le \beta_1 \le 0.5$):** Empresas maduras cuya operación se mantiene constante, sin variaciones drásticas a largo plazo.

---

## 6. Saturación de Sectores y Picos Hora

La principal dificultad operativa es que no podemos predecir con exactitud cuántos vuelos habrá a las 10:00 AM de un martes dentro de tres meses debido a la alta volatilidad horaria. 

### 6.1 Estimación del Pico Horario (La Regla del 10%)

Para resolver esto de forma práctica en el sistema (`predict_sector_saturation.py`), optamos por utilizar el estándar aeronáutico de **Volumen Horario de Diseño**. En lugar de intentar predecir cada hora individualmente, tomamos la predicción agregada del día completo que nos da el Random Forest ($\hat{y}_{diario}$) y asumimos que durante la "hora pico" o mayor congestión del sector, se concentrará aproximadamente el 10% de las operaciones diarias:

$$
\hat{D}_{max} = \hat{y}_{diario} \cdot 0.10
$$

Esta heurística es mucho más robusta computacionalmente y suficientemente precisa para planeación a mediano y largo plazo.

### 6.2 Construcción del Índice de Saturación ($IS$)

Con la demanda máxima por hora estimada ($\hat{D}_{max}$), ahora debemos cruzarla con la barrera física de lo que un controlador puede manejar. Esta barrera es la Capacidad Ajustada ($CH_{adj}$).

Calculamos la capacidad base sumando los tiempos que le toma al controlador gestionar un vuelo individual ($TFC = \text{T. Transferencia} + \text{T. Comunicaciones} + \dots$). Para evitar saturación cognitiva, le aplicamos un margen de seguridad ($\beta = 1.3$) y finalmente ajustamos por complejidad del sector (factor $R$):

$$
CH_{adj} = \left(\frac{3600}{TFC \cdot \beta}\right) \cdot R
$$

Finalmente, el **Índice de Saturación ($IS$)** se calcula como una simple relación porcentual entre lo que va a llegar y lo que podemos atender:

$$
IS = \left( \frac{\hat{D}_{max}}{CH_{adj}} \right) \cdot 100
$$

Para que esta matemática sea útil a nivel operativo, el código define límites duros de decisión:
* **Operación Normal ($IS \le 80\%$):** El sector operará dentro de límites seguros.
* **Estado de Alerta ($80\% < IS \le 100\%$):** Riesgo inminente de saturación; es el momento ideal para planear regulaciones ATFM (Air Traffic Flow Management).
* **Estado Crítico ($IS > 100\%$):** Demanda excesiva confirmada que sobrepasará la capacidad del control manual.
---

## 📚 7. Bibliografía y Referencias

*   **Aerocivil**. (2015). *Circular Reglamentaria 006: Metodologías para el cálculo de capacidad*.
*   **Breiman, L.** (2001). Random Forests. *Machine Learning*, 45(1), 5-32. (Fundamento del algoritmo de predicción diaria).
*   **Hastie, T., Tibshirani, R., & Friedman, J.** (2009). *The Elements of Statistical Learning*. Springer. (Teoría sobre minimización de impureza en árboles).
*   **Hyndman, R. J., & Athanasopoulos, G.** (2018). *Forecasting: Principles and Practice*. OTexts. (Metodología de Lags y Series de Fourier).
*   **OACI**. (2020). *Doc 9971: Manual on Collaborative Air Traffic Flow Management*.
