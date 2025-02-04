# Módulo para conexión a la base de datos
from src.data.adaptadores.postgres_adapter import PostgresAdapter

class ConexionDB:
    def __init__(self, adaptador: PostgresAdapter):
        self.adaptador = adaptador

    def obtener_conexion(self):
        return self.adaptador.obtener_conexion()

# Prueba de la conexión
if __name__ == "__main__":
    adaptador_postgres = PostgresAdapter()
    conexion_db = ConexionDB(adaptador_postgres)
    engine = conexion_db.obtener_conexion()
    connection = engine.connect()
    print("Conexión exitosa a PostgreSQL")
    connection.close()