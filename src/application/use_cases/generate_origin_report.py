import duckdb
import io
import datetime
from typing import Dict, Any, List
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as PlatypusImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import squarify
import openpyxl
from openpyxl.drawing.image import Image as ExcelImage

class GenerateOriginReport:
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        self.db_path = db_path

    def _get_filter_summary(self, filters: Dict[str, Any]) -> Dict[str, str]:
        # ... (same as before, concise for replacement)
        summary = {}
        
        # Date Range
        start = filters.get('start_date')
        end = filters.get('end_date')
        if start and end:
            summary['Rango de Fechas'] = f"{start} al {end}"
        elif start:
            summary['Rango de Fechas'] = f"Desde {start}"
        elif end:
            summary['Rango de Fechas'] = f"Hasta {end}"
        else:
            summary['Rango de Fechas'] = "Todo el periodo"

        # List Filters Helper
        def process_list_filter(key, label):
            items = filters.get(key, [])
            if items:
                return ", ".join(map(str, items))
            return "Todos"

        summary['Orígenes'] = process_list_filter('origins', 'Orígenes')
        summary['Destinos'] = process_list_filter('destinations', 'Destinos')
        summary['Matrículas'] = process_list_filter('matriculas', 'Matrículas')
        summary['Tipo de Aeronave'] = process_list_filter('tipo_aeronave', 'Tipo de Aeronave')
        summary['Empresa'] = process_list_filter('empresa', 'Empresa')
        summary['Tipo de Vuelo'] = process_list_filter('tipo_vuelo', 'Tipo de Vuelo')
        summary['Callsign'] = process_list_filter('callsign', 'Callsign')
        
        # Flight Level
        min_lvl = filters.get('min_level')
        max_lvl = filters.get('max_level')
        if min_lvl is not None or max_lvl is not None:
            min_s = min_lvl if min_lvl is not None else "Min"
            max_s = max_lvl if max_lvl is not None else "Max"
            summary['Nivel de Vuelo'] = f"{min_s} - {max_s}"
        else:
            summary['Nivel de Vuelo'] = "Todos"

        return summary

    def _get_data(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            query = "SELECT origen, COUNT(*) as count FROM flights WHERE 1=1"
            params = []

            # Date Filters
            if filters.get('start_date'):
                query += " AND fecha >= ?"
                params.append(filters['start_date'])
            
            if filters.get('end_date'):
                query += " AND fecha <= ?"
                params.append(filters['end_date'])

            # Flight Level 
            if filters.get('min_level') is not None:
                query += " AND flight_level >= ?"
                params.append(filters['min_level'])
            
            if filters.get('max_level') is not None:
                query += " AND flight_level <= ?"
                params.append(filters['max_level'])

             # List filters
            def add_list_filter(field_name, filter_key):
                items = filters.get(filter_key, [])
                if items:
                    placeholders = ','.join(['?'] * len(items))
                    nonlocal query
                    query += f" AND {field_name} IN ({placeholders})"
                    params.extend(items)

            # Map frontend keys to DB columns
            add_list_filter('origen', 'origins') 
            add_list_filter('destino', 'destinations')
            add_list_filter('matricula', 'matriculas')
            add_list_filter('tipo_aeronave', 'tipo_aeronave')
            add_list_filter('empresa', 'empresa')
            add_list_filter('tipo_vuelo', 'tipo_vuelo')
            add_list_filter('callsign', 'callsign')

            query += " GROUP BY origen ORDER BY count DESC"
            
            results = conn.execute(query, params).fetchall()
            return [{'origen': r[0], 'count': r[1]} for r in results]

        except Exception as e:
            print(f"Error fetching data for report: {e}")
            raise e
        finally:
            conn.close()

    def _generate_chart(self, data: List[Dict[str, Any]]) -> io.BytesIO:
        """Generates a Treemap of the Top 10 origins."""
        if not data:
            return None
            
        # Top 10
        sorted_data = sorted(data, key=lambda x: x['count'], reverse=True)[:10]
        sizes = [x['count'] for x in sorted_data]
        labels = [f"{x['origen']}\n{x['count']}" for x in sorted_data]
        
        # Colors (similar to frontend)
        colors_list = [
            '#3b82f6', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308',
            '#22c55e', '#06b6d4', '#6366f1', '#d946ef', '#ef4444', '#14b8a6'
        ]
        
        plt.figure(figsize=(10, 6))
        try:
            squarify.plot(sizes=sizes, label=labels, color=colors_list[:len(sizes)], alpha=0.8, pad=True)
            plt.axis('off')
            plt.title("Top 10 Orígenes", fontsize=16, fontweight="bold")
        except Exception as e:
            # Fallback to bar chart if squarify fails unexpectedly
            print(f"Squarify error: {e}, using Bar Chart")
            plt.clf()
            names = [x['origen'] for x in sorted_data]
            plt.barh(names, sizes, color='#3b82f6')
            plt.xlabel('Vuelos')
            plt.title("Top 10 Orígenes")
            plt.gca().invert_yaxis()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        buffer.seek(0)
        return buffer

    def generate_excel(self, filters: Dict[str, Any]) -> io.BytesIO:
        data = self._get_data(filters)
        filter_summary = self._get_filter_summary(filters)
        chart_buffer = self._generate_chart(data)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')
        
        # Summary Sheet
        total_flights = df['count'].sum() if not df.empty else 0
        
        # Build summary with filters
        summary_rows = [
            {'Parametro': 'Reporte', 'Valor': 'Vuelos por Origen'},
            {'Parametro': 'Fecha Generación', 'Valor': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            {'Parametro': 'Total Vuelos', 'Valor': total_flights},
            {'Parametro': 'Total Origenes', 'Valor': len(df)},
            {'Parametro': '', 'Valor': ''}, # Spacer
            {'Parametro': 'FILTROS APLICADOS', 'Valor': ''}
        ]
        
        for key, value in filter_summary.items():
            summary_rows.append({'Parametro': key, 'Valor': value})

        pd.DataFrame(summary_rows).to_excel(writer, sheet_name='Resumen', index=False)
        
        # Data Sheet
        if not df.empty:
            # Add Percentage Column
            df['percent'] = (df['count'] / total_flights * 100)
            df['percent'] = df['percent'].apply(lambda x: f"{x:.4f}%")
            
            df.rename(columns={'origen': 'Código Origen', 'count': 'Total Vuelos', 'percent': '% del Total'}, inplace=True)
            df.to_excel(writer, sheet_name='Detalle', index=False)
        else:
             pd.DataFrame({'Info': ['No hay datos para los filtros seleccionados']}).to_excel(writer, sheet_name='Detalle', index=False)
        
        # Add Chart to Resumen Sheet if available
        if chart_buffer:
            worksheet = writer.sheets['Resumen']
            img = ExcelImage(chart_buffer)
            img.anchor = 'D2' # Place chart next to summary
            worksheet.add_image(img)

        writer.close()
        output.seek(0)
        return output

    def generate_pdf(self, filters: Dict[str, Any]) -> io.BytesIO:
        data = self._get_data(filters)
        filter_summary = self._get_filter_summary(filters)
        chart_buffer = self._generate_chart(data)
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title_style = styles['Title']
        elements.append(Paragraph("Reporte Ejecutivo: Distribución de Vuelos por Origen", title_style))
        elements.append(Spacer(1, 12))

        # Metadata & Filters
        normal_style = styles['Normal']
        gen_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elements.append(Paragraph(f"<b>Fecha de Generación:</b> {gen_date}", normal_style))
        
        total_flights = sum(d['count'] for d in data)
        elements.append(Paragraph(f"<b>Total de Vuelos en Filtro:</b> {total_flights:,}", normal_style))
        elements.append(Spacer(1, 12))

        # Filters Section
        elements.append(Paragraph("<b>Filtros Aplicados:</b>", normal_style))
        for key, value in filter_summary.items():
            elements.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;<b>{key}:</b> {value}", normal_style))
        
        elements.append(Spacer(1, 12))

        # Add Chart
        if chart_buffer:
             img = PlatypusImage(chart_buffer, width=450, height=270)
             elements.append(img)
             elements.append(Spacer(1, 12))

        # Table Data
        if data:
            # Headers
            table_data = [['#', 'Código Origen', 'Cantidad de Vuelos', '% del Total']]
            
            for idx, row in enumerate(data, 1):
                percent = (row['count'] / total_flights * 100) if total_flights > 0 else 0
                table_data.append([
                    str(idx),
                    row['origen'],
                    f"{row['count']:,}",
                    f"{percent:.4f}%"
                ])

            # Table Style
            table = Table(table_data, colWidths=[50, 150, 150, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')), # Indigo header
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
        else:
             elements.append(Paragraph("No se encontraron registros para los filtros seleccionados.", normal_style))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
