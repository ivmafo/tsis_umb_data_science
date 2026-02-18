import duckdb
import io
import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as PlatypusImage
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import numpy as np
import openpyxl
from openpyxl.drawing.image import Image as ExcelImage

class GenerateHeatmapReport:
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        self.db_path = db_path

    def _get_data(self, filters: Dict[str, Any], time_column: str) -> List[Dict[str, Any]]:
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            # dayofweek(date) -> 0=Mon..6=Sun? 
            # DuckDB ISODOW -> 1=Mon..7=Sun
            # We will use ISODOW to match typical mapping
            
            # Extract hour from time_column which might be time, timestamp, or string?
            # Assuming it's a timestamp or time type.
            # Query: SELECT ISODOW(fecha) as day, DATE_PART('hour', CAST(time_column AS TIME)) as hour, COUNT(*)
            
            # Actually, `fecha` is date. `time_column` (hora_salida) is likely just Time.
            # Need to combine or just check logic.
            # Assuming `hora_salida` is a TIME column or string HH:MM:SS. 
            
            query = f"""
                SELECT 
                    ISODOW(fecha) as day, 
                    CAST(SUBSTR(CAST({time_column} AS VARCHAR), 1, 2) AS INTEGER) as hour, 
                    COUNT(*) as count 
                FROM flights 
                WHERE 1=1
            """
            params = []
            
            if filters.get('start_date'):
               query += " AND fecha >= ?"
               params.append(filters['start_date'])
            # ... other filters ...
            
            query += " GROUP BY day, hour"
            results = conn.execute(query, params).fetchall()
            # Filter checks
            cleaned_results = []
            for r in results:
                if r[0] is not None and r[1] is not None:
                     cleaned_results.append({'day': r[0], 'hour': r[1], 'value': r[2]})
            return cleaned_results
        finally:
            conn.close()

    def _generate_chart(self, data: List[Dict[str, Any]]) -> io.BytesIO:
        if not data: return None
        
        # Grid: 7 days x 24 hours
        grid = np.zeros((7, 24))
        for d in data:
            # day is 1-7 (Mon-Sun). Index 0-6.
            # hour is 0-23.
            d_idx = d['day'] - 1
            h_idx = d['hour']
            if 0 <= d_idx < 7 and 0 <= h_idx < 24:
                grid[d_idx, h_idx] = d['value']
        
        # Days Labels (Top to Bottom: Mon -> Sun)
        days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        
        plt.figure(figsize=(12, 5))
        plt.imshow(grid, cmap='RdYlBu_r', aspect='auto') # Blue to Red heatmap? Or single color intensity? 
        # Using simple heatmap.
        
        plt.colorbar(label='Vuelos')
        plt.yticks(range(7), days)
        plt.xlabel("Hora del Día")
        plt.xticks(range(24), [str(i) for i in range(24)])
        plt.title("Mapa de Calor: Frecuencia de Vuelos")
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        buffer.seek(0)
        return buffer

    def generate_excel(self, filters: Dict[str, Any], time_column: str = 'hora_salida') -> io.BytesIO:
        data = self._get_data(filters, time_column)
        chart = self._generate_chart(data)
        
        # Pivot for Excel Table
        # Rows: Days, Cols: Hours
        # We can make a nice table in DataFrame
        df_flat = pd.DataFrame(data)
        if not df_flat.empty:
            df_pivot = df_flat.pivot(index='day', columns='hour', values='value').fillna(0)
            df_pivot.index = df_pivot.index.map({1:'Lun', 2:'Mar', 3:'Mié', 4:'Jue', 5:'Vie', 6:'Sáb', 7:'Dom'})
        else:
            df_pivot = pd.DataFrame()

        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')
        
        if not df_pivot.empty:
            df_pivot.to_excel(writer, sheet_name='Matriz')
        
        if chart:
             ws = writer.book.create_sheet('Resumen')
             ws.add_image(ExcelImage(chart), 'A1')
             
        writer.close()
        output.seek(0)
        return output

    def generate_pdf(self, filters: Dict[str, Any], time_column: str = 'hora_salida') -> io.BytesIO:
        data = self._get_data(filters, time_column)
        chart = self._generate_chart(data)
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        elements.append(Paragraph(f"Reporte: Mapa de Calor ({time_column})", getSampleStyleSheet()['Title']))
        
        if chart:
             elements.append(PlatypusImage(chart, width=500, height=250))
        
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Ver el archivo Excel para el detalle matricial completo.", getSampleStyleSheet()['Normal']))
             
        doc.build(elements)
        buffer.seek(0)
        return buffer
