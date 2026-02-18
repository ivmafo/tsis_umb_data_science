import duckdb
import io
from typing import Dict, Any
import polars as pl
from src.infrastructure.config.settings import Settings

class ExportRawFlightsUseCase:
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        self.db_path = db_path

    def execute(self, filters: Dict[str, Any]) -> io.BytesIO:
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            # Base Query with Joins
            query = """
                SELECT 
                    f.*,
                    r_orig.name as region_origen,
                    r_dest.name as region_destino,
                    fpc.file_name as archivo_origen
                FROM flights f
                LEFT JOIN region_airports ra_orig ON f.origen = ra_orig.icao_code
                LEFT JOIN regions r_orig ON ra_orig.region_id = r_orig.id
                LEFT JOIN region_airports ra_dest ON f.destino = ra_dest.icao_code
                LEFT JOIN regions r_dest ON ra_dest.region_id = r_dest.id
                LEFT JOIN file_processing_control fpc ON f.file_id = fpc.id
                WHERE 1=1
            """
            
            params = []

            # 1. Date Range
            if filters.get('start_date'):
                query += " AND f.fecha >= ?"
                params.append(filters['start_date'])
            
            if filters.get('end_date'):
                query += " AND f.fecha <= ?"
                params.append(filters['end_date'])

            # 2. Flight Level
            if filters.get('min_level') is not None:
                query += " AND f.nivel >= ?"  # Note: table column is 'nivel', filter key often 'min_level'
                params.append(filters['min_level'])
            
            if filters.get('max_level') is not None:
                query += " AND f.nivel <= ?"
                params.append(filters['max_level'])

            # 3. List Filters Helper
            def add_list_filter(field_name, filter_key):
                items = filters.get(filter_key, [])
                if items:
                    # Handle potential dict items if they come as objects (though usually processed before)
                    # Assuming list of values or objects with 'value' key is handled by controller or caller
                    # But let's be safe and assume simple list of values here as per other use cases
                    placeholders = ','.join(['?'] * len(items))
                    nonlocal query
                    query += f" AND {field_name} IN ({placeholders})"
                    params.extend(items)

            # Map frontend keys to DB columns
            # Note: filters keys match what is sent from frontend (e.g. 'origins', 'destinations')
            # DB columns match 'f.origen', 'f.destino', etc.
            add_list_filter('f.origen', 'origins') 
            add_list_filter('f.destino', 'destinations')
            add_list_filter('f.matricula', 'matriculas')
            add_list_filter('f.tipo_aeronave', 'tipo_aeronave')
            add_list_filter('f.empresa', 'empresa')
            add_list_filter('f.tipo_vuelo', 'tipo_vuelo')
            add_list_filter('f.callsign', 'callsign')

            # Execute Query and get Polars DataFrame
            # collecting into Polars is efficient for CSV writing
            df = conn.execute(query, params).pl()
            
            # Write to buffer
            buffer = io.BytesIO()
            df.write_csv(buffer,separator=";")
            buffer.seek(0)
            
            return buffer

        except Exception as e:
            print(f"Error exporting raw data: {e}")
            raise e
        finally:
            conn.close()
