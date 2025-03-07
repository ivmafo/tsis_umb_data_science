import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

class AnalizadorVuelosInteractivo:
    def __init__(self, directorio_salida='resultados/analisis_origen'):
        self.directorio_salida = directorio_salida
        self.crear_directorio()
        self.app = dash.Dash(__name__, suppress_callback_exceptions=True)
        
    def cargar_datos(self):
        """Carga los datos desde la base de datos PostgreSQL"""
        try:
            engine = create_engine('postgresql://postgres:Iforero2011.@localhost:5432/flights')
            query = "SELECT * FROM public.fligths"  # Fixed table name
            return pd.read_sql(query, engine)
        except Exception as e:
            print(f"Error al cargar datos: {e}")
            return pd.DataFrame()
            
    def preparar_datos(self, df):
        """Prepara los datos para el análisis"""
        df['tiempo_inicial'] = pd.to_datetime(df['tiempo_inicial'])
        df['fecha'] = df['tiempo_inicial'].dt.date
        df['hora'] = df['tiempo_inicial'].dt.hour
        df['dia_semana'] = df['tiempo_inicial'].dt.day_name()
        df['semana'] = df['tiempo_inicial'].dt.isocalendar().week
        df['mes'] = df['tiempo_inicial'].dt.month_name()
        df['año'] = df['tiempo_inicial'].dt.year
        df['trimestre'] = df['tiempo_inicial'].dt.quarter
        return df
            
    def crear_directorio(self):
        """Crea el directorio de salida si no existe"""
        import os
        if not os.path.exists(self.directorio_salida):
            os.makedirs(self.directorio_salida)
            
    def configurar_layout(self, df):
        # Helper function to handle None values in dropdowns
        def get_sorted_unique(df, column):
            if column not in df.columns:
                return []
            values = df[column].unique()
            values = [x for x in values if x is not None]
            return sorted(values)
        self.app.layout = html.Div([
            html.H1('Análisis de Vuelos Interactivo'),
            
            # Filtros actualizados
            html.Div([
                # Filtro de Año
                html.Div([
                    html.Label('Año:'),
                    dcc.Dropdown(
                        id='año-filter',
                        options=[{'label': str(x), 'value': x} 
                                for x in sorted(df['año'].unique())],
                        multi=False
                    )
                ], style={'width': '20%', 'display': 'inline-block', 'marginRight': '2%'}),
                
                # Filtro de Trimestre
                html.Div([
                    html.Label('Trimestre:'),
                    dcc.Dropdown(
                        id='trimestre-filter',
                        options=[
                            {'label': f'Q{i}', 'value': i} 
                            for i in range(1, 5)
                        ],
                        multi=True
                    )
                ], style={'width': '20%', 'display': 'inline-block', 'marginRight': '2%'}),
                
                # Filtro de Origen
                html.Div([
                    html.Label('Origen:'),
                    dcc.Dropdown(
                        id='origen-filter',
                        options=[{'label': x, 'value': x} 
                                for x in sorted(df['origen'].unique())],
                        multi=True
                    )
                ], style={'width': '20%', 'display': 'inline-block', 'marginRight': '2%'}),
                
                # Filtro de Destino
                html.Div([
                    html.Label('Destino:'),
                    dcc.Dropdown(
                        id='destino-filter',
                        options=[{'label': x, 'value': x} 
                                for x in sorted(df['destino'].unique())],
                        multi=True
                    )
                ], style={'width': '20%', 'display': 'inline-block', 'marginRight': '2%'}),
            ], style={'marginBottom': '10px'}),
            
            html.Div([
                # Filtro de Empresa
                html.Div([
                    html.Label('Empresa:'),
                    dcc.Dropdown(
                        id='empresa-filter',
                        options=[{'label': str(x), 'value': x} 
                                for x in get_sorted_unique(df, 'empresa')],
                        multi=True
                    )
                ], style={'width': '20%', 'display': 'inline-block', 'marginRight': '2%'}),
                
                # Filtro de Nivel
                html.Div([
                    html.Label('Nivel:'),
                    dcc.Dropdown(
                        id='nivel-filter',
                        options=[{'label': str(x), 'value': x} 
                                for x in get_sorted_unique(df, 'nivel')],
                        multi=True
                    )
                ], style={'width': '20%', 'display': 'inline-block', 'marginRight': '2%'}),
            ], style={'marginBottom': '20px'}),
            
            # Agrupar por:
            html.Div([
                html.Label('Agrupar por:'),
                dcc.Dropdown(
                    id='group-by',
                    options=[
                        {'label': 'Día', 'value': 'fecha'},
                        {'label': 'Mes', 'value': 'mes'},
                        {'label': 'Día de la semana', 'value': 'dia_semana'},
                        {'label': 'Semana', 'value': 'semana'}
                    ],
                    value='fecha'
                )
            ], style={'width': '30%', 'display': 'inline-block'})
        ], style={'marginBottom': '20px'}),
        
        # Gráficos
        dcc.Graph(id='heatmap-vuelos'),
        dcc.Graph(id='bar-chart-vuelos'),
        html.Div([
            dcc.Graph(id='treemap-aerodromos'),
            dcc.Graph(id='bar-pistas'),
            dcc.Graph(id='bar-anual'),
            dcc.Graph(id='pie-aeronaves'),
            dcc.Graph(id='line-mensual'),
            dcc.Graph(id='bar-diario'),
            dcc.Graph(id='bar-semanal'),
            dcc.Graph(id='bar-horario'),
            dcc.Graph(id='heatmap-vuelos'),
            dcc.Graph(id='bar-chart-vuelos'),
            html.Div(id='summary-table')
        ])
    def callback_actualizacion(self):
        @self.app.callback(
            [Output('treemap-aerodromos', 'figure'),
             Output('bar-pistas', 'figure'),
             Output('bar-anual', 'figure'),
             Output('pie-aeronaves', 'figure'),
             Output('line-mensual', 'figure'),
             Output('bar-diario', 'figure'),
             Output('bar-semanal', 'figure'),
             Output('bar-horario', 'figure'),
             Output('heatmap-vuelos', 'figure'),
             Output('bar-chart-vuelos', 'figure'),
             Output('summary-table', 'children')],
            [Input('año-filter', 'value'),
             Input('trimestre-filter', 'value'),
             Input('origen-filter', 'value'),
             Input('destino-filter', 'value'),
             Input('empresa-filter', 'value'),
             Input('nivel-filter', 'value'),
             Input('group-by', 'value')]
        )
        def update_graphs(año, trimestre, origenes, destinos, empresas, niveles, group_by):
            df_filtered = self.df.copy()
            
            # Apply all filters
            if año:
                df_filtered = df_filtered[df_filtered['año'] == año]
            if trimestre:
                df_filtered = df_filtered[df_filtered['trimestre'].isin(trimestre)]
            if origenes:
                df_filtered = df_filtered[df_filtered['origen'].isin(origenes)]
            if destinos:
                df_filtered = df_filtered[df_filtered['destino'].isin(destinos)]
            if empresas:
                df_filtered = df_filtered[df_filtered['empresa'].isin(empresas)]
            if niveles:
                df_filtered = df_filtered[df_filtered['nivel'].isin(niveles)]

            # Treemap de aeródromos
            treemap = px.treemap(
                df_filtered, 
                path=['origen'], 
                values='tiempo_inicial',
                title='Número de Vuelos por Aeródromo'
            )

            # Gráfico de barras por pista
            df_pistas = df_filtered.groupby('pista').size().reset_index(name='conteo')
            bar_pistas = px.bar(
                df_pistas,
                x='pista',
                y='conteo',
                title='Número de Vuelos por Pista'
            )

            # Gráfico de barras por año
            df_filtered['año'] = df_filtered['tiempo_inicial'].dt.year
            df_anual = df_filtered.groupby('año').size().reset_index(name='conteo')
            bar_anual = px.bar(
                df_anual,
                x='año',
                y='conteo',
                title='Número de Vuelos por Año'
            )

            # Gráfico de pie por tipo de aeronave
            df_aeronaves = df_filtered.groupby('tipo_aeronave').size().reset_index(name='conteo')
            pie_aeronaves = px.pie(
                df_aeronaves,
                values='conteo',
                names='tipo_aeronave',
                title='Distribución de Vuelos por Tipo de Aeronave'
            )

            # Gráfico de línea por mes
            df_mensual = df_filtered.groupby('mes').size().reset_index(name='conteo')
            line_mensual = px.line(
                df_mensual,
                x='mes',
                y='conteo',
                title='Número de Operaciones por Mes'
            )

            # Gráfico de barras por día
            df_diario = df_filtered.groupby('fecha').size().reset_index(name='conteo')
            bar_diario = px.bar(
                df_diario,
                x='fecha',
                y='conteo',
                title='Número de Operaciones por Día'
            )

            # Gráfico de barras por día de la semana
            df_semanal = df_filtered.groupby('dia_semana').size().reset_index(name='conteo')
            bar_semanal = px.bar(
                df_semanal,
                x='dia_semana',
                y='conteo',
                title='Número de Vuelos por Día de la Semana'
            )

            # Gráfico de barras por hora
            df_horario = df_filtered.groupby('hora').size().reset_index(name='conteo')
            bar_horario = px.bar(
                df_horario,
                x='hora',
                y='conteo',
                title='Número de Vuelos por Hora del Día'
            )
            # Crear heatmap
            df_heat = df_filtered.groupby(['hora', group_by]).size().reset_index(name='conteo')
            heatmap = px.density_heatmap(
                df_heat,
                x=group_by,
                y='hora',
                z='conteo',
                title=f'Distribución de Vuelos por Hora y {group_by}',
                labels={'hora': 'Hora del día', 'conteo': 'Número de vuelos'}
            )
            # Crear gráfico de barras
            df_bar = df_filtered.groupby(['origen', 'destino']).size().reset_index(name='conteo')
            df_bar = df_bar.sort_values('conteo', ascending=False).head(10)
            bar_chart = px.bar(
                df_bar,
                x='origen',
                y='conteo',
                color='destino',
                title='Top 10 Rutas más frecuentes',
                labels={'conteo': 'Número de vuelos', 'origen': 'Origen', 'destino': 'Destino'}
            )
            # Crear tabla de resumen
            df_summary = df_filtered.groupby(['origen', 'destino']).agg({
                'tiempo_inicial': 'count'
            }).reset_index()
            df_summary.columns = ['Origen', 'Destino', 'Total Vuelos']
            df_summary = df_summary.sort_values('Total Vuelos', ascending=False)
            
            table = go.Figure(data=[go.Table(
                header=dict(values=list(df_summary.columns),
                          fill_color='paleturquoise',
                          align='left'),
                cells=dict(values=[df_summary[col] for col in df_summary.columns],
                         fill_color='lavender',
                         align='left'))
            ])
            return treemap, bar_pistas, bar_anual, pie_aeronaves, line_mensual, \
                   bar_diario, bar_semanal, bar_horario, heatmap, bar_chart, table
    
    def ejecutar_dashboard(self):
        print("Cargando datos...")
        self.df = self.cargar_datos()
        self.df = self.preparar_datos(self.df)
        
        print("Configurando dashboard...")
        self.configurar_layout(self.df)
        self.callback_actualizacion()
        
        print("\nIniciando servidor...")
        self.app.run_server(debug=True)

def main():
    analizador = AnalizadorVuelosInteractivo()
    analizador.ejecutar_dashboard()

if __name__ == "__main__":
    main()