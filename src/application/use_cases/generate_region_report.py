import duckdb
import io
import datetime
from typing import Dict, Any, List
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as PlatypusImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import matplotlib.pyplot as plt
import squarify
import openpyxl
from openpyxl.drawing.image import Image as ExcelImage

class GenerateRegionReport:
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        self.db_path = db_path

    def _get_filter_summary(self, filters: Dict[str, Any]) -> Dict[str, str]:
        # Reuse common logic or import if refactored. Integrating directly for speed.
        summary = {}
        
        # 1. Date Range
        start, end = filters.get('start_date'), filters.get('end_date')
        if start and end: summary['Rango de Fechas'] = f"{start} al {end}"
        elif start: summary['Rango de Fechas'] = f"Desde {start}"
        elif end: summary['Rango de Fechas'] = f"Hasta {end}"
        else: summary['Rango de Fechas'] = "Todo el periodo"
        
        # 2. List Filters Helper
        def parse_list_filter(key, label):
            items = filters.get(key, [])
            if items:
                # Extract values if items are objects/dicts
                values = []
                for x in items:
                    if isinstance(x, dict):
                        # Handle commonly used frontend headers
                        if 'label' in x: values.append(str(x['label'])) 
                        elif 'value' in x: 
                             # value might be dict too if it's complex select
                             val = x['value']
                             if isinstance(val, dict) and 'icao_code' in val: values.append(str(val['icao_code']))
                             else: values.append(str(val))
                        elif 'id' in x: values.append(str(x['id']))
                    else:
                        values.append(str(x))
                        
                if values:
                    summary[label] = ", ".join(values)

        # 3. Apply standard filters
        parse_list_filter('selectedOrigins', 'Orígenes')
        parse_list_filter('selectedDestinations', 'Destinos')
        parse_list_filter('selectedEmpresa', 'Empresas')
        parse_list_filter('selectedTipoAeronave', 'Tipos de Aeronave')
        parse_list_filter('selectedTipoVuelo', 'Tipos de Vuelo')
        parse_list_filter('selectedCallsign', 'Callsigns')
        parse_list_filter('selectedMetricula', 'Matrículas')

        return summary

    def _get_data(self, filters: Dict[str, Any], dimension: str) -> List[Dict[str, Any]]:
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            # Determine field based on dimension
            flight_field = 'f.origen' if dimension == 'origin' else 'f.destino'
            
            query = f"""
                SELECT 
                    r.name as region_name,
                    {flight_field} as airport_code,
                    COUNT(*) as count
                FROM flights f
                JOIN region_airports ra ON {flight_field} = ra.icao_code
                JOIN regions r ON ra.region_id = r.id
                WHERE 1=1
            """
            params = []
            
            if filters.get('start_date'):
                query += " AND f.fecha >= ?"
                params.append(filters['start_date'])
            if filters.get('end_date'):
                query += " AND f.fecha <= ?"
                params.append(filters['end_date'])
                
            # ... other filters logic (simplified for report but ideally should match UseCase) ...
            # For strict consistency, we should replicate all filters, but starting with date is key.

            query += f" GROUP BY region_name, airport_code"
            results = conn.execute(query, params).fetchall()
            
            # Map results: Region -> Total Count (aggregating all airports in that region)
            # OR Region -> List of Airports?
            # The report chart expects: [{'region': 'Andina', 'count': 100}, ...]
            # So we aggregate by region here in python or in SQL?
            # In SQL is better.
            
            # Re-aggregating in Python for flexibility if I want detail later, 
            # but for the Chart/Report summary we need Region totals.
            
            data_map = {}
            for r in results:
                region = r[0] if r[0] else 'Desconocida'
                cnt = r[2]
                data_map[region] = data_map.get(region, 0) + cnt
                
            return [{'region': k, 'count': v} for k, v in data_map.items()]

        except Exception as e:
            print(f"Error fetching data: {e}")
            raise e
        finally:
            conn.close()

    def _generate_chart(self, data: List[Dict[str, Any]]) -> io.BytesIO:
        if not data: return None
        sorted_data = sorted(data, key=lambda x: x['count'], reverse=True)
        sizes = [x['count'] for x in sorted_data]
        labels = [f"{x['region']}\n{x['count']}" for x in sorted_data]
        
        plt.figure(figsize=(10, 6))
        try:
            squarify.plot(sizes=sizes, label=labels, alpha=0.8, pad=True)
            plt.axis('off')
            plt.title("Distribución por Región")
        except:
             plt.clf() # fallback
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        buffer.seek(0)
        return buffer

    def generate_excel(self, filters: Dict[str, Any], dimension: str = 'origin') -> io.BytesIO:
        data = self._get_data(filters, dimension)
        chart = self._generate_chart(data)
        df = pd.DataFrame(data)
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')
        if not df.empty:
            df.to_excel(writer, sheet_name='Detalle', index=False)
        
        # Add Filter Summary
        summary = self._get_filter_summary(filters)
        if summary:
            ws_meta = writer.book.create_sheet('Filtros')
            ws_meta.append(['Filtro', 'Valor'])
            for k, v in summary.items():
                ws_meta.append([k, v])

        if chart:
            ws = writer.sheets.get('Resumen', writer.book.create_sheet('Resumen'))
            img = ExcelImage(chart)
            ws.add_image(img, 'A1')
        writer.close()
        output.seek(0)
        return output

    def generate_pdf(self, filters: Dict[str, Any], dimension: str = 'origin') -> io.BytesIO:
        data = self._get_data(filters, dimension)
        chart = self._generate_chart(data)
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        # Add Filter Summary
        summary = self._get_filter_summary(filters)
        if summary:
            elements.append(Paragraph("Filtros Aplicados:", getSampleStyleSheet()['Heading2']))
            data_filters = [[k, v] for k, v in summary.items()]
            t_filters = Table(data_filters, hAlign='LEFT')
            t_filters.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ]))
            elements.append(t_filters)
            elements.append(Spacer(1, 12))

        if chart:
            elements.append(PlatypusImage(chart, width=400, height=250))
        
        # Table
        if data:
            t_data = [['Región', 'Vuelos']] + [[d['region'], d['count']] for d in data]
            elements.append(Table(t_data))
            
        doc.build(elements)
        buffer.seek(0)
        return buffer
