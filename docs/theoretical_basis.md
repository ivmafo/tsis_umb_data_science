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

### 1.2 Justificación e Implementación en Código

Esta aproximación matemática se implementa rigurosamente en el modelo de Machine Learning (`predict_daily_demand.py`). En lugar de realizar cálculos geoespaciales pesados sobre cada coordenada del vuelo, el sistema traduce la Definición Formal (Teoría de Conjuntos) directamente a una consulta matricial de DuckDB. 

En la función `execute` de `PredictDailyDemand`:
```python
origins_str = "', '".join(origins)
destinations_str = "', '".join(destinations)
conditions.append(f"origen IN ('{origins_str}') AND destino IN ('{destinations_str}')")
```
Esto reduce la complejidad computacional en tiempo real de $O(N \cdot K)$ (intersección poligonal geométrica clásica) a $O(1)$ mediante indexación Hash en la base de datos, lo que resulta indispensable al procesar Big Data de miles de vuelos históricos en microsegundos para alimentar los modelos predictivos AI.

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

### 2.2 Capacidad Horaria Teórica ($CH$)

La Capacidad Horaria (métrica final de flujo proyectada a una ventana de 3600 segundos) se calcula matemáticamente integrando el Factor de Seguridad o Buffer Factor ($\beta = 1.3$) sugerido por los estándares de fatiga para prevenir la saturación cognitiva del controlador:

$$
CH = \frac{3600}{TFC \cdot \beta}
$$

### 2.3 Capacidad Ajustada ($CH_{adj}$) y Código

Una vez obtenida la métrica ideal, se pasa por un "filtro de la vida real" o Factor de Complejidad ($R$). Este factor $R$ (típicamente entre 0.8 y 1.0) se codifica explícitamente en el CRUD del sistema (`manage_sectors.py`) para absorber características únicas (clima recurrente, cuellos de botella del radar, etc.).

$$
CH_{adj} = CH \cdot R
$$

Esta matemática aeronáutica se transcribe línea por línea en el motor de saturación (`predict_sector_saturation.py`):
```python
# 2. Calculate Capacity (CH)
TFC = t_transfer + t_comm_ag + t_separation + t_coordination
buffer_factor = 1.3
CH = 3600 / (TFC * buffer_factor)

R = sector.get('adjustment_factor_r', 0.8) or 0.8
CH_Adjusted = CH * R
```
Al tener este cálculo paramétrico, cualquier coordinador de vuelo puede ajustar un tiempo en la Plataforma UI y ver reflejado instantáneamente el impacto real en la Capacidad Declarada del sector, cerrando la brecha entre la teoría ATC OACI y la operación en vivo.

---

## 3. Predicción Estacional: Descomposición de Fourier

Para el módulo de **Predicción Estacional**, el sistema utiliza un modelo híbrido que combina Regresión Lineal para la tendencia secular y **Series de Fourier** para modelar la ciclicidad compleja (anual y semanal). 

### 3.1 Modelo Aditivo en Código

La demanda $y(t)$ se modela matemáticamente como:

$$
y(t) = T(t) + S_{anual}(t) + S_{semanal}(t) + \epsilon
$$

Donde $T(t)$ es la tendencia lineal y $S(t)$ son los componentes estacionales. En el archivo `predict_seasonal_trend.py`, el sistema entrena este modelo uniendo ambas piezas mediante un ensamble de *Scikit-Learn*:

```python
model = make_pipeline(StandardScaler(), LinearRegression())
model.fit(X, y)
```

### 3.2 Series de Fourier (Estacionalidad)

Para capturar la periodicidad anual ($P \approx 365.25$) y semanal ($P=7$), se utilizan sumas de senos y cosenos:

$$
S(t) = \sum_{n=1}^{N} \left( a_n \cos\left(\frac{2\pi n t}{P}\right) + b_n \sin\left(\frac{2\pi n t}{P}\right) \right)
$$

Esta matemática compleja se implementa limpiamente en el sistema a través de las funciones trigonométricas de NumPy (`np.sin`, `np.cos`) en una función interna iterativa `add_fourier_terms()`:

*   **Ciclo Anual**: La teoría exige $N=10$ armónicos para capturar picos finos (como temporada decembrina). En código:
    ```python
    t_year = data[date_col].dt.dayofyear
    for k in range(1, 11):
        data[f'sin_year_{k}'] = np.sin(2 * np.pi * k * t_year / 365.25)
    ...
    ```
*   **Ciclo Semanal**: Se exigen $N=3$ armónicos para diferenciar los patrones de fin de semana:
    ```python
    t_week = data[date_col].dt.dayofweek
    for k in range(1, 4): ...
    ```

Este enlace directo entre teoría y código permite proyectar patrones repetitivos suaves hacia el futuro (inyectando dichas variables `X` a fechas venideras), superando las limitaciones de los simples promedios móviles, y justificando el porqué el backend maneja con tanta fidelidad la ciclicidad aeronáutica interanual.

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

### 4.3 Variables de Entrada (Features) en la Arquitectura

El vector de características $X_t$ para un día $t$ se construye mediante ingeniería de variables para capturar la autocorrelación (dependencia temporal):

