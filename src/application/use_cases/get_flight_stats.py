import duckdb
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class GetFlightStats:
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        self.db_path = db_path

    def execute(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Aggregates flight data by Origin based on provided filters.
        """
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            # Base query (corrected column name: origen)
            query = "SELECT origen, COUNT(*) as count FROM flights WHERE origen IS NOT NULL"
            params = []
            
            # Apply filters
            
            # 1. Date Range
            if filters.get('start_date'):
                query += " AND (fecha) >= ?"
                params.append(filters['start_date'])
            
            if filters.get('end_date'):
                query += " AND (fecha) <= ?"
                params.append(filters['end_date'])

            # 2. Level Range
            if filters.get('min_level'):
                try:
                    min_l = int(filters['min_level'])
                    query += " AND CAST(nivel AS INTEGER) >= ?"
                    params.append(min_l)
                except: pass
                
            if filters.get('max_level'):
                try:
                    max_l = int(filters['max_level'])
                    query += " AND CAST(nivel AS INTEGER) <= ?"
                    params.append(max_l)
                except: pass

            # 3. List Filters
            # Helper to add IN clauses
            def add_list_filter(field_name, filter_key):
                items = filters.get(filter_key, [])
                if items:
                    placeholders = ','.join(['?'] * len(items))
                    nonlocal query
                    query += f" AND {field_name} IN ({placeholders})"
                    params.extend(items)

            # Map frontend filter keys to DB columns
            # Note: filters.get('origins') comes from frontend 'origin' filter which maps to DB 'origen'
            add_list_filter('origen', 'origins') 
            add_list_filter('destino', 'destinations') # Assuming destinations might be 'destino' or 'destination', likely 'destino' given schema
            add_list_filter('matricula', 'matriculas')
            add_list_filter('tipo_aeronave', 'tipo_aeronave')
            add_list_filter('empresa', 'empresa')
            add_list_filter('tipo_vuelo', 'tipo_vuelo')
            add_list_filter('callsign', 'callsign')

            # Grouping
            query += " GROUP BY origen ORDER BY count DESC LIMIT 100"
            
            print(f"[RunDebug] Executing SQL: {query}")
            print(f"[RunDebug] Params: {params}")

            # Execute
            results = conn.execute(query, params).fetchall()
            
            # Format for Recharts Treemap (name, value)
            return [{"name": r[0], "value": r[1]} for r in results]
            
        except Exception as e:
            logger.error(f"Error getting flight stats: {e}")
            return []
        finally:
            conn.close()
