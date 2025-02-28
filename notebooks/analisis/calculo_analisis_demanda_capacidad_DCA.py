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

def calcular_factor_disponibilidad_controlador(self, tiempo_trabajo, tiempo_descanso, num_controladores):
    """
    Calcula el Factor de Disponibilidad del Controlador (F)
    
    Parámetros:
    tiempo_trabajo: minutos efectivos de trabajo por hora
    tiempo_descanso: minutos de descanso requeridos
    num_controladores: número de controladores disponibles
    """
    tiempo_total = 60  # minutos por hora
    tiempo_efectivo = (tiempo_trabajo - tiempo_descanso) * num_controladores
    factor_disponibilidad = tiempo_efectivo / tiempo_total
    
    return min(factor_disponibilidad, 1.0)  # El factor no puede ser mayor que 1

# Ejemplo de uso
tiempo_trabajo = 50  # minutos de trabajo por hora
tiempo_descanso = 10  # minutos de descanso requeridos
num_controladores = 2  # número de controladores
factor_F = calcular_factor_disponibilidad_controlador(tiempo_trabajo, tiempo_descanso, num_controladores)
print(f"Factor de Disponibilidad del Controlador (F): {factor_F:.2f}")