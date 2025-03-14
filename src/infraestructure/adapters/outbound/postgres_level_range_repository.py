import psycopg2
from psycopg2.extras import RealDictCursor
from src.core.ports.level_range_repository import LevelRangeRepository
from src.core.entities.level_range import LevelRange
from typing import Optional, List

class PostgresLevelRangeRepository(LevelRangeRepository):
    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection

    def save(self, level_range: LevelRange) -> LevelRange:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    INSERT INTO sectores (origen, destino, nivel_min, nivel_max, ruta, zona)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING *;
                """
                cursor.execute(query, (
                    level_range.origen,
                    level_range.destino,
                    level_range.nivel_min,
                    level_range.nivel_max,
                    level_range.ruta,
                    level_range.zona
                ))
                result = cursor.fetchone()
                self.connection.commit()
                return LevelRange(**result) if result else None
        except Exception as e:
            self.connection.rollback()
            print(f"Error saving level range: {e}")
            raise

    def find_by_id(self, id: int) -> Optional[LevelRange]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT * FROM sectores WHERE id_sector = %s;"
                cursor.execute(query, (id,))
                result = cursor.fetchone()
                if result:
                    result['id'] = result.pop('id_sector')
                    return LevelRange(**result)
                return None
        except Exception as e:
            print(f"Error finding level range: {e}")
            return None

    def find_by_route(self, origen: str, destino: str) -> Optional[LevelRange]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT * FROM sectores WHERE origen = %s AND destino = %s;"
                cursor.execute(query, (origen, destino))
                result = cursor.fetchone()
                if result:
                    result['id'] = result.pop('id_sector')
                    return LevelRange(**result)
                return None
        except Exception as e:
            print(f"Error finding level range by route: {e}")
            return None

    def find_by_zone(self, zona: str) -> List[LevelRange]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT * FROM sectores WHERE zona = %s;"
                cursor.execute(query, (zona,))
                results = cursor.fetchall()
                return [LevelRange(**{**row, 'id': row['id_sector']}) for row in results]
        except Exception as e:
            print(f"Error finding level ranges by zone: {e}")
            return []

    def find_by_level_range(self, nivel_min: int, nivel_max: int) -> List[LevelRange]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT * FROM sectores 
                    WHERE nivel_min >= %s AND nivel_max <= %s;
                """
                cursor.execute(query, (nivel_min, nivel_max))
                results = cursor.fetchall()
                return [LevelRange(**{**row, 'id': row['id_sector']}) for row in results]
        except Exception as e:
            print(f"Error finding level ranges by level range: {e}")
            return []

    def get_all(self) -> List[LevelRange]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT * FROM sectores ORDER BY ruta, zona,origen,nivel_min;"
                cursor.execute(query)
                results = cursor.fetchall()
                processed_results = []
                for row in results:
                    # Handle NULL values by replacing them with empty strings
                    row['origen'] = row['origen'] or ''
                    row['destino'] = row['destino'] or ''
                    row['ruta'] = row['ruta'] or ''
                    row['zona'] = row['zona'] or ''
                    row['nivel_min'] = row['nivel_min'] or 0
                    row['nivel_max'] = row['nivel_max'] or 0
                    # Convert id_sector to id
                    row['id'] = row.pop('id_sector')
                    processed_results.append(LevelRange(**row))
                return processed_results
        except Exception as e:
            print(f"Error getting all level ranges: {e}")
            return []

    def update(self, level_range: LevelRange) -> LevelRange:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    UPDATE sectores 
                    SET origen = %s, destino = %s, nivel_min = %s, nivel_max = %s, 
                        ruta = %s, zona = %s
                    WHERE id_sector = %s
                    RETURNING *;
                """
                cursor.execute(query, (
                    level_range.origen,
                    level_range.destino,
                    level_range.nivel_min,
                    level_range.nivel_max,
                    level_range.ruta,
                    level_range.zona,
                    level_range.id
                ))
                result = cursor.fetchone()
                self.connection.commit()
                if result:
                    result['id'] = result.pop('id_sector')
                    return LevelRange(**result)
                return None
        except Exception as e:
            self.connection.rollback()
            print(f"Error updating level range: {e}")
            raise

    def delete_by_id(self, id: int) -> bool:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "DELETE FROM sectores WHERE id_sector = %s;"
                cursor.execute(query, (id,))
                self.connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.connection.rollback()
            print(f"Error deleting level range: {e}")
            raise