import psycopg2
from psycopg2.extras import RealDictCursor
from src.core.ports.file_processing_control_repository import FileProcessingControlRepository

class PostgresFileProcessingControlRepository(FileProcessingControlRepository):
    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection

    def add_file(self, file_name: str) -> None:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = "INSERT INTO file_processing_control (file_name) VALUES (%s);"
            cursor.execute(query, (file_name,))
            self.connection.commit()

    def is_file_processed(self, file_name: str) -> bool:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = "SELECT 1 FROM file_processing_control WHERE file_name = %s;"
            cursor.execute(query, (file_name,))
            result = cursor.fetchone()
            return result is not None