$$
X_t = [ DOW_t, MES_t, AÑO_t, DOY_t, Lag_1, Lag_7, Lag_{14}, Lag_{28} ]
$$

En el archivo `predict_daily_demand.py`, esta formulación teórica se define en la etapa de pre-procesamiento de `Pandas`, declarando el arreglo de *features* que usará el bosque aleatorio para encontrar los cortes (Splits):
```python
# 3. Feature Engineering Lags
for lag in [1, 7, 14, 28]:
    df[f'lag_{lag}'] = df['y'].shift(lag)

features = ['day_of_week', 'month', 'year', 'day_of_year', 'lag_1', 'lag_7', 'lag_14', 'lag_28']
X = df_train[features]
```
Esta selección garantiza que el árbol asocie de manera nativa (sin estacionalidad forzada manual) el impacto que tiene en la demanda de hoy lo que ocurrió puntualmente ayer ($Lag_1$) o hace exactamente 4 semanas ($Lag_{28}$).

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

En el submódulo `predict_airline_growth.py`, lo que realmente nos interesa extraer tras entrenar el modelo es el valor de $\beta_1$ que define la curva. Se recupera nativamente del arreglo de coeficientes tras llamar al optimizador:

```python
model = LinearRegression()
model.fit(X, y)
slope = model.coef_[0]  # Representa beta_1
```

A través de esta pendiente `slope`, el sistema clasifica automáticamente a las aerolíneas basándose en el valor estadístico puro:

* **Expansión Positiva (`slope > 0.5`):** La compañía está en crecimiento comprobable (suma en promedio más de medio vuelo base cada mes).
* **Contracción Negativa (`slope < -0.5`):** El operador está reduciendo su oferta.
* **Estable ($-0.5 \le slope \le 0.5$):** Empresas maduras cuya operación se mantiene constante, sin variaciones drásticas a largo plazo.

---

## 6. Saturación de Sectores y Picos Hora

La principal dificultad operativa es que no podemos predecir con exactitud cuántos vuelos habrá a las 10:00 AM de un martes dentro de tres meses debido a la alta volatilidad horaria. 

### 6.1 Estimación del Pico Horario (La Regla del 10%)

Para resolver esto de forma práctica en el sistema (`predict_sector_saturation.py`), optamos por utilizar el estándar aeronáutico de **Volumen Horario de Diseño**. En lugar de intentar predecir cada hora individualmente, tomamos la predicción agregada del día completo que nos da el Random Forest ($\hat{y}_{diario}$) y asumimos que durante la "hora pico" o mayor congestión del sector, se concentrará aproximadamente el 10% de las operaciones diarias:

$$
\hat{D}_{max} = \hat{y}_{diario} \cdot 0.10
$$

En el código fuente, la implementación es directa sobre cada elemento de la demanda futura, dotando al sistema de una heurística computacionalmente ultraligera a diferencia de procesar $24\times K$ predicciones estocásticas diarias:
```python
# Estimate Peak Hour Load (10% rule)
estimated_peak_hour_load = val * 0.10
```

### 6.2 Construcción del Índice de Saturación ($IS$)

Con la demanda máxima por hora estimada ($\hat{D}_{max}$ o `estimated_peak_hour_load`), cruzamos el indicador con la barrera física (Capacidad Ajustada $CH_{adj}$). 

El **Índice de Saturación ($IS$)** se calcula como una simple relación porcentual entre lo que va a llegar y lo que podemos atender:

$$
IS = \left( \frac{\hat{D}_{max}}{CH_{adj}} \right) \cdot 100
$$

La regla codificada en la línea 118 de `predict_sector_saturation.py` aplica la validación matemática contra división en ceros:
```python
saturation_index = (estimated_peak_hour_load / CH_Adjusted) * 100 if CH_Adjusted > 0 else 0
```

Para que esta matemática sea útil a nivel operativo, el propio controlador (Backend) define límites duros de decisión al generar las Alertas:
* **Operación Normal ($IS \le 80\%$):** El sector operará dentro de límites seguros.
* **Estado de Alerta ($80\% < IS \le 100\%$):** Riesgo inminente de saturación; disparador ("Trigger") preventivo para planear regulaciones ATFM (Air Traffic Flow Management).
* **Estado Crítico ($IS > 100\%$):** Demanda excesiva confirmada que sobrepasará la capacidad matemática.
---

## 📚 7. Bibliografía y Referencias

*   **Aerocivil**. (2015). *Circular Reglamentaria 006: Metodologías para el cálculo de capacidad*.
*   **Breiman, L.** (2001). Random Forests. *Machine Learning*, 45(1), 5-32. (Fundamento del algoritmo de predicción diaria).
*   **Hastie, T., Tibshirani, R., & Friedman, J.** (2009). *The Elements of Statistical Learning*. Springer. (Teoría sobre minimización de impureza en árboles).
*   **Hyndman, R. J., & Athanasopoulos, G.** (2018). *Forecasting: Principles and Practice*. OTexts. (Metodología de Lags y Series de Fourier).
*   **OACI**. (2020). *Doc 9971: Manual on Collaborative Air Traffic Flow Management*.
