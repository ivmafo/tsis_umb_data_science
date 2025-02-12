#import os
#from pathlib import Path
#from datetime import datetime
from infraestructure.config.database import PostgresConnectionPool
from src.infraestructure.adapters.outbound.postgres_flight_repository import PostgresFlightRepository
#from application.use_cases.create_flight import CreateFlightUseCase
#from application.use_cases.process_flights_from_excel import ProcessFlightsFromExcelUseCase


# Configurar el pool de conexiones
pool = PostgresConnectionPool()
conn = pool.get_connection()

# Inicializar repositorio y caso de uso
flight_repo = PostgresFlightRepository(conn)


# Liberar recursos
pool.release_connection(conn)
pool.close_all_connections()

'''
###############################################################################
###############################################################################
###################### TEST ###################################################
###############################################################################
###############################################################################
# prueba unitaria de creacion de vuelo
create_flight_uc = CreateFlightUseCase(flight_repo)

# Crear un vuelo de ejemplo
new_flight = create_flight_uc.execute({
    "callsign": "AVA101",
    "matricula": "HK-4567",
    "tipo_aeronave": "Boeing 737",
    "empresa": "Avianca",
    "numero_vuelo": "101",
    "tipo_vuelo": "Comercial",
    "tiempo_inicial": datetime(2023, 1, 1, 8, 0),
    "origen": "SKRG",
    "pista_origen": "01L",
    "sid": "GEMPA1",
    "fecha_salida": datetime(2023, 1, 1, 8, 15),
    "hora_salida": datetime(2023, 1, 1, 8, 15),
    "destino": "SKBO",
    "pista_destino": "19R",
    "fecha_llegada": datetime(2023, 1, 1, 9, 30),
    "hora_llegada": datetime(2023, 1, 1, 9, 30),
    "nivel": "FL350",
    "ambito": "Nacional",
    "nombre_origen": "Aeropuerto José María Córdova",
    "nombre_destino": "Aeropuerto El Dorado"
})

print(f"Vuelo creado: {new_flight}")

###############################################################################
###############################################################################
###################### TEST ###################################################
###############################################################################
###############################################################################
*/
'''

