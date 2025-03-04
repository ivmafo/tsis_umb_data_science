import psycopg2
from psycopg2.extras import RealDictCursor
from src.core.ports.config_repository import ConfigRepository
from src.core.entities.config import Config
from typing import Optional, List

class PostgresConfigRepository(ConfigRepository):
    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection

    def save(self, config: Config) -> Config:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    INSERT INTO config (key, value, created_at, updated_at)
                    VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    RETURNING *;
                """
                cursor.execute(query, (config.key, config.value))
                result = cursor.fetchone()
                self.connection.commit()
                return Config(**result) if result else None
        except Exception as e:
            self.connection.rollback()
            print(f"Error al guardar la configuración: {e}")
            raise

    def find_by_key(self, key: str) -> Optional[Config]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT * FROM config WHERE key = %s;"
                cursor.execute(query, (key,))
                result = cursor.fetchone()
                return Config(**result) if result else None
        except Exception as e:
            print(f"Error al buscar la configuración: {e}")
            return None

    def get_all(self) -> List[Config]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT * FROM config ORDER BY key;"
                cursor.execute(query)
                results = cursor.fetchall()
                return [Config(**row) for row in results]
        except Exception as e:
            print(f"Error al obtener configuraciones: {e}")
            return []

    def update(self, config: Config) -> Config:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    UPDATE config 
                    SET value = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE key = %s
                    RETURNING *;
                """
                cursor.execute(query, (config.value, config.key))
                result = cursor.fetchone()
                self.connection.commit()
                return Config(**result) if result else None
        except Exception as e:
            self.connection.rollback()
            print(f"Error al actualizar la configuración: {e}")
            raise
    def __init__(self, connection):
        self.connection = connection
    def create(self, config):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO configs (key, value, created_at, updated_at)
                VALUES (%s, %s, %s, %s)
                RETURNING *
                """,
                (config.key, config.value, config.created_at, config.updated_at)
            )
            self.connection.commit()
            return cursor.fetchone()
    def delete_by_key(self, key: str) -> bool:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "DELETE FROM config WHERE key = %s;"
                cursor.execute(query, (key,))
                self.connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.connection.rollback()
            print(f"Error al eliminar la configuración: {e}")
            raise