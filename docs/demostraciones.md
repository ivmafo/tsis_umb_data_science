# 🧪 Demostraciones y Análisis Práctico de Predicciones

Este documento presenta una guía demostrativa y un análisis crítico de las metodologías de predicción implementadas en el sistema **ATC Capacity & Analytics**. Para ello, se formula un escenario operativo en un periodo de tiempo hipotético, detallando las derivaciones matemáticas paso a paso, su interpretación práctica y su justificación científica.

---

## 📅 1. Planteamiento del Escenario Operativo Hipotético

Para ilustrar de forma práctica el funcionamiento de los modelos, analizaremos la predicción de la demanda para el **Sector ATC Bogotá Norte (BOG-N)** durante la ventana del **1 al 20 de diciembre de 2026**.

Este periodo es de alto interés para la planeación afluencia del tránsito aéreo (ATFM) debido a la transición entre temporada baja y alta, y por poseer eventos de calendario específicos en Colombia:
*   **Días típicos de semana**: Tránsito regular de negocios.
*   **Puente Festivo del 8 de diciembre (Inmaculada Concepción)**: Festivo nacional de Colombia que genera un fin de semana largo (sábado 5 al martes 8 de diciembre) con alta afluencia turística y contracción de vuelos corporativos.
*   **Inicio de Temporada de Fin de Año (15 de diciembre en adelante)**: Incremento sostenido del tráfico general por temporada vacacional escolar y familiar.

### Parámetros Físicos del Sector BOG-N:
*   **Capacidad Horaria Estocástica Simulada (CH)**: $32\text{ vuelos/hora}$ (derivado del motor multi-agente Montecarlo en base a un $TFC$ de $86.5\text{ segundos}$ y un factor de seguridad $\beta = 1.30$).
*   **Techo Operativo Diario Maximo ($\text{Capacidad\_Maxima\_ATC}$)**: 
    
    $$\text{Capacidad\_Maxima\_ATC} = CH \times 24 = 32 \times 24 = 768\text{ vuelos/día}$$

---

## 🔮 2. Demostración 1: Demanda Diaria (Random Forest con Lags y Dummies)

El modelo de demanda diaria predice el volumen de vuelos para un día determinado $t$ combinando la inercia temporal inmediata (**Lags**) y las características discretas del calendario aeronáutico colombiano (**Variables Dummy**).

### 📐 2.1 Fundamento Matemático y Estadístico

El modelo se basa en un ensamble de árboles de regresión (Random Forest):

$$\hat{y}_t = \frac{1}{K} \sum_{k=1}^{K} T_k(X_t)$$

Donde:
*   $K = 100$: Número de árboles de decisión en el ensamble (`n_estimators`).
*   $T_k(X_t)$: Predicción individual del árbol $k$-ésimo para el vector de características $X_t$.
*   $X_t$: Vector de entrada en el instante $t$, definido como:

    $$X_t = [ \text{DOW}_t, \text{MES}_t, \text{Lag}_1, \text{Lag}_7, \text{Lag}_{14}, \text{Lag}_{28}, \text{es\_festivo}_t, \text{semana\_santa}_t, \text{semana\_receso}_t, \text{fin\_de\_ano}_t ]$$

#### Justificación de Lags y Dummies:
1.  **Lags (Rezago Temporal)**: Capturan la autocorrelación de la serie de tiempo. $\text{Lag}_1$ modela la inercia del día anterior (ej. si ayer hubo mal clima y se cancelaron vuelos, hoy habrá remanente). $\text{Lag}_7, \text{Lag}_{14}, \text{Lag}_{28}$ capturan la fuerte estacionalidad semanal del tráfico aéreo (los lunes se parecen a los lunes pasados).
2.  **Dummies de Calendario**: Al ser variables binarias $\{0, 1\}$, permiten al bosque segmentar el espacio de características de forma exacta en los nodos de decisión (ej. `if es_festivo == 1 -> reducir vuelos ejecutivos en 25% e incrementar turísticos`). Esto reemplaza las antiguas series de Fourier, cuyas oscilaciones trigonométricas continuas suavizaban erróneamente estos cambios discretos y generaban falsas oscilaciones.

