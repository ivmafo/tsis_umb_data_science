import duckdb
import holidays
from datetime import datetime, date
from typing import Dict, Any, List

class ManageCalendar:
    """
    Caso de uso para la gestión del calendario aeronáutico y festivos.
    
    Permite administrar eventos personalizados en DuckDB y combinarlos
    con los festivos oficiales de Colombia generados por la librería holidays.
    """
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        self.db_path = db_path
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Crea la tabla de eventos personalizados si no existe en DuckDB."""
        conn = duckdb.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS calendar_events (
                    fecha DATE PRIMARY KEY,
                    descripcion VARCHAR NOT NULL,
                    tipo VARCHAR NOT NULL -- 'festivo', 'receso', 'fin_de_ano', 'custom'
                )
            """)
        finally:
            conn.close()

    def get_custom_events(self) -> List[Dict[str, Any]]:
        """Recupera todos los eventos personalizados guardados en la BD."""
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            res = conn.execute("""
                SELECT fecha, descripcion, tipo 
                FROM calendar_events 
                ORDER BY fecha ASC
            """).fetchall()
            return [
                {
                    "fecha": row[0].strftime("%Y-%m-%d") if isinstance(row[0], (date, datetime)) else str(row[0]),
                    "descripcion": row[1],
                    "tipo": row[2]
                }
                for row in res
            ]
        finally:
            conn.close()

    def save_event(self, fecha: str, descripcion: str, tipo: str) -> Dict[str, Any]:
        """Guarda o actualiza un evento personalizado en la base de datos."""
        # Validar fecha
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Formato de fecha inválido. Debe ser YYYY-MM-DD")

        conn = duckdb.connect(self.db_path)
        try:
            conn.execute("""
                INSERT OR REPLACE INTO calendar_events (fecha, descripcion, tipo) 
                VALUES (?, ?, ?)
            """, [fecha, descripcion, tipo])
            return {"status": "success", "message": f"Evento guardado para la fecha {fecha}"}
        finally:
            conn.close()

    def delete_event(self, fecha: str) -> Dict[str, Any]:
        """Elimina un evento personalizado de la base de datos."""
        conn = duckdb.connect(self.db_path)
        try:
            conn.execute("DELETE FROM calendar_events WHERE fecha = ?", [fecha])
            return {"status": "success", "message": f"Evento eliminado para la fecha {fecha}"}
        finally:
            conn.close()

    def get_merged_calendar(self, year: int) -> List[Dict[str, Any]]:
        """
        Devuelve la lista unificada de todos los eventos del año.
        Combina los festivos oficiales de Colombia y los personalizados en DuckDB.
        """
        # 1. Obtener festivos oficiales de Colombia para el año
        try:
            co_holidays = holidays.Colombia(years=year)
        except Exception as e:
            print(f"Error cargando holidays.Colombia para {year}: {e}")
            co_holidays = {}

        merged_events = {}

        for dt, name in co_holidays.items():
            dt_str = dt.strftime("%Y-%m-%d")
            merged_events[dt_str] = {
                "fecha": dt_str,
                "descripcion": name,
                "tipo": "festivo",
                "es_oficial": True
            }

        # 2. Mezclar con los eventos de la base de datos para ese año
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            res = conn.execute("""
                SELECT fecha, descripcion, tipo 
                FROM calendar_events 
                WHERE EXTRACT(YEAR FROM fecha) = ?
                ORDER BY fecha ASC
            """, [year]).fetchall()

            for row in res:
                dt_str = row[0].strftime("%Y-%m-%d") if isinstance(row[0], (date, datetime)) else str(row[0])
                merged_events[dt_str] = {
                    "fecha": dt_str,
                    "descripcion": row[1],
                    "tipo": row[2],
                    "es_oficial": False
                }
        finally:
            conn.close()

        # Ordenar por fecha
        return [merged_events[k] for k in sorted(merged_events.keys())]
