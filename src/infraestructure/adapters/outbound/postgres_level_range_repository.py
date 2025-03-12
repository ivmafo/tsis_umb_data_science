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
                    INSERT INTO level_ranges (min_level, max_level, alias, created_at, updated_at)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    RETURNING *;
                """
                cursor.execute(query, (level_range.min_level, level_range.max_level, level_range.alias))
                result = cursor.fetchone()
                self.connection.commit()
                return LevelRange(**result) if result else None
        except Exception as e:
            self.connection.rollback()
            print(f"Error al guardar el rango de nivel: {e}")
            raise

    def find_by_id(self, id: int) -> Optional[LevelRange]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT * FROM level_ranges WHERE id = %s;"
                cursor.execute(query, (id,))
                result = cursor.fetchone()
                return LevelRange(**result) if result else None
        except Exception as e:
            print(f"Error al buscar el rango de nivel: {e}")
            return None

    def get_all(self) -> List[LevelRange]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT * FROM level_ranges ORDER BY min_level;"
                cursor.execute(query)
                results = cursor.fetchall()
                return [LevelRange(**row) for row in results]
        except Exception as e:
            print(f"Error al obtener rangos de nivel: {e}")
            return []

    def update(self, level_range: LevelRange) -> LevelRange:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    UPDATE level_ranges 
                    SET min_level = %s, max_level = %s, alias = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING *;
                """
                cursor.execute(query, (
                    level_range.min_level,
                    level_range.max_level,
                    level_range.alias,
                    level_range.id
                ))
                result = cursor.fetchone()
                self.connection.commit()
                return LevelRange(**result) if result else None
        except Exception as e:
            self.connection.rollback()
            print(f"Error al actualizar el rango de nivel: {e}")
            raise

    def delete_by_id(self, id: int) -> bool:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "DELETE FROM level_ranges WHERE id = %s;"
                cursor.execute(query, (id,))
                self.connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.connection.rollback()
            print(f"Error al eliminar el rango de nivel: {e}")
            raise