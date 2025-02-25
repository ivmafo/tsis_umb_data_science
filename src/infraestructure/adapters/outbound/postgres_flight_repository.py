# src\infraestructure\adapters\outbound\postgres_flight_repository.py
import psycopg2
from psycopg2.extras import RealDictCursor  , execute_values
from src.core.ports.flight_repository import FlightRepository
from src.core.entities.flight import Flight
from typing import Optional
from datetime import datetime




class PostgresFlightRepository(FlightRepository):
    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection

    def save(self, flight: Flight) -> Flight:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    INSERT INTO 
                    public.fligths (
                        fecha, sid, ssr, callsign, matricula,
                        tipo_aeronave, empresa, numero_vuelo,
                        tipo_vuelo, tiempo_inicial, origen,
                        fecha_salida, hora_salida, hora_pv, destino,
                        fecha_llegada, hora_llegada, nivel, duracion, distancia, velocidad, eq_ssr,
                        nombre_origen, nombre_destino,fecha_registro
                    ) VALUES %s
                                           
                                   
                                   
                                       
                                                   
                                  
                     
                    RETURNING *;
                """
                
                # Convertir el vuelo a tupla de valores
                values = [(
                    flight.fecha, flight.sid, flight.ssr, flight.callsign,
                    flight.matricula, flight.tipo_aeronave, flight.empresa,
                    flight.numero_vuelo, flight.tipo_vuelo, flight.tiempo_inicial,
                    flight.origen, flight.fecha_salida, flight.hora_salida,
                    flight.hora_pv, flight.destino, flight.fecha_llegada,
                    flight.hora_llegada, flight.nivel, flight.duracion,
                    flight.distancia, flight.velocidad, flight.eq_ssr,
                    flight.nombre_origen, flight.nombre_destino, flight.fecha_registro
                )]

                # Usar execute_values con template específico
                execute_values(
                    cursor, 
                    query, 
                    values,
                    template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    page_size=1000
                )
                result = cursor.fetchone()
                self.connection.commit()
                return Flight(**result) if result else None

        except Exception as e:
            self.connection.rollback()
            print(f"Error al guardar el vuelo: {e}")
            raise

    '''
                cursor.execute(query, (
                    flight.fecha,
                    flight.sid,
                    flight.ssr,
                    flight.callsign,
                    flight.matricula,
                    flight.tipo_aeronave,
                    flight.empresa,
                    flight.numero_vuelo,
                    flight.tipo_vuelo,
                    flight.tiempo_inicial,
                    flight.origen,
                    flight.fecha_salida,
                    flight.hora_salida,
                    flight.hora_pv,
                    flight.destino,
                    flight.fecha_llegada,
                    flight.hora_llegada,                    
                    flight.nivel,
                    flight.duracion,
                    flight.distancia,
                    flight.velocidad,
                    flight.eq_ssr,
                    flight.nombre_origen,
                    flight.nombre_destino,
                    flight.fecha_registro
                ))
                result = cursor.fetchone()
                self.connection.commit()
                
                # Combinar fecha y hora para los campos hora_salida y hora_llegada
                #result['hora_salida'] = datetime.combine(result['fecha_salida'], result['hora_salida'])
                #result['hora_llegada'] = datetime.combine(result['fecha_llegada'], result['hora_llegada'])

                return Flight(**result)
        except Exception as e:
            print(f"EEEEEEError al guardar el vuelo: {e}")
            return None
    '''

    def find_by_id(self, flight_id: str) -> Optional[Flight]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT * FROM flights WHERE id = %s;"
                cursor.execute(query, (flight_id,))
                result = cursor.fetchone()

                if result:
                    # Combinar fecha y hora para los campos hora_salida y hora_llegada
                    result['hora_salida'] = datetime.combine(result['fecha_salida'], result['hora_salida'])
                    result['hora_llegada'] = datetime.combine(result['fecha_llegada'], result['hora_llegada'])

                return Flight(**result) if result else None
        except Exception as e:
            print(f"Error al encontrar el vuelo: {e}")
            return None

    def find_by_callsign(self, callsign: str) -> Optional[Flight]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT * FROM flights WHERE callsign = %s;"
                cursor.execute(query, (callsign,))
                result = cursor.fetchone()

                if result:
                    # Combinar fecha y hora para los campos hora_salida y hora_llegada
                    result['hora_salida'] = datetime.combine(result['fecha_salida'], result['hora_salida'])
                    result['hora_llegada'] = datetime.combine(result['fecha_llegada'], result['hora_llegada'])

                return Flight(**result) if result else None
        except Exception as e:
            print(f"Error al encontrar el vuelo: {e}")
            return None




