
import duckdb
import uuid
import json
from typing import List, Dict, Any, Optional

class ManageSectors:
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        self.db_path = db_path

    def get_all(self) -> List[Dict[str, Any]]:
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            # simple select
            result = conn.execute("SELECT * FROM sectors").fetchall()
            sectors = []
            for row in result:
                sectors.append({
                    "id": row[0],
                    "name": row[1],
                    "definition": json.loads(row[2]) if row[2] else {},
                    "t_transfer": row[3],
                    "t_comm_ag": row[4],
                    "t_separation": row[5],
                    "t_coordination": row[6],
                    "adjustment_factor_r": row[7],
                    "capacity_baseline": row[8]
                })
            return sectors
        finally:
            conn.close()

    def get_by_id(self, sector_id: str) -> Optional[Dict[str, Any]]:
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            result = conn.execute("SELECT * FROM sectors WHERE id = ?", [sector_id]).fetchone()
            if result:
                return {
                    "id": result[0],
                    "name": result[1],
                    "definition": json.loads(result[2]) if result[2] else {},
                    "t_transfer": result[3],
                    "t_comm_ag": result[4],
                    "t_separation": result[5],
                    "t_coordination": result[6],
                    "adjustment_factor_r": result[7],
                    "capacity_baseline": result[8]
                }
            return None
        finally:
            conn.close()

    def create(self, data: Dict[str, Any]) -> str:
        conn = duckdb.connect(self.db_path)
        try:
            sector_id = str(uuid.uuid4())
            definition_json = json.dumps(data.get("definition", {}))
            
            conn.execute("""
                INSERT INTO sectors (id, name, definition, t_transfer, t_comm_ag, t_separation, t_coordination, adjustment_factor_r, capacity_baseline)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                sector_id,
                data.get("name"),
                definition_json,
                data.get("t_transfer", 0.0),
                data.get("t_comm_ag", 0.0),
                data.get("t_separation", 0.0),
                data.get("t_coordination", 0.0),
                data.get("adjustment_factor_r", 0.8), # Default R
                data.get("capacity_baseline", 0)
            ])
            return sector_id
        finally:
            conn.close()

    def update(self, sector_id: str, data: Dict[str, Any]) -> bool:
        # Fetch existing definition if not provided
        # Do this BEFORE opening the write connection to avoid "different configuration" error
        current_sector = self.get_by_id(sector_id)
        if not current_sector:
            return False

        if "definition" in data:
                definition_json = json.dumps(data["definition"])
        else:
                definition_json = json.dumps(current_sector["definition"])

        conn = duckdb.connect(self.db_path)
        try:
            conn.execute("""
                UPDATE sectors 
                SET name = COALESCE(?, name), 
                    definition = ?, 
                    t_transfer = COALESCE(?, t_transfer), 
                    t_comm_ag = COALESCE(?, t_comm_ag), 
                    t_separation = COALESCE(?, t_separation), 
                    t_coordination = COALESCE(?, t_coordination), 
                    adjustment_factor_r = COALESCE(?, adjustment_factor_r), 
                    capacity_baseline = COALESCE(?, capacity_baseline)
                WHERE id = ?
            """, [
                data.get("name"),
                definition_json,
                data.get("t_transfer"),
                data.get("t_comm_ag"),
                data.get("t_separation"),
                data.get("t_coordination"),
                data.get("adjustment_factor_r"),
                data.get("capacity_baseline"),
                sector_id
            ])
            return True
        except Exception as e:
            print(f"Update error: {e}")
            return False
        finally:
            conn.close()
            
    def delete(self, sector_id: str) -> bool:
        conn = duckdb.connect(self.db_path)
        try:
            conn.execute("DELETE FROM sectors WHERE id = ?", [sector_id])
            return True
        finally:
            conn.close()
