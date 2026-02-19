# 📐 Fundamentación Teórica y Matemática

Este documento detalla los principios matemáticos, estadísticos y algorítmicos que sustentan el sistema, proporcionando una base rigurosa independiente de la implementación en código.

---

## 1. Geometría Computacional: Pertenencia Espacial

Para determinar si un vuelo (punto $P$) se encuentra dentro de un sector ATC (polígono $S$), utilizamos el algoritmo de **Ray Casting** (o "Even-Odd Rule"), fundamental en sistemas de información geográfica (Haines, 1994).

### 1.1 Definición Formal

Sea $S$ un polígono simple definido por una secuencia de vértices $V_0, V_1, ..., V_n$, donde $V_n = V_0$.
Sea $P = (x, y)$ un punto de prueba correspondiente a la posición de la aeronave ($\text{lon}, \text{lat}$).
Sea $R$ un rayo que parte de $P$ y se extiende hasta el infinito en una dirección fija (usualmente eje $X$ positivo).

El punto $P$ está dentro de $S$ si y solo si el rayo $R$ intersecta los bordes de $S$ un número **impar** de veces, conforme a los teoremas de topología de curvas de Jordan.

$$
P \in S \iff (\text{Intersecciones}(R, S) \mod 2) \neq 0
$$

### 1.2 Formulación Algorítmica

Para cada arista del polígono formada por $V_i$ y $V_{i+1}$:
1.  Verificar si la coordenada $Y$ del punto $P$ está dentro del rango vertical de la arista.
2.  Calcular la intersección en $X$ de la arista con la línea horizontal que pasa por $P$.
3.  Si la intersección está a la derecha de $P$, contarla.

$$
x_{int} = x_i + \frac{(y_P - y_i) \cdot (x_{i+1} - x_i)}{(y_{i+1} - y_i)}
$$

Si $x_{int} > x_P$, entonces $Counter \leftarrow Counter + 1$.

---

## 2. Gestión de Tráfico Aéreo (ATM): Capacidad de Sector

La capacidad teórica de un sector de control se deriva estrictamente de la metodología definida en la **Circular Reglamentaria 006** de la Aeronáutica Civil (Aerocivil, 2015), alineada con los estándares de la OACI Doc 9971 (OACI, 2020) para la gestión colaborativa del flujo de tránsito aéreo.

### 2.1 Derivación de la Fórmula C006

La capacidad ($C$) se define como el flujo máximo sostenible de aeronaves por unidad de tiempo, dado un nivel de servicio aceptable y limitaciones cognitivas del controlador.

A partir de la ecuación fundamental de flujo descrita en la teoría de colas aplicada a tránsito aéreo:

$$
Flujo = \frac{\text{Densidad}}{\text{Tiempo de Residencia}}
$$

Se introduce el factor de utilización máxima ($U$) y el buffer de seguridad ($B$) (Aerocivil, 2015), resultando en:

$$
C = \frac{U}{t_{occ} \cdot (1 + B)}
$$

Donde:
*   $U \in [0, 1]$: Factor de eficiencia máxima (típicamente 0.80 según OACI).
*   $B \in [0, \infty)$: Margen de buffer (típicamente 0.10 para contingencias).
*   $t_{occ}$: Tiempo promedio de ocupación en segundos.

### 2.2 Cálculo Ponderado de $t_{occ}$

El tiempo de ocupación no es constante; varía según la trayectoria y velocidad de la aeronave. Se calcula como la media aritmética de los tiempos de tránsito de todas las aeronaves $N$ en una muestra histórica, tal como se especifica en los anexos técnicos de la Circular 006:

$$
t_{occ} = \frac{1}{N} \sum_{i=1}^{N} \Delta t_i
$$

Donde $\Delta t_i = t_{exit}^{(i)} - t_{entry}^{(i)}$ es el tiempo exacto que la aeronave $i$ permaneció dentro del polígono $S$.

---

## 3. Modelos Estadísticos: Regresión Lineal (Tendencias)

Para proyectar el crecimiento del tráfico a largo plazo, se utiliza un modelo de Regresión Lineal Simple, asumiendo una relación lineal entre el tiempo ($x$) y la cantidad de vuelos ($y$), fundamentado en los principios de inferencia estadística (Hastie et al., 2009).

