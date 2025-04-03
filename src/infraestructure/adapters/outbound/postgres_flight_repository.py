# src\infraestructure\adapters\outbound\postgres_flight_repository.py
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from typing import List, Optional, Dict
from src.core.ports.flight_repository import FlightRepository
from src.core.entities.flight import Flight
from src.core.dtos.flight_dtos import (
    FlightFilterDTO, 
    FlightOriginCountDTO,
    FlightDestinationCountDTO,
    FlightAirlineCountDTO,
    FlightTypeCountDTO,
    DateRangeDTO,
    FlightHourlyCountDTO
)

class PostgresFlightRepository(FlightRepository):
    """
    PostgreSQL implementation of the Flight Repository.
    
    This class handles all database operations related to flight data using PostgreSQL.
    
    Attributes:
        connection (psycopg2.extensions.connection): Database connection instance
    """

    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection

    def _execute_query(self, query: str, params=None):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params if params else ())
                return cursor.fetchall()
        except Exception as e:
            self.connection.rollback()
            print(f"Database error in _execute_query: {str(e)}")
            raise e

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
                    template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    page_size=1000
                )
                result = cursor.fetchone()
                self.connection.commit()
                return Flight(**result) if result else None

        except Exception as e:
            self.connection.rollback()
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

    def get_origins_count(self, filters: FlightFilterDTO) -> List[FlightOriginCountDTO]:
        try:
            where_clauses = []
            params = []
            
            if filters.years:
                where_clauses.append("EXTRACT(YEAR FROM fecha)::text = ANY(%s)")
                params.append(filters.years)
            
            if filters.months:
                where_clauses.append("EXTRACT(MONTH FROM fecha)::text = ANY(%s)")
                params.append(filters.months)
            
            if filters.origins:
                where_clauses.append("origen = ANY(%s)")
                params.append(filters.origins)
            
            if filters.destinations:
                where_clauses.append("destino = ANY(%s)")
                params.append(filters.destinations)
            
            if filters.flight_types:
                where_clauses.append("tipo_vuelo = ANY(%s)")
                params.append(filters.flight_types)
            
            if filters.airlines:
                where_clauses.append("empresa = ANY(%s)")
                params.append(filters.airlines)
            
            if filters.aircraft_types:
                where_clauses.append("tipo_aeronave = ANY(%s)")
                params.append(filters.aircraft_types)
            
            query = "SELECT origen as origin, COUNT(*) as count FROM fligths"
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            query += " GROUP BY origen ORDER BY count DESC"

            results = self._execute_query(query, params)
            return [FlightOriginCountDTO(origin=row['origin'], count=row['count']) for row in results]
            
        except Exception as e:
            print(f"Error in get_origins_count: {str(e)}")
            raise e

    def get_destinations_count(self, filters: FlightFilterDTO) -> List[FlightDestinationCountDTO]:
        try:
            where_clauses = []
            params = []
            
            if filters.years:
                where_clauses.append("EXTRACT(YEAR FROM fecha)::text = ANY(%s)")
                params.append(filters.years)
            
            if filters.months:
                where_clauses.append("EXTRACT(MONTH FROM fecha)::text = ANY(%s)")
                params.append(filters.months)
            
            if filters.origins:
                where_clauses.append("origen = ANY(%s)")
                params.append(filters.origins)
            
            if filters.destinations:
                where_clauses.append("destino = ANY(%s)")
                params.append(filters.destinations)
            
            if filters.flight_types:
                where_clauses.append("tipo_vuelo = ANY(%s)")
                params.append(filters.flight_types)
            
            if filters.airlines:
                where_clauses.append("empresa = ANY(%s)")
                params.append(filters.airlines)
            
            if filters.aircraft_types:
                where_clauses.append("tipo_aeronave = ANY(%s)")
                params.append(filters.aircraft_types)
            
            query = "SELECT destino as destination, COUNT(*) as count FROM fligths"
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            query += " GROUP BY destino ORDER BY count DESC"

            results = self._execute_query(query, params)
            return [FlightDestinationCountDTO(destination=row['destination'], count=row['count']) for row in results]
            
        except Exception as e:
            print(f"Error in get_destinations_count: {str(e)}")
            raise e

    def get_airlines_count(self, filters: FlightFilterDTO) -> List[FlightAirlineCountDTO]:
            try:
                where_clauses = []
                params = []
                
                if filters.years:
                    where_clauses.append("EXTRACT(YEAR FROM fecha)::text = ANY(%s)")
                    params.append(filters.years)
                
                if filters.months:
                    where_clauses.append("EXTRACT(MONTH FROM fecha)::text = ANY(%s)")
                    params.append(filters.months)
                
                if filters.origins:
                    where_clauses.append("origen = ANY(%s)")
                    params.append(filters.origins)
                
                if filters.destinations:
                    where_clauses.append("destino = ANY(%s)")
                    params.append(filters.destinations)
                
                if filters.flight_types:
                    where_clauses.append("tipo_vuelo = ANY(%s)")
                    params.append(filters.flight_types)
                
                if filters.airlines:
                    where_clauses.append("empresa = ANY(%s)")
                    params.append(filters.airlines)
                
                if filters.aircraft_types:
                    where_clauses.append("tipo_aeronave = ANY(%s)")
                    params.append(filters.aircraft_types)
                

    
                # Modified query to handle NULL values
                query = """
                    SELECT 
                        COALESCE(empresa, 'Unknown') as airline,
                        COUNT(*) as count 
                    FROM fligths
                """
                
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
                
                query += " GROUP BY empresa ORDER BY count DESC"
    
                results = self._execute_query(query, params)
                return [
                    FlightAirlineCountDTO(
                        airline=row['airline'] if row['airline'] else 'Unknown',
                        count=row['count']
                    ) 
                    for row in results
                ]
                
            except Exception as e:
                print(f"Error in get_airlines_count: {str(e)}")
                raise e

    def get_flight_types_count(self, filters: FlightFilterDTO) -> List[FlightTypeCountDTO]:
            try:
                where_clauses = []
                params = []
                
                if filters.years:
                    where_clauses.append("EXTRACT(YEAR FROM fecha)::text = ANY(%s)")
                    params.append(filters.years)
                
                if filters.months:
                    where_clauses.append("EXTRACT(MONTH FROM fecha)::text = ANY(%s)")
                    params.append(filters.months)
                
                if filters.origins:
                    where_clauses.append("origen = ANY(%s)")
                    params.append(filters.origins)
                
                if filters.destinations:
                    where_clauses.append("destino = ANY(%s)")
                    params.append(filters.destinations)
                
                if filters.flight_types:
                    where_clauses.append("tipo_vuelo = ANY(%s)")
                    params.append(filters.flight_types)
                
                if filters.airlines:
                    where_clauses.append("empresa = ANY(%s)")
                    params.append(filters.airlines)
                
                if filters.aircraft_types:
                    where_clauses.append("tipo_aeronave = ANY(%s)")
                    params.append(filters.aircraft_types)
                
   
                query = """
                    SELECT 
                        COALESCE(tipo_vuelo, 'Unknown') as flight_type,
                        COUNT(*) as count 
                    FROM fligths
                """
                
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
                
                query += " GROUP BY tipo_vuelo ORDER BY count DESC"
    
                results = self._execute_query(query, params)
                return [
                    FlightTypeCountDTO(
                        flight_type=row['flight_type'] if row['flight_type'] else 'Unknown',
                        count=row['count']
                    ) 
                    for row in results
                ]
                
            except Exception as e:
                print(f"Error in get_flight_types_count: {str(e)}")
                raise e

    def get_hourly_counts_by_date_ranges(self, date_ranges: List[DateRangeDTO], airport: Optional[str] = None) -> List[FlightHourlyCountDTO]:
        """
        Get hourly flight counts for specified date ranges and origin airport.
        
        Args:
            date_ranges (List[DateRangeDTO]): List of date ranges to analyze
            airport (Optional[str]): Origin airport code to filter by
            
        Returns:
            List[FlightHourlyCountDTO]: Hourly flight counts for each date range
            
        Raises:
            Exception: If there's an error executing the query
        """
        try:
            if not date_ranges:
                return []

            airport_condition = "AND origen = %s" if airport else ""
            query = """
            WITH RECURSIVE hours AS (
                SELECT generate_series(0, 23) AS hour
            ),
            date_ranges AS (
                SELECT 
                    id as range_id,
                    label,
                    start_date::date, 
                    end_date::date
                FROM unnest(%s::int[], %s::text[], %s::date[], %s::date[]) 
                AS dr(id, label, start_date, end_date)
            ),
            flight_counts AS (
                SELECT 
                    date_part('hour', hora_salida)::int AS hour,
                    dr.label,
                    COUNT(*) AS flight_count
                FROM fligths f
                CROSS JOIN date_ranges dr
                WHERE f.fecha_salida::date BETWEEN dr.start_date AND dr.end_date
                """ + airport_condition + """
                GROUP BY date_part('hour', hora_salida), dr.label
            )
            SELECT 
                h.hour,
                json_object_agg(
                    COALESCE(fc.label, 'sin_datos'),
                    COALESCE(fc.flight_count, 0)
                ) as counts
            FROM hours h
            LEFT JOIN flight_counts fc ON h.hour = fc.hour
            GROUP BY h.hour
            ORDER BY h.hour;
            """
            
            range_ids = [r.id for r in date_ranges]
            labels = [r.label for r in date_ranges]
            start_dates = [r.start_date for r in date_ranges]
            end_dates = [r.end_date for r in date_ranges]
            
            params = [range_ids, labels, start_dates, end_dates]
            if airport:
                params.append(airport)

            results = self._execute_query(query, tuple(params))
            
            return [
                FlightHourlyCountDTO(
                    hour=row['hour'],
                    counts=row['counts'] if row['counts'] else {}
                )
                for row in results
            ]
        except Exception as e:
            print(f"Error in get_hourly_counts_by_date_ranges: {str(e)}")
            return [FlightHourlyCountDTO(hour=h, counts={}) for h in range(24)]

    def get_hourly_counts_by_date_ranges_destination(self, date_ranges: List[DateRangeDTO], airport: Optional[str] = None) -> List[FlightHourlyCountDTO]:
        """
        Get hourly flight counts for specified date ranges and destination airport.
        
        Args:
            date_ranges (List[DateRangeDTO]): List of date ranges to analyze
            airport (Optional[str]): Destination airport code to filter by
            
        Returns:
            List[FlightHourlyCountDTO]: Hourly flight counts for each date range
            
        Raises:
            Exception: If there's an error executing the query
        """
        try:
            if not date_ranges:
                return []

            airport_condition = "AND destino = %s" if airport else ""
            query = """
            WITH RECURSIVE hours AS (
                SELECT generate_series(0, 23) AS hour
            ),
            date_ranges AS (
                SELECT 
                    id as range_id,
                    label,
                    start_date::date, 
                    end_date::date
                FROM unnest(%s::int[], %s::text[], %s::date[], %s::date[]) 
                AS dr(id, label, start_date, end_date)
            ),
            flight_counts AS (
                SELECT 
                    date_part('hour', hora_llegada)::int AS hour,
                    dr.label,
                    COUNT(*) AS flight_count
                FROM fligths f
                CROSS JOIN date_ranges dr
                WHERE f.fecha_llegada::date BETWEEN dr.start_date AND dr.end_date
                """ + airport_condition + """
                GROUP BY date_part('hour', hora_llegada), dr.label
            )
            SELECT 
                h.hour,
                json_object_agg(
                    COALESCE(fc.label, 'sin_datos'),
                    COALESCE(fc.flight_count, 0)
                ) as counts
            FROM hours h
            LEFT JOIN flight_counts fc ON h.hour = fc.hour
            GROUP BY h.hour
            ORDER BY h.hour;
            """
            
            range_ids = [r.id for r in date_ranges]
            labels = [r.label for r in date_ranges]
            start_dates = [r.start_date for r in date_ranges]
            end_dates = [r.end_date for r in date_ranges]
            
            params = [range_ids, labels, start_dates, end_dates]
            if airport:
                params.append(airport)

            results = self._execute_query(query, tuple(params))
            
            return [
                FlightHourlyCountDTO(
                    hour=row['hour'],
                    counts=row['counts'] if row['counts'] else {}
                )
                for row in results
            ]
        except Exception as e:
            print(f"Error in get_hourly_counts_by_date_ranges_destination: {str(e)}")

    