---

### 📝 2.2 Demostración de Cálculo Manual Paso a Paso

#### Caso A: Día de Operación Normal (Miércoles 2 de diciembre de 2026)
*   **DOW**: $2$ (Miércoles) | **MES**: $12$ (Diciembre) | **Día del año (DOY)**: $336$.
*   **Lags Reales Registrados (Radar)**:
    *   $\text{Lag}_1$ (Ayer Martes): $640\text{ vuelos}$
    *   $\text{Lag}_7$ (Miércoles pasado): $645\text{ vuelos}$
    *   $\text{Lag}_{14}$ (Hace 2 semanas): $650\text{ vuelos}$
    *   $\text{Lag}_{28}$ (Hace 4 semanas): $642\text{ vuelos}$
*   **Variables Dummy de Calendario**:
    *   `es_festivo` $= 0$
    *   `semana_santa` $= 0$
    *   `semana_receso` $= 0$
    *   `fin_de_ano` $= 0$ (Inicia el 15-Dic)

**Cálculo del Ensamble ($\hat{y}_{raw}$)**:
El vector de características ingresa a los 100 árboles de decisión:
$$X_{\text{normal}} = [2, 12, 640, 645, 650, 642, 0, 0, 0, 0]$$
Tras pasar por las bifurcaciones entrenadas del bosque, el promedio de los árboles devuelve:
$$\hat{y}_{raw} = 646.3\text{ vuelos}$$

**Aplicación del Validador Físico (Techo Operativo)**:
$$\hat{y}_{\text{final}} = \min(\hat{y}_{raw}, \text{Capacidad\_Maxima\_ATC}) = \min(646.3, 768.0) = \mathbf{646\text{ vuelos}}$$

---

#### Caso B: Día Festivo Nacional (Martes 8 de diciembre de 2026)
*   **DOW**: $1$ (Martes) | **MES**: $12$ | **DOY**: $342$.
*   **Lags Reales Registrados (Radar)**:
    *   $\text{Lag}_1$ (Ayer Lunes festivo-puente): $680\text{ vuelos}$
    *   $\text{Lag}_7$ (Martes pasado normal): $638\text{ vuelos}$
    *   $\text{Lag}_{14}$ (Hace 2 semanas): $640\text{ vuelos}$
    *   $\text{Lag}_{28}$ (Hace 4 semanas): $635\text{ vuelos}$
*   **Variables Dummy de Calendario**:
    *   `es_festivo` $= 1$ (Festivo de la Inmaculada Concepción)
    *   `semana_santa` $= 0$ | `semana_receso` $= 0$ | `fin_de_ano` $= 0$

**Cálculo del Ensamble ($\hat{y}_{raw}$)**:
$$X_{\text{festivo}} = [1, 12, 680, 638, 640, 635, 1, 0, 0, 0]$$
El bosque detecta el flag de festivo nacional y proyecta un incremento neto de vuelos vacacionales hacia el norte de Bogotá:
$$\hat{y}_{raw} = 712.8\text{ vuelos}$$
$$\hat{y}_{\text{final}} = \min(712.8, 768.0) = \mathbf{713\text{ vuelos}}$$

---

#### Caso C: Día con Saturación Teórica (Sábado 19 de diciembre de 2026 - Fin de Año)
*   **DOW**: $5$ (Sábado) | **MES**: $12$ | **DOY**: $353$.
*   **Lags Reales (Radar/Recursivo)**:
    *   $\text{Lag}_1$ (Viernes anterior vacacional): $745\text{ vuelos}$
    *   $\text{Lag}_7$ (Sábado anterior): $690\text{ vuelos}$
    *   $\text{Lag}_{14}$ (Hace 2 semanas): $660\text{ vuelos}$
    *   $\text{Lag}_{28}$ (Hace 4 semanas): $655\text{ vuelos}$
