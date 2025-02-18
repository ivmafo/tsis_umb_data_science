# Definir las configuraciones de pistas y condiciones meteorológicas
configuraciones_pistas = {
    "paralelas": 30,  # Capacidad en operaciones por hora por pista en condiciones VFR
    "cruzadas": 20    # Capacidad en operaciones por hora por pista en condiciones VFR
}

condiciones_meteorologicas = {
    "VFR": 1.0,  # Factor de capacidad para condiciones visuales
    "IFR": 0.67  # Factor de capacidad para condiciones instrumentales
}

# Función para calcular la capacidad del aeropuerto
def calcular_capacidad(num_pistas, tipo_pistas, condiciones):
    capacidad_base = configuraciones_pistas[tipo_pistas] * num_pistas
    factor_condiciones = condiciones_meteorologicas[condiciones]
    capacidad_total = capacidad_base * factor_condiciones
    return capacidad_total

# Ejemplo de uso
num_pistas = 2
tipo_pistas = "paralelas"
condiciones = "IFR"

capacidad = calcular_capacidad(num_pistas, tipo_pistas, condiciones)
print(f"La capacidad del aeropuerto es de {capacidad} operaciones por hora bajo condiciones {condiciones}.")