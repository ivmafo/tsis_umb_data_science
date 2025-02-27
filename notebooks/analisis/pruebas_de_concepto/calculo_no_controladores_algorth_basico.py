import simpy
import random

# Parámetros de la simulación
NUM_CONTROLADORES = 3
CAPACIDAD_CONTROLADOR = 20  # Aeronaves por hora
TIEMPO_SIMULACION = 8 * 60  # Minutos (8 horas)
INTERVALO_LLEGADAS = 3  # Minutos entre llegadas de aeronaves

# Función para simular la llegada de aeronaves
def llegada_aeronaves(env, torre_control):
    while True:
        yield env.timeout(random.expovariate(1.0 / INTERVALO_LLEGADAS))
        env.process(gestionar_aeronave(env, torre_control))

# Función para simular la gestión de una aeronave
def gestionar_aeronave(env, torre_control):
    with torre_control.request() as request:
        yield request
        tiempo_gestion = random.expovariate(1.0 / CAPACIDAD_CONTROLADOR)
        yield env.timeout(tiempo_gestion)
        print(f"Aeronave gestionada a las {env.now // 60:.0f} horas y {env.now % 60:.0f} minutos")

# Configuración del entorno de simulación
env = simpy.Environment()
torre_control = simpy.Resource(env, capacity=NUM_CONTROLADORES)

# Iniciar procesos de simulación
env.process(llegada_aeronaves(env, torre_control))

# Ejecutar la simulación
env.run(until=TIEMPO_SIMULACION)