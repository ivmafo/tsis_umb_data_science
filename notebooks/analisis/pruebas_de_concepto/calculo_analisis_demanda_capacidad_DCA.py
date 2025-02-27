import numpy as np

# Datos de ejemplo: demanda de vuelos por hora
demanda_por_hora = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135]

# Capacidad del aeropuerto por hora
capacidad_por_hora = 600

# Función para calcular la relación demanda/capacidad
def calcular_relacion_dc(demanda, capacidad):
    relacion_dc = np.array(demanda) / capacidad
    return relacion_dc

# Calcular la relación demanda/capacidad
relacion_dc = calcular_relacion_dc(demanda_por_hora, capacidad_por_hora)

# Evaluar la capacidad del aeropuerto
def evaluar_capacidad(relacion_dc):
    if np.any(relacion_dc > 1):
        return "La demanda excede la capacidad en algunas horas."
    else:
        return "La capacidad es suficiente para la demanda."

# Resultado de la evaluación
resultado = evaluar_capacidad(relacion_dc)
print("Relación Demanda/Capacidad por hora:", relacion_dc)
print("Evaluación de la capacidad del aeropuerto:", resultado)