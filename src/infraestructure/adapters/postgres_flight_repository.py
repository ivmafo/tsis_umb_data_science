# src/infrastructure/adapters/postgres_flight_repository.py
from domain.ports.flight_repository import FlightRepository
from domain.entities.flight import Flight
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional

class PostgresFlightRepository(FlightRepository):
    def __init__(self, connection):
        self.connection = connection

    def save(self, flight: Flight) -> Flight:
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
            return Flight(**result)

    def find_by_callsign(self, callsign: str) -> Optional[Flight]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = "SELECT * FROM flights WHERE callsign = %s;"
            cursor.execute(query, (callsign,))
            result = cursor.fetchone()
            return Flight(**result) if result else None