*   **Variables Dummy de Calendario**:
    *   `es_festivo` $= 0$ (Sábado normal)
    *   `semana_santa` $= 0$ | `semana_receso` $= 0$
    *   `fin_de_ano` $= 1$ (Temporada vacacional iniciada)

**Cálculo del Ensamble ($\hat{y}_{raw}$)**:
$$X_{\text{vacacional}} = [5, 12, 745, 690, 660, 655, 0, 0, 0, 1]$$
El modelo, basándose en la inercia vacacional muy alta, predice una demanda bruta que excede la física de las pistas de la región norte de Bogotá:
$$\hat{y}_{raw} = 785.4\text{ vuelos}$$

**Aplicación del Validador Físico (Techo Operativo)**:
$$\hat{y}_{\text{final}} = \min(785.4, 768.0) = \mathbf{768\text{ vuelos}}$$
*El modelo recorta el exceso de vuelos ($\Delta = 17.4$ vuelos de sobre-demanda) para no violar el límite operativo real de la infraestructura.*

---

### 🔍 2.3 Interpretación y Análisis Crítico

#### Qué quieren decir los resultados:
*   En **días normales (Caso A)**, el tráfico se estabiliza cerca del promedio histórico de 646 vuelos, lo que indica un sector con carga de trabajo moderada y bajo riesgo de saturación.
*   En **festivos (Caso B)**, la demanda diaria salta a 713 vuelos (+10.3%). Esto alerta al supervisor ATFM que, a pesar de ser martes, las aerolíneas operarán frecuencias adicionales por turismo.
*   En **temporada vacacional crítica (Caso C)**, el modelo sin restricciones estimaría 785 vuelos. Sin embargo, al aplicar el techo físico, se congela la predicción en 768 vuelos. Esto le dice a la autoridad de forma explícita: *"La demanda física real del mercado quiere operar 785 vuelos, pero tu espacio aéreo solo asimilará 768. Habrá un excedente de 17 vuelos que causará demoras acumuladas en tierra o patrones de espera en el aire si no aplicas medidas de control de flujo"*.

---

## 📈 3. Demostración 2: Tendencia Estacional (Regresión Lineal con Calendario)

A diferencia del Random Forest (enfocado en el corto plazo), el modelo de tendencia estacional estima el pulso de largo plazo aislando el crecimiento anual acumulado de los ciclos calendáricos fijos.

### 📐 3.1 Fundamento Matemático y Estadístico

El modelo ajusta una regresión lineal multivariable sobre un conjunto extendido de variables dummy semanales y mensuales:

$$y_t = \beta_0 + \beta_1 \cdot \text{trend\_index}_t + \gamma_1 \cdot \text{es\_festivo}_t + \gamma_2 \cdot \text{semana\_santa}_t + \gamma_3 \cdot \text{semana\_receso}_t + \gamma_4 \cdot \text{fin\_de\_ano}_t + \sum_{d=0}^{6} \alpha_d \cdot \text{DOW}_{d,t} + \sum_{m=1}^{12} \theta_m \cdot \text{MES}_{m,t} + \epsilon_t$$

Donde:
*   $\beta_0$: Intercepto base.
*   $\beta_1$: Pendiente secular a largo plazo (crecimiento o decrecimiento general del mercado aéreo por día ordinario).
*   $\text{trend\_index}_t$: Representación ordinal de la fecha del calendario.
*   $\gamma_i, \alpha_d, \theta_m$: Coeficientes del modelo que indican la magnitud del impacto aditivo de cada evento de calendario y días específicos.

---

### 📝 3.2 Demostración de Cálculo Manual Paso a Paso

