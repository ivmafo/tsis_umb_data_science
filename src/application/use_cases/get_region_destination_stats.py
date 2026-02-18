import duckdb
from typing import List, Dict, Any

class GetRegionDestinationStats:
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        self.db_path = db_path

    def execute(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            # Query to get count by Region and Destination
            # Structure: Region -> Destination -> Count
            
            query = """
                SELECT 
                    r.name as region_name,
                    f.destino as destination_code,
                    COUNT(*) as value
                FROM flights f
                JOIN region_airports ra ON f.destino = ra.icao_code
                JOIN regions r ON ra.region_id = r.id
                WHERE 1=1
            """
            params = []

            # --- Apply Filters (Standard) ---
            if filters.get('startDate'):
                if filters['startDate'].strip():
                    query += " AND f.fecha >= ?"
                    params.append(filters['startDate'])
            
            if filters.get('endDate'):
                if filters['endDate'].strip():
                    query += " AND f.fecha <= ?"
                    params.append(filters['endDate'])

            if filters.get('minLevel'):
                try: 
                    params.append(float(filters['minLevel']))
                    query += " AND f.nivel >= ?"
                except: pass

            if filters.get('maxLevel'):
                try: 
                    params.append(float(filters['maxLevel']))
                    query += " AND f.nivel <= ?"
                except: pass

            # List filters
            def add_list_filter(field_name, filter_key, value_mapper=None):
                items = filters.get(filter_key, [])
                if items:
                    values = []
                    for item in items:
                        if isinstance(item, dict):
                            if value_mapper:
                                val = value_mapper(item)
                                if val: values.append(val)
                            elif 'value' in item:
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

            add_list_filter('f.origen', 'selectedOrigins') 
            add_list_filter('f.destino', 'selectedDestinations')
            add_list_filter('f.matricula', 'selectedMetricula')
            add_list_filter('f.tipo_aeronave', 'selectedTipoAeronave')
            add_list_filter('f.empresa', 'selectedEmpresa')
            add_list_filter('f.tipo_vuelo', 'selectedTipoVuelo')
            add_list_filter('f.callsign', 'selectedCallsign')

            query += """
                GROUP BY region_name, destination_code
                ORDER BY region_name, value DESC
            """

            results = conn.execute(query, params).fetchall()
            
            # Transform to hierarchical format for ApexCharts Treemap (Multi-series)
            
            regions_map = {}
            for row in results:
                region = row[0]
                dest = row[1]
                count = row[2]
                
                if region not in regions_map:
                    regions_map[region] = []
                
                regions_map[region].append({'x': dest, 'y': count})
            
            output = []
            for region, data in regions_map.items():
                output.append({
                    'name': region,
                    'data': data
                })
                
            # Sort regions by total volume
            output.sort(key=lambda s: sum(d['y'] for d in s['data']), reverse=True)
            
            return output

        except Exception as e:
            print(f"ERROR in GetRegionDestinationStats: {e}")
            raise e
        finally:
            conn.close()
