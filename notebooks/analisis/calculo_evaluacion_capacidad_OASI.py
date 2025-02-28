import random

# Parámetros de la simulación
num_pistas = 2
capacidad_por_pista = 30  # Operaciones por hora
horas_simulacion = 24
demanda_por_hora = [random.randint(20, 40) for _ in range(horas_simulacion)]

# Función para calcular la capacidad según la OACI
def calcular_capacidad_oaci(num_pistas, capacidad_por_pista, demanda_por_hora):
    capacidad_total = num_pistas * capacidad_por_pista
    operaciones_realizadas = 0
    demoras = 0

    for demanda in demanda_por_hora:
        if demanda <= capacidad_total:
            operaciones_realizadas += demanda
        else:
            operaciones_realizadas += capacidad_total
            demoras += demanda - capacidad_total

    return operaciones_realizadas, demoras

# Ejecutar la simulación
operaciones, demoras = calcular_capacidad_oaci(num_pistas, capacidad_por_pista, demanda_por_hora)
print(f"Operaciones realizadas: {operaciones}")
print(f"Demoras acumuladas: {demoras}")