### 3.1 Formulación del Modelo

$$
y = \beta_0 + \beta_1 x + \epsilon
$$

*   $y$: Variable dependiente (Número de vuelos).
*   $x$: Variable independiente (Tiempo/Año).
*   $\beta_0$: Intersección con el eje $Y$ (Intercepto).
*   $\beta_1$: Pendiente de la recta (Tasa de crecimiento).
*   $\epsilon$: Término de error aleatorio con distribución normal $N(0, \sigma^2)$.

### 3.2 Estimación por Mínimos Cuadrados Ordinarios (OLS)

Los parámetros $\hat{\beta}_0$ y $\hat{\beta}_1$ se estiman minimizando la Suma de los Errores Cuadráticos (SSE), un método estándar para obtener estimadores insesgados de varianza mínima (BLUE):

$$
\min_{\beta_0, \beta_1} \sum_{i=1}^{n} (y_i - (\beta_0 + \beta_1 x_i))^2
$$

La solución analítica para la pendiente es:

$$
\hat{\beta}_1 = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sum (x_i - \bar{x})^2}
$$

---

## 4. Machine Learning: Random Forest (Predicción Horaria)

Para capturar la estacionalidad compleja y los patrones no lineales del tráfico diario que la regresión lineal no puede modelar, se emplea un ensamble de árboles de decisión (*Random Forest Regressor*), introducido por Leo Breiman (2001).

### 4.1 Árboles de Decisión y Partición

El espacio de características (hora del día, día de la semana, mes) se divide recursivamente. Para un nodo $m$ con una muestra $Q_m$, buscamos una división $\theta = (j, t_m)$ (feature $j$ y umbral $t_m$) que minimice la impureza.

Para regresión, la métrica de impureza es el Error Cuadrático Medio (MSE), tal como se implementa en bibliotecas como Scikit-Learn (Pedregosa et al., 2011):

$$
H(Q_m) = \frac{1}{N_m} \sum_{y \in Q_m} (y - \bar{y}_m)^2
$$

Donde $\bar{y}_m$ es el promedio de los valores objetivo en el nodo $m$.

### 4.2 Agregación (Bagging)

El Random Forest promedia las predicciones de $K$ árboles independientes ($T_k$), entrenados sobre subconjuntos aleatorios de datos (Bootstrap). Esta técnica de *Bootstrap Aggregating* reduce la varianza sin aumentar el sesgo (Breiman, 2001).

$$
\hat{y} = \frac{1}{K} \sum_{k=1}^{K} T_k(x)
$$

Esto mitiga el sobreajuste (overfitting) típico de los árboles de decisión individuales profundos.

### 4.3 Intervalos de Confianza (Quantile Regression Forest)

Para estimar la incertidumbre ($\hat{y} \pm \delta$), no solo predecimos la media, sino la distribución condicional completa. Aproximamos los cuantiles $q_{\alpha}$ (ej. intervalo de confianza del 95%):

$$
\hat{y}_{lower} = Q(0.025 | x), \quad \hat{y}_{upper} = Q(0.975 | x)
$$

---

## 📚 5. Bibliografía Académica y Referencias

*   **Aerocivil**. (2015). *Circular Reglamentaria 006: Metodologías para el cálculo de capacidad en sectores ATC y aeropuertos*. Unidad Administrativa Especial de Aeronáutica Civil de Colombia.
*   **Breiman, L.** (2001). Random Forests. *Machine Learning*, 45(1), 5–32. https://doi.org/10.1023/A:1010933404324
*   **Haines, E.** (1994). Point in Polygon Strategies. En *Graphics Gems IV* (pp. 24–46). Academic Press.
*   **Hastie, T., Tibshirani, R., & Friedman, J.** (2009). *The Elements of Statistical Learning: Data Mining, Inference, and Prediction*. Springer.
*   **OACI**. (2020). *Doc 9971: Manual on Collaborative Air Traffic Flow Management*. International Civil Aviation Organization.
*   **Pedregosa, F., et al.** (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.
