# 🤖 Manual de Agentes Inteligentes (RAC 14 Estocástico)

Este documento detalla exhaustivamente la nueva arquitectura orientada a agentes incluida en el directorio `src/domain/agents` y su contraparte en la interfaz visual interactiva. 

---

## 🏗️ 1. Lógica del Sistema: De Determinista a Estocástico

Anteriormente, el cálculo de capacidad (legacy Circular 006) utilizaba una **fórmula estática y determinista**: $C = U / (t_{occ} \cdot 1.10)$. 
Sin embargo, el espacio aéreo real es altamente dinámico y sujeto a múltiples variables (clima, fatiga de controladores, tipos de aviones). El nuevo módulo RAC 14 soluciona esto introduciendo un ensamble de **Agentes Inteligentes** coordinados por un `BackendAgent`.

### 🧠 1.1 El Orquestador: `BackendAgent` 
*Archivo: `src/application/use_cases/backend_agent.py`*

**Teoría Estructural**: En modelación multi-agente, un "Orquestador" es necesario para construir el contexto histórico antes de inyectarlo a los agentes autónomos especialistas. Su única tarea es recuperar los Tiempos de Permanencia en el Sector (TPS), hallar los aeropuertos adyacentes y ensamblar las piezas.

**¿Qué hace el código?**  
El método `execute_dynamic_capacity_calculation` consulta la base de datos (Legacy) para hallar el TFC nominal. Luego insta a la tríada de agentes a ejecutar sus cálculos y toma la decisión dictatorial final con base en las recomendaciones de sus "subordinados":
```python
# Fragmento del paso por cada Aeropuerto en el Sector
for ap in airports_entities:
    # 1. Agente Normativo evalúa riesgos
    officer = ComplianceOfficer(airport=ap)
    compliance_observations.extend(officer.validate_rac14_compliance())
    
    # 2. Agente Físico calcula el impacto cinemático de TFC y ROT
    phys = Physicist(airport=ap)
    ap_tfc, ap_sep = phys.calculate_dynamic_tfc(base_tfc, base_separation)
    ap_rot = phys.estimate_dynamic_rot()
```


### 📐 1.2 Agente Físico: `Physicist` 
*Archivo: `src/domain/agents/physicist.py`*

**Teoría Matemática y Física (Mínimos OACI Doc 4444 y Doc 9157)**: 
A mayor elevación, la *Densidad Acústica del Aire* es menor. Esto requiere que las aeronaves mantengan una mayor Velocidad Verdadera (True Airspeed - TAS) para sustentar el vuelo. Una mayor TAS incrementa la distancia horizontal recorrida en relación a la inercia, requiriendo mayor distancia de *separación en vuelo* y mayor distancia de *frenado en pista*. Adicionalmente, ciertas maniobras infraestructurales consumen preciados segundos de ocupación (Backtrack).

**¿Qué hace el código?**  
El agente inspecciona los atributos geofísicos e infraestructurales del aeropuerto. Si la elevación supera 5,000 pies, aplica un **+15% de penalización algorítmica** sobre el Tiempo de Funciones de Control y el Tiempo de Separación. Además, proyecta dinámicamente el *Runway Occupancy Time (ROT)* (tiempo usado de la pista).
```python
# Cálculo Matemático del ROT estresado
base_rot = 50.0  # Segundos ideales
if self.airport.requires_backtrack:
    base_rot += 120.0  # Penalización: Maniobra 180° suma 2 minutos muertos
if not self.airport.has_rapid_exit_taxiway:
    base_rot += 15.0   # Penalización: Salida predeterminada 90°
if self.airport.is_high_altitude:
    base_rot *= 1.10   # Elevación superior a 5000ft penaliza +10% de frenado
```
*Impacto*: Al concluir, si el tiempo de uso en pista (ROT) es mayor que el TFC nominal de espacio aéreo, el componente aéreo no puede arrojar más vuelos a la terminal. El sistema asume que la capacidad está ahora limitada por tierra.

### ⚖️ 1.3 Agente Normativo: `ComplianceOfficer` 
*Archivo: `src/domain/agents/compliance_officer.py`*

**Teoría de Seguridad Operacional (OACI Doc 4444 PANS-ATM / RAC 14 / Doc 9157)**: 
Las fórmulas de física puras no consideran el alto sesgo hacia la seguridad pasiva. No basta con que quepan los aviones en un tubo físico de espacio aéreo; deben caber *cumpliendo las reglas de separación civil*.

