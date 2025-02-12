import psycopg2
#from psycopg2 import pool

class PostgresConnectionPool:
    def __init__(self, min_conn=1, max_conn=5):
        self.config = {
            "host": "localhost",
            "database": "flights",
            "user": "postgres",
            "password": "Iforero2011.",
            "port": 5432
        }
        self.pool = psycopg2.pool.SimpleConnectionPool(
            min_conn, max_conn, **self.config
        )

    def get_connection(self):
        return self.pool.getconn()

    def release_connection(self, conn):
        self.pool.putconn(conn)

    def close_all_connections(self):
        self.pool.closeall()