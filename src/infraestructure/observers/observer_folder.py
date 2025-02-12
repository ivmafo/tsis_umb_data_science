import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from application.use_cases.process_flights_from_excel import ProcessFlightsFromExcelUseCase
from infrastructure.config.database import PostgresConnectionPool
from infrastructure.adapters.postgres_flight_repository import PostgresFlightRepository

class NewFileHandler(FileSystemEventHandler):
    def __init__(self, process_flights_uc):
        self.process_flights_uc = process_flights_uc

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".xlsx"):
            print(f"Nuevo archivo detectado: {event.src_path}")
            self.process_flights_uc.execute(event.src_path)

def start_observer(directory, process_flights_uc):
    event_handler = NewFileHandler(process_flights_uc)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Script principal para iniciar el observador
if __name__ == "__main__":
    # Configurar el pool de conexiones
    pool = PostgresConnectionPool()
    conn = pool.get_connection()

    # Inicializar repositorio
    flight_repo = PostgresFlightRepository(conn)

    # Inicializar caso de uso para procesar archivos Excel
    process_flights_uc = ProcessFlightsFromExcelUseCase(flight_repo)

    # Ruta del directorio a monitorear
    raw_directory = Path('data/raw')

    # Iniciar el observador
    start_observer(raw_directory, process_flights_uc)

    # Liberar recursos (este código nunca se ejecutará mientras el observador esté en funcionamiento)
    pool.release_connection(conn)
    pool.close_all_connections()