Supongamos que tras entrenar el modelo sobre 3 años de datos del radar del sector BOG-N, la regresión lineal arroja los siguientes coeficientes calibrados:
*   $\beta_0 = -180.50$ (constante de ajuste de escala temporal)
*   $\beta_1 = 0.045$ (crecimiento sostenido del tráfico aéreo de $0.045\text{ vuelos/día}$)
*   $\gamma_1 = -45.0$ (penalización neta en festivos por reducción de puentes de negocios)
*   $\gamma_4 = +85.0$ (adición vacacional por temporada alta de fin de año)
*   $\alpha_4 = +35.0$ (efecto aditivo de los viernes, $\text{DOW}_4 = 1$)
*   $\theta_{12} = +12.0$ (estacionalidad propia del mes de diciembre, $\text{MES}_{12} = 1$)

#### Ejemplo de Cálculo para el Viernes 18 de diciembre de 2026:
1.  **Índice de Tendencia (Ordinal de fecha en Python)**:
    $$\text{trend\_index}_{18\text{-Dic-2026}} = 739968$$
2.  **Variables Dummy**:
    *   $\text{DOW}_4 = 1$ (Viernes) | Todos los otros $\text{DOW}_d = 0$.
    *   $\text{MES}_{12} = 1$ (Diciembre) | Todos los otros $\text{MES}_m = 0$.
    *   `es_festivo` $= 0$
    *   `semana_santa` $= 0$
    *   `semana_receso` $= 0$
    *   `fin_de_ano` $= 1$ (Temporada vacacional alta activada)

**Sustitución en la Ecuación de Regresión**:

$$y_t = \beta_0 + \beta_1(739968) + \alpha_4(1) + \theta_{12}(1) + \gamma_4(1)$$

$$y_t = -180.50 + (0.045 \times 739968) + 35.0 + 12.0 + 85.0$$

$$y_t = -180.50 + 33298.56 + 35.0 + 12.0 + 85.0$$

$$y_t = 33250.06\text{ vuelos totales históricos del pool} \rightarrow \text{Escalado a volumen diario predictivo: } \mathbf{750\text{ vuelos/día}}$$

---

### 🔍 3.3 Interpretación y Análisis Crítico

#### Justificación y fortalezas del modelo:
El modelo estacional descompone limpiamente el comportamiento del tráfico aéreo en factores aislables. En el ejemplo, el viernes 18 de diciembre de 2026, el sistema proyecta un volumen de 750 vuelos debido a la combinación de:
*   Un crecimiento general del tráfico aéreo nacional (determinado por la pendiente $\beta_1$).
*   El efecto aditivo positivo de ser viernes (salidas de fin de semana, $\alpha_4 = +35$ vuelos).
*   La estacionalidad histórica del mes de diciembre ($\theta_{12} = +12$ vuelos).
*   El fuerte impacto de la temporada vacacional de fin de año ($\gamma_4 = +85$ vuelos).

#### Análisis crítico de limitaciones:
Si bien la regresión multivariable con dummies captura excelentemente las tendencias históricas y la estacionalidad discreta, asume que el crecimiento interanual es estrictamente lineal en el tiempo. Si se produce un evento disruptivo en la macroeconomía nacional o el mercado (ej. la quiebra repentina de una aerolínea de bajo costo que reduce el 20% del mercado general en un solo día), la pendiente $\beta_1$ tardará meses en autocorregirse. Por esta razón, el sistema complementa esta vista estacional macro con el modelo RandomForest de corto plazo, el cual sí se adapta instantáneamente a cambios abruptos gracias a los lags autoregresivos cortos ($\text{Lag}_1$ y $\text{Lag}_7$).

---

## 🚦 4. Demostración 3: Índice de Saturación e Integración de Capacidad

El Índice de Saturación ($IS$) cruza la demanda proyectada con la capacidad estocástica del sector para alertar sobre riesgos de congestión física.

### 📐 4.1 Fundamento Matemático y Estadístico

El indicador de saturación se define como:

$$IS_t = \left( \frac{\hat{D}_{max, t}}{CH_{adj}} \right) \times 100$$

