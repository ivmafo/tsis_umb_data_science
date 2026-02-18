import duckdb
from typing import List, Dict, Any

class GetPeakHourStats:
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        self.db_path = db_path

    def execute(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        print(f"DEBUG: GetPeakHourStats executing with filters: {filters}")
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            # Query to get count by Day of Week (1-7) and Hour (0-23)
            # We treat hora_salida as 'HH:MM:SS' string or similar. 
            # try_cast to TIME allows extracting the hour.
            # isodow: 1=Monday, 7=Sunday
            
            # Determine time column (default to hora_salida)
            time_col = filters.get('timeColumn', 'hora_salida')
            
            # Validate to prevent SQL injection (though using f-string with known values is safer)
            allowed_cols = ['hora_salida', 'hora_llegada', 'hora_pv'] # Add others if needed
            if time_col not in allowed_cols:
                time_col = 'hora_salida'

            query = f"""
                SELECT 
                    isodow(fecha) as day_of_week,
                    date_part('hour', try_cast({time_col} as TIME)) as hour_of_day,
                    COUNT(*) as value
                FROM flights
                WHERE 1=1
                AND {time_col} IS NOT NULL 
                AND try_cast({time_col} as TIME) IS NOT NULL
            """
            params = []

            # --- Standard Filters (Duplicated from other use cases) ---
            # --- Standard Filters (Enhanced to support both camelCase and snake_case keys) ---
            start_date = filters.get('startDate') or filters.get('start_date')
            if start_date and start_date.strip():
                query += " AND fecha >= ?"
                params.append(start_date)
            
            end_date = filters.get('endDate') or filters.get('end_date')
            if end_date and end_date.strip():
                query += " AND fecha <= ?"
                params.append(end_date)

            min_level = filters.get('minLevel') or filters.get('min_level')
            if min_level:
                try: 
                    params.append(float(min_level))
                    query += " AND nivel >= ?"
                except: pass

            max_level = filters.get('maxLevel') or filters.get('max_level')
            if max_level:
                try: 
                    params.append(float(max_level))
                    query += " AND nivel <= ?"
                except: pass

            # Helper for list filters
            def add_list_filter(field_name, *filter_keys):
                # Check multiple potential keys (e.g. 'selectedOrigins', 'origins')
                items = []
                for k in filter_keys:
                    val = filters.get(k)
                    if val:
                        items = val
                        break
                
                if items:
                    values = []
                    for item in items:
                        if isinstance(item, dict):
                            if 'value' in item:
                                if isinstance(item['value'], dict) and 'icao_code' in item['value']:
                                    values.append(item['value']['icao_code'])
                                else:
                                    values.append(item['value'])
                            elif 'id' in item:
                                values.append(item['id'])
                        else:
                            values.append(item)
                    
                    if values:
                        placeholders = ','.join(['?'] * len(values))
                        nonlocal query
                        query += f" AND {field_name} IN ({placeholders})"
                        params.extend(values)

            # Support both frontend state keys (selectedX) and clean API keys (X)
            add_list_filter('origen', 'selectedOrigins', 'origins') 
            add_list_filter('destino', 'selectedDestinations', 'destinations')
            add_list_filter('matricula', 'selectedMetricula', 'matriculas')
            add_list_filter('tipo_aeronave', 'selectedTipoAeronave', 'tipo_aeronave')
            add_list_filter('empresa', 'selectedEmpresa', 'empresa')
            add_list_filter('tipo_vuelo', 'selectedTipoVuelo', 'tipo_vuelo')
            add_list_filter('callsign', 'selectedCallsign', 'callsign')

            query += """
                GROUP BY day_of_week, hour_of_day
                ORDER BY day_of_week, hour_of_day
            """

            results = conn.execute(query, params).fetchall()
            
            # Map results to list of dicts
            # isodow 1=Mon, 7=Sun.
            # hour 0-23
            return [{"day": int(r[0]), "hour": int(r[1]), "value": r[2]} for r in results]

        except Exception as e:
            print(f"ERROR in GetPeakHourStats: {e}")
            raise e
        finally:
            conn.close()
