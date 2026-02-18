
import duckdb
import json
from typing import Dict, Any, List
from .manage_sectors import ManageSectors

class CalculateSectorCapacity:
    """
    Caso de uso para el cálculo de la Capacidad de un Sector Aeronáutico.
    Orquestador del cálculo de capacidad técnica de sectores ATC.
    Implementa la metodología de la Circular 006 de la Aerocivil para derivar
    la capacidad horaria basada en parámetros operativos y demanda real.
    """
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        """
        Inicializa el calculador inyectando la base de datos y utilidades.
        """
        self.db_path = db_path
        self.manage_sectors = ManageSectors(db_path)

    def execute(self, sector_id: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el ciclo completo de cálculo de capacidad.
        
        1. Recupera la configuración técnica del sector.
        2. Procesa la demanda histórica para obtener el TPS (Tiempo de Permanencia).
        3. Aplica la fórmula de SCV y CH (Capacidad Horaria).
        
        Args:
            sector_id (str): UUID del sector a analizar.
            filters (Dict): Filtros temporales (fecha_inicio, fecha_fin) para el cálculo de TPS.
            
        Returns:
            Dict: Resultados detallados incluyendo TPS, TFC, SCV y Capacidad Horaria Ajustada.
        """
        # Recuperar la configuración del sector
        sector = self.manage_sectors.get_by_id(sector_id)
        if not sector:
            raise ValueError(f"Sector {sector_id} no encontrado")

        # 1. Recuperar Parámetros Manuales (TFC - Tiempo de Funciones de Control)
        # El TFC es el tiempo total invertido por el controlador en un vuelo promedio.
        t_transfer = sector.get('t_transfer', 0)  # Tiempo de Transferencia
        t_comm_ag = sector.get('t_comm_ag', 0)    # Tiempo de Comunicaciones Aire-Tierra
        t_separation = sector.get('t_separation', 0) # Tiempo de Vigilancia y Separación
        t_coordination = sector.get('t_coordination', 0) # Tiempo de Coordinaciones
        
        # Cálculo del TFC Total
        TFC = t_transfer + t_comm_ag + t_separation + t_coordination
        
        # Validar que existan parámetros configurados
        if TFC <= 0:
            return {
                "error": "El TFC es cero. Por favor, configure los parámetros manuales para este sector.",
                "sector": sector
            }

        # 2. Consultar Datos de Vuelos basados en la definición del Sector y Filtros
        sector_def = sector.get('definition', {})
        
        # Construcción de la consulta SQL para obtener el tiempo promedio en el sector (TPS)
        query = "SELECT AVG(duracion) * 60 as avg_duration_sec, COUNT(*) as total_flights FROM flights WHERE 1=1"
        params = []
        
        # Aplicar filtros de fecha
        if filters.get('start_date'):
            query += " AND fecha >= ?"
            params.append(filters['start_date'])
        if filters.get('end_date'):
            query += " AND fecha <= ?"
            params.append(filters['end_date'])
            
        # Filtrar por Orígenes y Destinos definidos en el sector
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
            
            # 3. Calcular TPS (Time in Sector - Tiempo de permanencia en el sector)
            TPS = avg_duration_sec
            
            if TPS <= 0:
                 return {
                    "error": "No se encontraron datos de vuelos para este sector en el periodo seleccionado para calcular el TPS.",
                    "TPS": 0,
                    "TFC": TFC,
                    "total_flights_analyzed": 0
                }

            # 4. Calcular SCV (Capacidad Simultánea de Vuelos)
            # Fórmula: SCV = TPS / (TFC * Factor de Carga Mental)
            # El factor 1.3 representa el margen de seguridad para evitar la saturación cognitiva del controlador.
            buffer_factor = 1.3
            SCV = TPS / (TFC * buffer_factor)
            
            # 5. Calcular CH (Capacidad Horaria Teórica)
            # Fórmula: CH = (3600 * SCV) / TPS
            # Este valor indica cuántos vuelos puede manejar el sector en una ventana de una hora bajo las condiciones dadas.
            CH = (3600 * SCV) / TPS
            
            # 6. Factor de Ajuste R
            # Se utiliza para penalizar o bonificar la capacidad según condiciones operacionales específicas.
            R = sector.get('adjustment_factor_r', 1.0) 
            if R is None: R = 0.8  # Valor base por defecto según normativa si no está definido
            
            # Capacidad Horaria Ajustada (Final)
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
            print(f"Error calculando capacidad: {e}")
            raise e
        finally:
            conn.close()
