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
                results = cursor.fetchall()
                return results
        except Exception as e:
            print(f"Database error in _execute_query: {str(e)}")
            self.connection.rollback()  # Add explicit rollback
            raise

    def save(self, flight_data):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                columns = [
                    'fecha', 'sid', 'ssr', 'callsign', 'matricula', 'tipo_aeronave',
                    'empresa', 'numero_vuelo', 'tipo_vuelo', 'tiempo_inicial', 'origen',
                    'fecha_salida', 'hora_salida', 'hora_pv', 'destino', 'fecha_llegada',
                    'hora_llegada', 'nivel', 'duracion', 'distancia', 'velocidad',
                    'eq_ssr', 'nombre_origen', 'nombre_destino', 'fecha_registro'
                ]
    
                # Convert input to list if it's not already
                fligths = flight_data if isinstance(flight_data, list) else [flight_data]
                
                values = []
                batch_size = 1000
                
                for flight in fligths:
                    # Convert Flight object to dict if necessary
                    if hasattr(flight, '__dict__'):
                        flight_dict = flight.__dict__
                    elif isinstance(flight, dict):
                        flight_dict = flight
                    else:
                        print(f"Warning: Invalid flight data type: {type(flight)}")
                        continue
                        
                    value_tuple = tuple(flight_dict.get(col) for col in columns)
                    values.append(value_tuple)
                    
                    if len(values) >= batch_size:
                        execute_values(
                            cursor,
                            f"""
                            INSERT INTO fligths ({', '.join(columns)})
                            VALUES %s
                            """,
                            values
                        )
                        values = []
                    
                # Insert remaining records
                if values:
                    execute_values(
                        cursor,
                        f"""
                        INSERT INTO fligths ({', '.join(columns)})
                        VALUES %s
                        """,
                        values
                    )
                
                self.connection.commit()
                return flight_data
        except Exception as e:
            self.connection.rollback()
            print(f"Error saving fligths: {str(e)}")
            raise

    def find_by_id(self, flight_id: str) -> Optional[Flight]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT * FROM fligths WHERE id = %s;"
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
                query = "SELECT * FROM fligths WHERE callsign = %s;"
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

    def get_years(self) -> List[int]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT DISTINCT EXTRACT(YEAR FROM fecha)::integer as year 
                FROM fligths 
                ORDER BY year
            """)
            return [row['year'] for row in cursor.fetchall()]

    def get_months(self) -> List[int]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT DISTINCT EXTRACT(MONTH FROM fecha)::integer as month 
                FROM fligths 
                ORDER BY month
            """)
            return [row['month'] for row in cursor.fetchall()]

    def get_origins(self) -> List[str]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT DISTINCT origen 
                FROM fligths 
                WHERE origen IS NOT NULL 
                ORDER BY origen
            """)
            return [row['origen'] for row in cursor.fetchall()]

    def get_destinations(self) -> List[str]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT DISTINCT destino 
                FROM fligths 
                WHERE destino IS NOT NULL 
                ORDER BY destino
            """)
            return [row['destino'] for row in cursor.fetchall()]

    def get_aircraft_types(self) -> List[str]:
        """
        Get list of distinct aircraft types. This is an alias for get_distinct_aircraft_types
        to maintain compatibility with the API.
        """
        return self.get_distinct_aircraft_types()

    def get_airlines(self) -> List[str]:
        try:
            query = """
                SELECT DISTINCT empresa 
                FROM fligths 
                WHERE empresa IS NOT NULL 
                AND empresa != '' 
                ORDER BY empresa
            """
            results = self._execute_query(query)
            return [row['empresa'] for row in results]
        except Exception as e:
            print(f"Error in get_airlines: {str(e)}")
            self.connection.rollback()
            return []

    def get_distinct_years(self) -> List[int]:
        try:
            query = """
                SELECT DISTINCT EXTRACT(YEAR FROM fecha)::integer as year 
                FROM fligths 
                ORDER BY year
            """
            results = self._execute_query(query)
            return [row['year'] for row in results]
        except Exception as e:
            print(f"Error in get_distinct_years: {str(e)}")
            self.connection.rollback()
            return []

    def get_distinct_months(self) -> List[int]:
        try:
            query = """
                SELECT DISTINCT EXTRACT(MONTH FROM fecha)::integer as month 
                FROM fligths 
                ORDER BY month
            """
            results = self._execute_query(query)
            return [row['month'] for row in results]
        except Exception as e:
            print(f"Error in get_distinct_months: {str(e)}")
            self.connection.rollback()
            return []

    def get_distinct_origins(self) -> List[str]:
        try:
            query = """
                SELECT DISTINCT origen 
                FROM fligths 
                WHERE origen IS NOT NULL 
                AND origen != '' 
                ORDER BY origen
            """
            results = self._execute_query(query)
            return [row['origen'] for row in results]
        except Exception as e:
            print(f"Error in get_distinct_origins: {str(e)}")
            self.connection.rollback()
            return []

    def get_distinct_destinations(self) -> List[str]:
        try:
            query = """
                SELECT DISTINCT destino 
                FROM fligths 
                WHERE destino IS NOT NULL 
                AND destino != '' 
                ORDER BY destino
            """
            results = self._execute_query(query)
            return [row['destino'] for row in results]
        except Exception as e:
            print(f"Error in get_distinct_destinations: {str(e)}")
            self.connection.rollback()
            return []

    def get_distinct_airlines(self) -> List[str]:
        try:
            query = """
                SELECT DISTINCT empresa 
                FROM fligths 
                WHERE empresa IS NOT NULL 
                AND empresa != '' 
                ORDER BY empresa
            """
            results = self._execute_query(query)
            return [row['empresa'] for row in results]
        except Exception as e:
            print(f"Error in get_distinct_airlines: {str(e)}")
            self.connection.rollback()
            return []

    def get_distinct_flight_types(self) -> List[str]:
        try:
            query = """
                SELECT DISTINCT tipo_vuelo 
                FROM fligths 
                WHERE tipo_vuelo IS NOT NULL 
                AND tipo_vuelo != '' 
                ORDER BY tipo_vuelo
            """
            results = self._execute_query(query)
            return [row['tipo_vuelo'] for row in results]
        except Exception as e:
            print(f"Error in get_distinct_flight_types: {str(e)}")
            self.connection.rollback()
            return []

    def get_distinct_aircraft_types(self) -> List[str]:
        try:
            query = """
                SELECT DISTINCT tipo_aeronave 
                FROM fligths 
                WHERE tipo_aeronave IS NOT NULL 
                AND tipo_aeronave != '' 
                ORDER BY tipo_aeronave
            """
            results = self._execute_query(query)
            return [row['tipo_aeronave'] for row in results]
        except Exception as e:
            print(f"Error in get_distinct_aircraft_types: {str(e)}")
            self.connection.rollback()
            return []

    def get_origins_count(self, filters: Optional[FlightFilterDTO] = None) -> List[FlightOriginCountDTO]:
        try:
            where_clauses = []
            params = []
            
            if filters:
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
                    COALESCE(origen, 'Unknown') as origin,
                    COUNT(*) as count 
                FROM fligths
            """
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            query += " GROUP BY origen ORDER BY count DESC"

            results = self._execute_query(query, params)
            return [
                FlightOriginCountDTO(
                    origin=row['origin'],
                    count=row['count']
                ) 
                for row in results
            ]
        except Exception as e:
            print(f"Error in get_origins_count: {str(e)}")
            self.connection.rollback()
            raise

    def get_destinations_count(self, filters: Optional[FlightFilterDTO] = None) -> List[FlightDestinationCountDTO]:
        try:
            where_clauses = []
            params = []
            
            if filters:
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
                    COALESCE(destino, 'Unknown') as destination,
                    COUNT(*) as count 
                FROM fligths
            """
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            query += " GROUP BY destino ORDER BY count DESC"

            results = self._execute_query(query, params)
            return [
                FlightDestinationCountDTO(
                    destination=row['destination'],
                    count=row['count']
                ) 
                for row in results
            ]
        except Exception as e:
            print(f"Error in get_destinations_count: {str(e)}")
            self.connection.rollback()
            raise

    def get_airlines_count(self, filters: Optional[FlightFilterDTO] = None) -> List[FlightAirlineCountDTO]:
        try:
            where_clauses = []
            params = []
            
            if filters:
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
            self.connection.rollback()
            raise

    def get_flight_types(self) -> List[str]:
        try:
            query = """
                SELECT DISTINCT tipo_vuelo 
                FROM fligths 
                WHERE tipo_vuelo IS NOT NULL 
                AND tipo_vuelo != '' 
                ORDER BY tipo_vuelo
            """
            results = self._execute_query(query)
            return [row['tipo_vuelo'] for row in results]
        except Exception as e:
            print(f"Error in get_flight_types: {str(e)}")
            self.connection.rollback()
            return []

    def get_flight_types_count(self, filters: FlightFilterDTO) -> List[FlightTypeCountDTO]:
        try:
            where_clauses = []
            params = []
            
            # Existing filters
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
            
            # Add level_min and level_max filters
            if hasattr(filters, 'level_min') and filters.level_min is not None:
                where_clauses.append("nivel::integer >= %s")
                params.append(filters.level_min)
                
            if hasattr(filters, 'level_max') and filters.level_max is not None:
                where_clauses.append("nivel::integer <= %s")
                params.append(filters.level_max)
            
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

    def get_hourly_counts_by_date_ranges(self, date_ranges: List[DateRangeDTO], analysis_type: str) -> List[FlightHourlyCountDTO]:
        try:
            query = """
            WITH RECURSIVE hours AS (
                SELECT generate_series(0, 23) AS hour
            ),
            date_ranges AS (
                SELECT 
                    id as range_id,
                    label,
                    start_date::date, 
                    end_date::date,
                    origin_airport,
                    nivel_min, 
                    nivel_max
                FROM unnest(%s::text[], %s::text[], %s::date[], %s::date[], %s::text[], %s::int[], %s::int[]) 
                AS dr(id, label, start_date, end_date, origin_airport, nivel_min, nivel_max)
            ),
            flight_counts AS (
                SELECT 
                    date_part('hour', hora_salida)::int AS hour,
                    dr.label as label,
                    COUNT(*) AS flight_count
                FROM fligths f
                INNER JOIN date_ranges dr ON f.origen = dr.origin_airport
                WHERE f.fecha BETWEEN dr.start_date AND dr.end_date
                  AND (f.nivel::integer BETWEEN dr.nivel_min AND dr.nivel_max)
                GROUP BY 1, 2
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
            # Preparar los arrays para unnest
            ids = [str(r.id) for r in date_ranges]
            labels = [r.label for r in date_ranges]
            start_dates = [r.start_date for r in date_ranges]
            end_dates = [r.end_date for r in date_ranges]
            origins = [r.origin_airport for r in date_ranges]
            nivel_mins = [r.nivel_min if r.nivel_min is not None else 0 for r in date_ranges]
            nivel_maxs = [r.nivel_max if r.nivel_max is not None else 99999 for r in date_ranges]

       

            with self.connection.cursor() as cursor:
                cursor.execute(query, (ids, labels, start_dates, end_dates, origins, nivel_mins, nivel_maxs))

                print("*****************************")
                print("*****************************")
                print("*****************************")
                print("debug query : ")
                print(query, (ids, labels, start_dates, end_dates, origins, nivel_mins, nivel_maxs)) 
                results = cursor.fetchall()
                
                return [
                    {"hour": row[0], **row[1]} for row in results
                ]
                
        except Exception as e:
            print(f"Error in get_hourly_counts_by_date_ranges: {e}")
            raise

    def get_hourly_counts_by_date_ranges_destination(self, date_ranges: List[DateRangeDTO]) -> List[FlightHourlyCountDTO]:
        try:
            query = """
            WITH RECURSIVE hours AS (
                SELECT generate_series(0, 23) AS hour
            ),
            date_ranges AS (
                SELECT 
                    id as range_id,
                    label,
                    start_date::date, 
                    end_date::date,
                    destination_airport,
                    nivel_min, 
                    nivel_max
                FROM unnest(%s::text[], %s::text[], %s::date[], %s::date[], %s::text[], %s::int[], %s::int[]) 
                AS dr(id, label, start_date, end_date, destination_airport, nivel_min, nivel_max)
            ),
            flight_counts AS (
                SELECT 
                    date_part('hour', hora_llegada)::int AS hour,
                    dr.label as label,
                    COUNT(*) AS flight_count
                FROM fligths f
                INNER JOIN date_ranges dr ON f.destino = dr.destination_airport
                WHERE f.fecha BETWEEN dr.start_date AND dr.end_date
                  AND (f.nivel::integer BETWEEN dr.nivel_min AND dr.nivel_max)
                GROUP BY 1, 2
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
            
            # Preparar los arrays para unnest
            ids = [str(r.id) for r in date_ranges]
            labels = [r.label for r in date_ranges]
            start_dates = [r.start_date for r in date_ranges]
            end_dates = [r.end_date for r in date_ranges]
            destinations = [r.destination_airport for r in date_ranges]
            nivel_mins = [r.nivel_min if r.nivel_min is not None else 0 for r in date_ranges]
            nivel_maxs = [r.nivel_max if r.nivel_max is not None else 99999 for r in date_ranges]

            with self.connection.cursor() as cursor:
                cursor.execute(query, (ids, labels, start_dates, end_dates, destinations, nivel_mins, nivel_maxs))
                results = cursor.fetchall()
                
                return [
                    {"hour": row[0], **row[1]} for row in results
                ]
                
        except Exception as e:
            print(f"Error in get_hourly_counts_by_date_ranges_destination: {e}")
            raise