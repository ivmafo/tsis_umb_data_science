# 
import psycopg2
from psycopg2.extras import RealDictCursor
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
                    INSERT INTO flights (
                        callsign, matricula, tipo_aeronave, empresa, numero_vuelo,
                        tipo_vuelo, tiempo_inicial, origen, pista_origen, sid,
                        fecha_salida, hora_salida, destino, pista_destino,
                        fecha_llegada, hora_llegada, nivel, ambito,
                        nombre_origen, nombre_destino
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    RETURNING *;
                """
                cursor.execute(query, (
                    flight.callsign,
                    flight.matricula,
                    flight.tipo_aeronave,
                    flight.empresa,
                    flight.numero_vuelo,
                    flight.tipo_vuelo,
                    flight.tiempo_inicial,
                    flight.origen,
                    flight.pista_origen,
                    flight.sid,
                    flight.fecha_salida.date(),
                    flight.fecha_salida.time(),
                    flight.destino,
                    flight.pista_destino,
                    flight.fecha_llegada.date(),
                    flight.fecha_llegada.time(),
                    flight.nivel,
                    flight.ambito,
                    flight.nombre_origen,
                    flight.nombre_destino
                ))
                result = cursor.fetchone()
                self.connection.commit()

                # Combinar fecha y hora para los campos hora_salida y hora_llegada
                result['hora_salida'] = datetime.combine(result['fecha_salida'], result['hora_salida'])
                result['hora_llegada'] = datetime.combine(result['fecha_llegada'], result['hora_llegada'])

                return Flight(**result)
        except Exception as e:
            print(f"Error al guardar el vuelo: {e}")
            raise

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




