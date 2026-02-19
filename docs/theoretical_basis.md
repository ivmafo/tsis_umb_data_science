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

*   **TPS (Tiempo Promedio en Sector)**: Equivalente al tiempo de residencia ($t_{occ}$). Se calcula como la media aritmética de la duración de todos los vuelos $N$ en la muestra histórica.
    $$
    TPS = \frac{1}{N} \sum_{i=1}^{N} \text{duracion}_i
    $$

*   **TFC (Tiempo de Funciones de Control)**: Es la suma de los tiempos manuales requeridos por el controlador para gestionar un vuelo típico.
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

Para la predicción a corto plazo (30 días), se emplea un **Random Forest Regressor** no paramétrico, capaz de capturar no linealidades y relaciones complejas entre variables de calendario.

### 4.1 Ingeniería de Características (Lags)

El vector de características $X$ para el día $t$ incluye retardos temporales (autocorrelación):

$$
X_t = [ \text{dia\_semana}, \text{mes}, y_{t-1}, y_{t-7}, y_{t-14}, y_{t-28} ]
$$

Esto permite que el modelo "aprenda" la dependencia del tráfico con respecto al día anterior y a la misma semana del mes pasado.

### 4.2 Estimación de Incertidumbre

El intervalo de confianza del 95% se estima utilizando la dispersión de las predicciones de los árboles individuales del bosque ($T_k$).

$$
\sigma_{pred} = \text{std\_dev}(\{T_k(X) \mid k=1..K\})
$$
$$
IC_{95\%} = \hat{y} \pm 1.96 \cdot \sigma_{pred}
$$

---

## 5. Regresión Lineal: Crecimiento de Aerolíneas

Para el módulo de **Crecimiento de Aerolíneas**, se aplica el método de Mínimos Cuadrados Ordinarios (OLS) sobre series temporales agregadas mensualmente.

$$
y = \beta_0 + \beta_1 \cdot t
$$

Donde la pendiente $\beta_1$ representa la **Tasa de Crecimiento Mensual** (vuelos/mes). Una $\beta_1$ positiva significativa indica expansión de mercado, mientras que negativa indica contracción.

---

## 6. Saturación de Sectores y Picos Hora

### 6.1 Perfilamiento Estadístico (Picos Hora)

No es un modelo predictivo *per se*, sino una agregación estadística. Se calcula la intensidad $I$ para cada hora del día ($h$) y día de la semana ($d$):

$$
I_{d,h} = \frac{1}{|D_{d}|} \sum_{date \in D_d} \text{vuelos}(date, h)
$$

### 6.2 Índice de Saturación ($IS$)

Calculado en el módulo de **Saturación**, cruza la demanda máxima estimada ($\hat{D}_{max}$) con la capacidad ajustada ($CH_{adj}$).

$$
IS = \left( \frac{\hat{D}_{max}}{CH_{adj}} \right) \cdot 100
$$

*   **Normal**: $IS \le 80\%$
*   **Alerta**: $80\% < IS \le 100\%$
*   **Crítico**: $IS > 100\%$

---

## 📚 7. Bibliografía y Referencias

*   **Aerocivil**. (2015). *Circular Reglamentaria 006: Metodologías para el cálculo de capacidad*.
*   **Breiman, L.** (2001). Random Forests. *Machine Learning*.
*   **Bloomfield, P.** (2004). *Fourier Analysis of Time Series: An Introduction*. Wiley. (Base para la descomposición estacional).
*   **Hastie, T., et al.** (2009). *The Elements of Statistical Learning*. Springer.
*   **OACI**. (2020). *Doc 9971: Manual on Collaborative Air Traffic Flow Management*.
