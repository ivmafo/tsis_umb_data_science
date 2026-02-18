import duckdb
import io
import datetime
from typing import Dict, Any, List
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as PlatypusImage
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import openpyxl
from openpyxl.drawing.image import Image as ExcelImage

class GenerateTimeReport:
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        self.db_path = db_path

    def _get_data(self, filters: Dict[str, Any], group_by: str) -> List[Dict[str, Any]]:
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            # group_by: 'month' or 'year'
            if group_by == 'year':
                date_part = "strftime(fecha, '%Y')"
            else:
                date_part = "strftime(fecha, '%Y-%m')"
                
            query = f"SELECT {date_part} as period, COUNT(*) as count FROM flights WHERE 1=1"
            params = []
            
            if filters.get('start_date'):
                query += " AND fecha >= ?"
                params.append(filters['start_date'])
            # ... other filters ...
            
            query += f" GROUP BY period ORDER BY period"
            results = conn.execute(query, params).fetchall()
            return [{'name': r[0] if r[0] else 'N/A', 'value': r[1]} for r in results]
        finally:
            conn.close()

    def _generate_chart(self, data: List[Dict[str, Any]], group_by: str) -> io.BytesIO:
        if not data: return None
        periods = [d['name'] for d in data]
        values = [d['value'] for d in data]
        
        plt.figure(figsize=(12, 6))
        plt.plot(periods, values, marker='o', linestyle='-', color='#3b82f6')
        plt.bar(periods, values, alpha=0.3, color='#3b82f6')
        plt.title(f"Vuelos por {'Año' if group_by == 'year' else 'Mes'}")
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, linestyle='--', alpha=0.5)
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        buffer.seek(0)
        return buffer

    def generate_excel(self, filters: Dict[str, Any], group_by: str = 'month') -> io.BytesIO:
        data = self._get_data(filters, group_by)
        chart = self._generate_chart(data, group_by)
        df = pd.DataFrame(data)
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')
        if not df.empty:
            df.to_excel(writer, sheet_name='Detalle', index=False)
        if chart:
            ws = writer.book.create_sheet('Resumen')
            ws.add_image(ExcelImage(chart), 'A1')
        writer.close()
        output.seek(0)
        return output

    def generate_pdf(self, filters: Dict[str, Any], group_by: str = 'month') -> io.BytesIO:
        data = self._get_data(filters, group_by)
        chart = self._generate_chart(data, group_by)
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        elements.append(Paragraph(f"Reporte: Vuelos por {'Año' if group_by == 'year' else 'Mes'}", getSampleStyleSheet()['Title']))
        
        if chart:
             elements.append(PlatypusImage(chart, width=500, height=300))
        
        if data:
             t_data = [['Periodo', 'Vuelos']] + [[d['name'], d['value']] for d in data]
             elements.append(Table(t_data))
             
        doc.build(elements)
        buffer.seek(0)
        return buffer
