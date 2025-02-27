import simpy
import random

# Parámetros de la simulación
NUM_PISTAS = 2
CAPACIDAD_PISTA = 30  # Operaciones por hora
TIEMPO_SIMULACION = 24 * 60  # Minutos (24 horas)
INTERVALO_LLEGADAS = 2  # Minutos entre llegadas de vuelos

# Función para simular la llegada de vuelos
def llegada_vuelos(env, aeropuerto):
    while True:
        yield env.timeout(random.expovariate(1.0 / INTERVALO_LLEGADAS))
        env.process(aterrizaje(env, aeropuerto))

# Función para simular el aterrizaje de un vuelo
def aterrizaje(env, aeropuerto):
    with aeropuerto.request() as request:
        yield request
        tiempo_aterrizaje = random.expovariate(1.0 / CAPACIDAD_PISTA)
        yield env.timeout(tiempo_aterrizaje)
        print(f"Vuelo aterrizado a las {env.now // 60:.0f} horas y {env.now % 60:.0f} minutos")

# Configuración del entorno de simulación
env = simpy.Environment()
aeropuerto = simpy.Resource(env, capacity=NUM_PISTAS)

# Iniciar procesos de simulación
env.process(llegada_vuelos(env, aeropuerto))

# Ejecutar la simulación
env.run(until=TIEMPO_SIMULACION)