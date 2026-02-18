
import duckdb
import json
from typing import Dict, Any, List
from .manage_sectors import ManageSectors

class CalculateSectorCapacity:
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        self.db_path = db_path
        self.manage_sectors = ManageSectors(db_path)

    def execute(self, sector_id: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates Sector Capacity (SCV) and Hourly Capacity (CH).
        filters: contains 'start_date', 'end_date' for the analysis period.
        """
        sector = self.manage_sectors.get_by_id(sector_id)
        if not sector:
            raise ValueError(f"Sector {sector_id} not found")

        # 1. Fetch Manual Parameters (TFC)
        t_transfer = sector.get('t_transfer', 0)
        t_comm_ag = sector.get('t_comm_ag', 0)
        t_separation = sector.get('t_separation', 0)
        t_coordination = sector.get('t_coordination', 0)
        
        # Calculate Total TFC
        TFC = t_transfer + t_comm_ag + t_separation + t_coordination
        
        if TFC <= 0:
            return {
                "error": "TFC (Tiempo de Funciones de Control) is zero. Please configure manual parameters for this sector.",
                "sector": sector
            }

        # 2. Fetch Flight Data based on Sector Definition + Date Filters
        sector_def = sector.get('definition', {})
        
        # Build Query
        # Assuming 'duracion' is the correct column name for flight duration in minutes
        query = "SELECT AVG(duracion) * 60 as avg_duration_sec, COUNT(*) as total_flights FROM flights WHERE 1=1"
        params = []
        
        # Apply Date Filters
        if filters.get('start_date'):
            query += " AND fecha >= ?"
            params.append(filters['start_date'])
        if filters.get('end_date'):
            query += " AND fecha <= ?"
            params.append(filters['end_date'])
            
        # Apply Sector Definition Filters (Origins, Destinations)
        # Assuming definition has 'origins' (list) and 'destinations' (list)
        origins = sector_def.get('origins', [])
        destinations = sector_def.get('destinations', [])
        
        if origins:
            placeholders = ','.join(['?'] * len(origins))
            query += f" AND origen IN ({placeholders})"
            params.extend(origins)
            
        if destinations:
            placeholders = ','.join(['?'] * len(destinations))
            query += f" AND destino IN ({placeholders})"
            params.extend(destinations)

        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            result = conn.execute(query, params).fetchone()
            avg_duration_sec = result[0] if result[0] else 0
            total_flights_analyzed = result[1] if result[1] else 0
            
            # 3. Calculate TPS (Time in Sector)
            TPS = avg_duration_sec
            
            if TPS <= 0:
                 return {
                    "error": "No flight data found for this sector in the selected period to calculate TPS.",
                    "TPS": 0,
                    "TFC": TFC,
                    "total_flights_analyzed": 0
                }

            # 4. Calculate SCV (Simultaneous Capacity)
            # Formula: SCV = TPS / (TFC * 1.3)
            # 1.3 is the buffer factor
            buffer_factor = 1.3
            SCV = TPS / (TFC * buffer_factor)
            
            # 5. Calculate CH (Hourly Capacity)
            # Formula: CH = (3600 * SCV) / TPS
            # Wait, (3600 * (TPS / (TFC*1.3))) / TPS  ==> 3600 / (TFC * 1.3)
            # Mathematically, TPS cancels out?
            # CH = 3600 / (Workload per aircraft)
            # Yes, flow rate depends on service rate, regardless of time in system (Little's Law implication?)
            # But let's follow the user's explicit formula: CH = (3600 * SCV) / TPS
            
            CH = (3600 * SCV) / TPS
            
            # 6. Adjustment Factor R
            R = sector.get('adjustment_factor_r', 1.0) # Default to 1 if missing, though schema defaults to 0.8
            if R is None: R = 0.8
            
            CH_Adjusted = CH * R

            return {
                "sector_name": sector['name'],
                "TPS": round(TPS, 2),
                "TFC_Total": round(TFC, 2),
                "TFC_Breakdown": {
                    "t_transfer": t_transfer,
                    "t_comm_ag": t_comm_ag,
                    "t_separation": t_separation,
                    "t_coordination": t_coordination
                },
                "SCV": round(SCV, 2),
                "CH_Theoretical": round(CH, 2),
                "CH_Adjusted": round(CH_Adjusted, 2),
                "R_Factor": R,
                "total_flights_analyzed": total_flights_analyzed,
                "formula_used": "SCV = TPS / (TFC * 1.3); CH = (3600 * SCV) / TPS"
            }

        except Exception as e:
            print(f"Error calculating capacity: {e}")
            raise e
        finally:
            conn.close()
