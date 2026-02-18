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

class GenerateCompanyReport:
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        self.db_path = db_path

    def _get_data(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            query = "SELECT empresa, COUNT(*) as count FROM flights WHERE 1=1"
            params = []
            if filters.get('start_date'):
                query += " AND fecha >= ?"
                params.append(filters['start_date'])
            if filters.get('end_date'):
                query += " AND fecha <= ?"
                params.append(filters['end_date'])
            
            # ... other filters logic ...
            
            query += " GROUP BY empresa ORDER BY count DESC LIMIT 20" # Top 20
            results = conn.execute(query, params).fetchall()
            # Ensure name is not None for ReportLab
            return [{'name': r[0] if r[0] else 'N/A', 'value': r[1]} for r in results]
        finally:
            conn.close()

    def _generate_chart(self, data: List[Dict[str, Any]]) -> io.BytesIO:
        if not data: return None
        # Sort for horizontal bar (top at top)
        sorted_data = sorted(data, key=lambda x: x['value'])
        names = [d['name'] for d in sorted_data]
        values = [d['value'] for d in sorted_data]
        
        plt.figure(figsize=(10, 8))
        plt.barh(names, values, color='#6366f1')
        plt.title("Vuelos por Empresa")
        plt.xlabel("Vuelos")
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        buffer.seek(0)
        return buffer

    def generate_excel(self, filters: Dict[str, Any]) -> io.BytesIO:
        data = self._get_data(filters)
        chart = self._generate_chart(data)
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

    def generate_pdf(self, filters: Dict[str, Any]) -> io.BytesIO:
        data = self._get_data(filters)
        chart = self._generate_chart(data)
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        elements.append(Paragraph("Reporte: Vuelos por Empresa", getSampleStyleSheet()['Title']))
        
        if chart:
             elements.append(PlatypusImage(chart, width=500, height=400))
        
        if data:
             t_data = [['Empresa', 'Vuelos']] + [[d['name'], d['value']] for d in data]
             elements.append(Table(t_data))
             
        doc.build(elements)
        buffer.seek(0)
        return buffer
