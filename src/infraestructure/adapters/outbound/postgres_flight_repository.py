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

    def get_distinct_years(self) -> list:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT DISTINCT EXTRACT(YEAR FROM fecha) as year 
                    FROM fligths 
                    WHERE fecha IS NOT NULL 
                    ORDER BY year DESC;
                """
                cursor.execute(query)
                return [int(row['year']) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting distinct years: {e}")
            return []

    def get_distinct_months(self) -> list:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT DISTINCT EXTRACT(MONTH FROM fecha)::integer as month 
                    FROM fligths 
                    WHERE fecha IS NOT NULL 
                    ORDER BY month;
                """
                cursor.execute(query)
                months = [row['month'] for row in cursor.fetchall()]
                return months
        except Exception as e:
            print(f"Error getting distinct months: {e}")
            return []

    def get_distinct_origins(self) -> list:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT DISTINCT origen 
                    FROM fligths 
                    WHERE origen IS NOT NULL AND origen != ''
                    ORDER BY origen;
                """
                cursor.execute(query)
                origins = [row['origen'] for row in cursor.fetchall()]
                return origins
        except Exception as e:
            print(f"Error getting distinct origins: {e}")
            return []

    def get_distinct_destinations(self) -> list:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT DISTINCT destino 
                    FROM fligths 
                    WHERE destino IS NOT NULL AND destino != ''
                    ORDER BY destino;
                """
                cursor.execute(query)
                destinations = [row['destino'] for row in cursor.fetchall()]
                return destinations
        except Exception as e:
            print(f"Error getting distinct destinations: {e}")
            return []

    def get_distinct_flight_types(self) -> list:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT DISTINCT tipo_vuelo 
                    FROM fligths 
                    WHERE tipo_vuelo IS NOT NULL AND tipo_vuelo != ''
                    ORDER BY tipo_vuelo;
                """
                cursor.execute(query)
                return [row['tipo_vuelo'] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting distinct flight types: {e}")
            return []

    def get_distinct_airlines(self) -> list:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT DISTINCT empresa 
                    FROM fligths 
                    WHERE empresa IS NOT NULL 
                    AND empresa != '' 
                    ORDER BY empresa;
                """
                cursor.execute(query)
                return [row['empresa'] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting distinct airlines: {e}")
            return []

    def get_distinct_aircraft_types(self) -> list:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT DISTINCT tipo_aeronave 
                    FROM fligths 
                    WHERE tipo_aeronave IS NOT NULL 
                    AND tipo_aeronave != '' 
                    ORDER BY tipo_aeronave;
                """
                cursor.execute(query)
                return [row['tipo_aeronave'] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting distinct aircraft types: {e}")
            return []




