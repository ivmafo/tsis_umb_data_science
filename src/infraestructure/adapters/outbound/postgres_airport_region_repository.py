import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
from src.core.ports.airport_region_repository import AirportRegionRepository
from src.core.entities.airport_region import AirportRegion
from datetime import datetime

class PostgresAirportRegionRepository(AirportRegionRepository):
    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection

    def get_all(self) -> List[AirportRegion]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, icao_code, region_id, created_at
                FROM airport_regions
                ORDER BY created_at DESC
            """)
            results = cursor.fetchall()
            return [AirportRegion(**row) for row in results]

    def get_by_id(self, id: int) -> Optional[AirportRegion]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, icao_code, region_id, created_at
                FROM airport_regions
                WHERE id = %s
            """, (id,))
            result = cursor.fetchone()
            return AirportRegion(**result) if result else None

    def get_by_icao(self, icao_code: str) -> List[AirportRegion]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, icao_code, region_id, created_at
                FROM airport_regions
                WHERE icao_code = %s
            """, (icao_code,))
            results = cursor.fetchall()
            return [AirportRegion(**row) for row in results]

    def create(self, airport_region_data: dict) -> AirportRegion:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                INSERT INTO airport_regions (icao_code, region_id)
                VALUES (%s, %s)
                RETURNING id, icao_code, region_id, created_at
            """, (airport_region_data['icao_code'], airport_region_data['region_id']))
            self.connection.commit()
            result = cursor.fetchone()
            return AirportRegion(**result)

    def update(self, id: int, airport_region_data: dict) -> Optional[AirportRegion]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            updates = []
            params = []
            if 'icao_code' in airport_region_data:
                updates.append("icao_code = %s")
                params.append(airport_region_data['icao_code'])
            if 'region_id' in airport_region_data:
                updates.append("region_id = %s")
                params.append(airport_region_data['region_id'])
            
            if not updates:
                return None

            params.append(id)
            query = f"""
                UPDATE airport_regions
                SET {', '.join(updates)}
                WHERE id = %s
                RETURNING id, icao_code, region_id, created_at
            """
            cursor.execute(query, tuple(params))
            self.connection.commit()
            result = cursor.fetchone()
            return AirportRegion(**result) if result else None

    def delete(self, id: int) -> bool:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("DELETE FROM airport_regions WHERE id = %s", (id,))
            self.connection.commit()
            return cursor.rowcount > 0