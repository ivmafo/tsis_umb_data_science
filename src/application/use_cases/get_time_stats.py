import duckdb
from typing import List, Dict, Any, Optional

class GetTimeStats:
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        self.db_path = db_path

    def execute(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        print(f"DEBUG: GetTimeStats executing with filters: {filters}")
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            # Determine grouping
            group_by = filters.get('groupBy', 'month')
            date_format = '%Y' if group_by == 'year' else '%Y/%m'

            query = f"""
                SELECT 
                    strftime(fecha, '{date_format}') as name,
                    COUNT(*) as value
                FROM flights
                WHERE 1=1
            """
            params = []

            if filters.get('startDate'):
                # Handle possible Empty strings
                if filters['startDate'].strip():
                    query += " AND fecha >= ?"
                    params.append(filters['startDate'])
            
            if filters.get('endDate'):
                if filters['endDate'].strip():
                    query += " AND fecha <= ?"
                    params.append(filters['endDate'])

            if filters.get('minLevel'):
                try: 
                    params.append(float(filters['minLevel']))
                    query += " AND nivel >= ?"
                except: pass

            if filters.get('maxLevel'):
                try: 
                    params.append(float(filters['maxLevel']))
                    query += " AND nivel <= ?"
                except: pass

            # Dynamic Filters (Lists)
            # Adapting logic from GetFlightStats for handling list filters
            
            def add_list_filter(field_name, filter_key, value_mapper=None):
                items = filters.get(filter_key, [])
                if items:
                    # If items are objects with 'id' or 'value', extract them
                    # If value_mapper is provided, use it. Otherwise assume items are values if not dicts, or 'value'/'id' if dicts
                    values = []
                    for item in items:
                        if isinstance(item, dict):
                            if value_mapper:
                                val = value_mapper(item)
                                if val: values.append(val)
                            elif 'value' in item:
                                # Special case for airports which might have nested structure
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
                        # Special handling for Airports if needed, but assuming simple column matching based on previous code
                        # Actually previous code had subqueries for airports. 
                        # Let's verify schema: 'origen' is a string code (IATA/ICAO)? 
                        # Inspect DB showed 'SKBO', 'SKLG'. These are strings. 
                        # So filtering by 'origen IN (...)' with strings works.
                        query += f" AND {field_name} IN ({placeholders})"
                        params.extend(values)

            # Map filters
            # Note: The frontend sends 'selectedOrigins' which are objects.
            # in GetFlightStats it handled 'origins' (mapped from frontend).
            # Let's check what Frontend actually sends. 
            # In FlightDistributionView: <FlightsTimeChart filters={currentFilters} />
            # currentFilters is constructed from state. 
            # The state has 'selectedOrigins' etc.
            
            add_list_filter('origen', 'selectedOrigins') 
            add_list_filter('destino', 'selectedDestinations')
            add_list_filter('matricula', 'selectedMetricula')
            add_list_filter('tipo_aeronave', 'selectedTipoAeronave')
            add_list_filter('empresa', 'selectedEmpresa')
            add_list_filter('tipo_vuelo', 'selectedTipoVuelo')
            add_list_filter('callsign', 'selectedCallsign')

            query += " GROUP BY name ORDER BY name"

            print(f"DEBUG: Executing query: {query}")
            print(f"DEBUG: Params: {params}")

            results = conn.execute(query, params).fetchall()
            print(f"DEBUG: Result count: {len(results)}")
            
            # Format as Dicts for JSON response
            return [{"name": r[0], "value": r[1]} for r in results]

        except Exception as e:
            print(f"ERROR in GetTimeStats: {e}")
            raise e
        finally:
            conn.close()
