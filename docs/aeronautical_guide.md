# ✈️ Manual Aeronáutico para Principiantes

¡Bienvenido al mundo de la gestión del tráfico aéreo! Si eres nuevo en la aeronáutica, este manual es tu pasaporte para entender **qué es este sistema, para qué sirve y cómo funcionan sus cálculos matemáticos e inteligencia artificial**, explicado desde cero y con ejemplos de la vida real.

---

## 1. ¿Qué es este Sistema y Para Qué Sirve?

Imagina el cielo como una red invisible de autopistas (Aerovías). Estas autopistas no tienen semáforos, pero tienen **Controladores de Tráfico Aéreo (ATC - Air Traffic Controllers)**. Su trabajo es asegurar que los aviones mantengan distancias seguras (separación) para que no choquen, mientras garantizan que los vuelos lleguen a tiempo.

**El Problema:**
El espacio aéreo está dividido en bloques imaginarios llamados **Sectores**. Un controlador humano solo puede manejar un número máximo de aviones al mismo tiempo dentro de su sector antes de fatigarse o perder el control de la situación. A ese límite lo llamamos **Capacidad del Sector**.

**La Solución (Este Sistema):**
Nuestro software **ATC Capacity & Analytics** es un "asistente inteligente" para los directores de la torre de control. Hace tres cosas fundamentales:
1. **Analiza el Pasado:** Lee radares históricos para saber cómo vuelan realmente los aviones.
2. **Calcula el Presente (RAC 14):** Calcula matemáticamente cuántos aviones caben con seguridad en un sector específico hoy.
3. **Predice el Futuro (Inteligencia Artificial):** Adivina cuántos vuelos habrá mañana o la próxima semana, y lanza alertas en rojo si el sector se va a saturar (es decir, si van a llegar más aviones de los que el controlador puede manejar).

---

## 2. Los Términos Aeronáuticos (Diccionario Básico)

Antes de hablar de números, entendamos el vocabulario clave que verás en el software:

*   **ATC (Air Traffic Control):** El servicio que guía a los aviones desde tierra. 
*   **Sector:** Un trozo del cielo asignado a un solo controlador. Imagina una "caja" en el cielo; todo avión que entre allí debe hablar con el dueño de esa caja.
*   **TFC (Tiempo de Funciones de Control):** Los segundos que un controlador invierte mentalmente y hablando por radio con un solo avión. *Ejemplo: "Avianca 123, suba al nivel 300"* toma unos 15 segundos de trabajo.
*   **ROT (Runway Occupancy Time - Tiempo de Ocupación de Pista):** Los segundos que una aeronave tarda desde que toca el asfalto hasta que sale de la pista. Si la pista está ocupada, los aviones en el cielo deben esperar dando vueltas (Holdings).
*   **TPS (Tiempo de Permanencia en el Sector):** Lo que tarda un avión en cruzar de un lado a otro del sector. *Ejemplo: Cruzar el sector de Bogotá rumbo a Medellín puede tomar 12 minutos.*
*   **Separación Longitudinal:** La distancia de seguridad (medida en minutos o millas) que debe existir entre dos aviones que van por la misma ruta para evitar que la turbulencia del primero voltee al segundo (Estela Turbulenta).

---

## 3. ¿Qué es el RAC 14 y por qué es importante?

El **RAC (Reglamentos Aeronáuticos de Colombia)** es como el código de tránsito, pero para el cielo. El número **14** específicamente trata sobre los **Aeródromos** (Aeropuertos).

A nivel mundial, la OACI (Organización de Aviación Civil Internacional) impuso reglas para calcular capacidades (Doc 9689). En Colombia, la antigua *Circular 006* hacía esto con una fórmula rígida. 

**¿Qué hicimos nosotros?** 
Integramos la modernización dictada por el **RAC 14**, el cual indica que no todos los aviones son iguales ni todos los días son soleados. Por tanto, el cálculo de capacidad **no puede ser un número fijo**, debe ser *Estocástico* (una palabra técnica que significa "basado en probabilidades dinámicas").

---

## 4. Entendiendo los Cálculos Paso a Paso

El núcleo del sistema usa "Agentes Inteligentes" (pequeños cerebros de código) para hacer el cálculo. Veamos cada paso con un ejemplo fácil.

### Paso 1: El Agente Físico (Las Leyes Naturales)
Este agente mira la física de los aviones y la geografía.

*   **¿Qué calcula?** El TFC y el ROT, pero ajustados a la realidad.
*   **El Ejemplo de la Altura:** El Aeropuerto El Dorado en Bogotá está a 8,360 pies de altura (Muy alto). A esta altura, el aire es "delgado" (menos denso). Para que un avión no se caiga, tiene que aterrizar **más rápido**. Como aterriza más rápido, necesita más metros para frenar, lo que aumenta su tiempo en la pista (ROT). 
*   **¿Qué ves en el sistema?** Si el agente detecta un aeropuerto de altura (>5,000 pies), castiga el cálculo sumando un `+15%` al tiempo de separación por pura física aerodinámica.