**¿Qué hace el código?**  
La regla `validate_rac14_compliance` cruza el "Código de Referencia" OACI de máxima aeronave del aeropuerto (ej. E o F para el B747/A380) y evalúa si su geometría lo aprueba. Emite penalizaciones ("warnings" y de-ratings) si detecta inconsistencias críticas:
```python
# Evaluación Geométrica del Compliance Officer
code_letter = self.airport.reference_code[-1]
if code_letter in ["E", "F"] and not self.airport.has_rapid_exit_taxiway:
    warnings.append("RAC-14 Observación: Aeronaves pesadas sin Calle Salida Rápida.")
```
Estos mensajes son directamente entregados a la interfaz UI (dashboard) para que el ATC sepa por qué le asignaron una capacidad horaria reducida.


### 🎲 1.4 Motor Probabilístico: `RiskManager` 
*Archivo: `src/domain/agents/risk_manager.py`*

**Teoría Estadística (Montecarlo Estocástico y Factor Ashford)**:
El factor *Ashford (Utilization Factor)* indica que un controlador no debe exceder de $\approx 80\%$ (valor 0.8) la teoría óptima por efectos de fatiga (descansos fisiológicos requeridos), y asimetría de picos.
En el mundo rígido esto dejaría un número fijo. Pero la Teoría Probabilística dictamina que un clima perfecto o fallas de radar en un día de LVP (*Low Visibility Procedures*) generan un rango de dispersión.

**¿Qué hace el código?**  
`simulate_stochastic_capacity` crea una Campana de Gauss ($\sigma$). Construye la media ajustada (baseline_capacity) e inyecta hasta un $10\%$ de varianza estadística ($\pm 1.5$ de desviación estándar por ley empírica de seguridad al $95\%$ de confianza en el límite de densidad probabilística).
```python
# Se toma la Capacidad Horaria Teórica del Physicist y aplicamos factor Ashford
baseline_capacity = nominal_ch * self.utilization_factor  # Ej. 100 * 0.8 = 80 vuelos

std_dev = baseline_capacity * 0.10  # Varianza de 10%

# Se definen las colas inferior (tormenta) y superior (día perfecto) al 95% 
lower_bound = baseline_capacity - (std_dev * 1.5)
upper_bound = min(nominal_ch, baseline_capacity + (std_dev * 1.5))

# El sistema entrega un muestreo aleatorizado dentro de esta distribución:
simulated_ch = random.gauss(baseline_capacity, std_dev)
```

---

## 💻 2. Vistas Frontend y el Tablero Interactivo

El núcleo RAC 14 sería inútil si la presentación es confusa. Esto se gestiona en **`web/src/views/CapacityReportView.tsx`**.

### 🎮 El Componente Contralor:
La vista se divide en un *Layout Split*. Cuando el usuario oprime el botón maestro:
`const res = await api.post(/sectors/${selectedSector}/calculate)`
La inferencia se desencadena de ida y vuelta.

### 📊 ¿Qué Significa para el Usuario (el Tablero Final)?

1. **El Valor Central del Límite Operativo**
   - El tablero estocástico dejará de mostrar un rígido **"Mínimo 44, Máximo 44"**. Ahora mostrará la media gaussiana penalizada: **"Capacidad 38 vuelos/hr"**.
   - **Rango de Tolerancia ($95\%$ Error)**: El dashboard ilumina una banda de incertidumbre: *[35 vuelos/hr con LVP severo, a 42 en condiciones VFR]*. Esto otorga un margen de control real al Supervisor.

2. **Diagnóstico Físico (`PhysicistMetrics`)**
   - Los datos del `Physicist` impactan la UI arrojando si la saturación está provocada por el Tiempo Aéreo (TFC) o si un `Backtrack` en un aeropuerto secundario forzó un cuello de botella normativo (ROT Limitante).
   
3. **Paz y Auditoría (Contraste Legacy)**
   - Un usuario del Estado (Aerocivil) que vea esto podría asustarse frente a tanto algoritmo predictivo. Por tanto, el *Compliance Officer* anexa en la UI la Métrica Antigua de la Circular 006 para demostrar correlación directa de la seguridad: la Estocástica siempre tiene una tolerancia más humana y rigurosa que la Circular estricta.