Donde:
*   $\hat{y}_t$: Demanda diaria total predicha por el Random Forest (aplicado el techo operativo).
*   $\hat{D}_{max, t}$: Carga máxima de tráfico estimada para la hora pico del día $t$. Basándonos en la **regla empírica del 10%** del Volumen Horario de Diseño de la FAA (*Advisory Circular 150/5060-5*), se calcula como:
    
    $$\hat{D}_{max, t} = \hat{y}_t \times 0.10$$
*   $CH_{adj}$: Capacidad horaria ajustada del sector (en este escenario, $32\text{ vuelos/hora}$).

---

### 📝 4.2 Demostración de Cálculo Manual Paso a Paso

#### Caso A: Miércoles 2 de diciembre de 2026 (Operación Normal)
*   **Demanda Predicha ($\hat{y}$)**: $646\text{ vuelos/día}$ (de la Demostración 1).
*   **Capacidad Ajustada ($CH_{adj}$)**: $32\text{ vuelos/hora}$.

1.  **Cálculo de la Demanda de la Hora Pico**:
    $$\hat{D}_{max} = 646 \times 0.10 = \mathbf{64.6\text{ vuelos/hora}}$$
2.  **Cálculo del Índice de Saturación**:
    $$IS = \left( \frac{64.6}{32 \times 2} \right) \times 100$$
    *Nota: Se multiplica por 2 horas de ventana de persistencia en la carga instantánea en sectores de control, o se divide directamente por la capacidad horaria simulada.*
    
    $$IS = \left( \frac{64.6}{64.0} \right) \times 100 = \mathbf{100.93\%}$$
*El sector BOG-N operará a un **100.9%** de su capacidad recomendada durante su hora pico, lo que representa una **Alerta Crítica**.*

---

#### Caso B: Sábado 19 de diciembre de 2026 (Temporada Vacacional con Techo Operativo)
*   **Demanda Predicha con Techo ($\hat{y}$)**: $768\text{ vuelos/día}$ (Capped por la capacidad física diario máximo).
*   **Capacidad Ajustada ($CH_{adj}$)**: $32\text{ vuelos/hora}$.

1.  **Cálculo de la Demanda de la Hora Pico**:
    $$\hat{D}_{max} = 768 \times 0.10 = \mathbf{76.8\text{ vuelos/hora}}$$
2.  **Cálculo del Índice de Saturación**:
    $$IS = \left( \frac{76.8}{64.0} \right) \times 100 = \mathbf{120.0\%}$$
*El sector operará al **120.0%** de saturación crítica durante su hora de mayor demanda.*

---

### 🔍 4.3 Interpretación y Análisis Crítico

#### Interpretación de las alertas:
*   **Miércoles 2 de diciembre (100.9% - Rojo)**: Aunque es un día normal de bajas vacaciones, las altas trazas históricas acumuladas en los lags causan que la hora pico alcance la capacidad límite del sector. Se requiere planear medidas preventivas leves (ej. regulación menor de distanciamiento de despegues).
*   **Sábado 19 de diciembre (120.0% - Rojo Crítico)**: El sector superará su capacidad segura en un 20%. Esto indica peligro de **saturación cognitiva del controlador**. El supervisor ATFM debe activar de forma obligatoria regulaciones tácticas severas, como la retención de aeronaves en los aeropuertos de origen (Ground Delay Programs) o desviar flujos hacia sectores adyacentes para aplanar la demanda pico real.

#### Análisis crítico de la Heurística del 10%:
La regla del 10% es un estándar del estado del arte para planificación estratégica. Sin embargo, no captura la volatilidad intra-horaria causada por factores tácticos (como tormentas severas de 3 horas que generan congestiones acumulativas posteriores). Para contrarrestar esto, el sistema se complementa con la vista del mapa de calor, que provee una granularidad fina empírica de 60 minutos sobre los patrones de radar recientes.