### Paso 2: El Agente Normativo (The Compliance Officer)
Este agente revisa que no se rompan las reglas del RAC 14 basadas en la geometría del aeropuerto.

*   **El Ejemplo de las Calles de Salida:** Imagina una autopista de carros. Si para salir de ella tienes que frenar a cero y dar un giro de 90 grados, trancas a todos los de atrás. Si hay una "salida rápida" en curva suave, el tráfico fluye maravillosamente. 
*   **¿Qué hace el Agente?** Si le pides que calcule la capacidad del aeropuerto, pero el sistema sabe que van a aterrizar aviones gigantes (ej. B747) y el aeropuerto **NO** tiene calles de salida rápida, el agente penaliza el resultado bajando el puntaje de "Eficiencia". 

### Paso 3: El Motor de Simulación (El Factor Ashford y Montecarlo)
Ningún humano trabaja al 100% de su cerebro durante 8 horas seguidas sin cometer errores mortales. 

*   **Factor Ashford (Utilización):** La aviación dicta (mediante el modelo matemático de Ashford) que a un controlador se le planifica el trabajo máximo a un **80% (0.8)** de sus capacidades, reservando el 20% mental para emergencias climáticas o médicas.
*   **La Simulación de Montecarlo:** En un software antiguo, la máquina diría: *"Caben exactamente 45 vuelos por hora"*. Pero el clima cambia. Nuestro **RiskManager (Gestor de Riesgo)** tira los dados virtuales miles de veces simulando tormentas, fallas de radio y días despejados (Distribución de Gauss).
*   **¿Qué ves en el sistema?** En la pantalla no verás un "45". Verás un **Rango Probable de Incertidumbre: "Capacidad de 42 a 48 vuelos/hora"**. 

---

## 5. Interpretación de los Resultados Visibles (Dashboards)

Cuando abres la interfaz gráfica, verás gráficos llenos de colores. Aquí te explico cómo "leerlos" como un piloto experto:

### 🔴 Gráfico de Saturación de Sector (Líneas y Barras)
*   **La Línea Roja Horizontal:** Es el techo, la capacidad máxima calculada por nuestros agentes. Si la línea dice 40, el ATC no debería recibir más de 40 vuelos en esa hora.
*   **Las Barras Azules (Picos):** Es la cantidad de aviones reales o predichos por la Inteligencia Artificial (Random Forest) que van a entrar.
*   **Interpretación Operativa:** Si a las 08:00 AM la barra azul mide "35", todo está bien y seguro (verde). Si a las 18:00 PM la barra azul perfora hacia la línea roja midiendo "45", estalla la **saturación** (color rojo). 
*   **¿Para qué sirve?** El jefe de la torre mira este gráfico a primera hora de la mañana. Al ver el rojo futuro a las 18:00, llama a las aerolíneas y les cancela o retrasa vuelos unas horas antes (*Regulación de flujo*), evitando un desastre en el aire sin gasolina.

### 🟥 Gráficos de "Distribución" (Rectángulos o Treemaps)
Verás unos cuadrados grandes y pequeños agrupados por aeropuertos o regiones.
*   **Interpretación:** El tamaño del cuadrado equivale a la inyección de tráfico. Si el cuadrado de un aeropuerto es gigantesco, significa que es la arteria principal del corazón de la aviación. 
*   **¿Para qué sirve?** Para priorizar la inversión de recursos (ej. enviar a los mejores controladores a la región con el cuadrado más grande porque habrá más carga laboral).

### 🌡️ Mapas de Calor Horario (Heatmaps)
Un cuadro que cruza "Días de la semana" vs "Horas del Día". Las celdas rojas o moradas oscuras significan "Concentración Extrema de Vuelos" (*Peak Hours*).
*   **Ejemplo Real:** Es normal que veas rojo todos los viernes entre las 17:00 y las 20:00. Eso se llama un "Banco de Vuelos" corporativos cerrando semana.
*   **¿Para qué sirve?** Sirve para rotar el personal humano. Si en el mapa ves una matriz blanca brillante (cero vuelos) a las 02:00 AM un Martes, el jefe dejará solo a un controlador en turno minimizando horas extras. Y reforzará el Viernes con tres controladores en consola.

---

## Resumen Final

El **ATC Capacity & Analytics** no reemplaza al controlador aéreo humano; es su radar del futuro. Usa ciencia matemática dura (**RAC 14, Física y Probabilidad**) combinada con Inteligencia Artificial predictiva para transformar un problema invisible (la fatiga mental y las congestiones en el cielo) en gráficos interactivos que salvan vidas reales todos los días.
