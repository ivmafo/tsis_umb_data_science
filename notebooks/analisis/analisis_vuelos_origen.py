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
from dash.dependencies import Input, Output, State  # Added State import

class AnalizadorVuelosInteractivo:
    def __init__(self, directorio_salida='resultados/analisis_origen'):
        self.directorio_salida = directorio_salida
        self.crear_directorio()
        self.app = dash.Dash(__name__, suppress_callback_exceptions=True)
        self.df = None  # Initialize df attribute
        
    def crear_directorio(self):
        """Crea el directorio de salida si no existe"""
        import os
        if not os.path.exists(self.directorio_salida):
            os.makedirs(self.directorio_salida)
            
    def cargar_datos(self):
        """Carga los datos desde la base de datos PostgreSQL con optimizaciones"""
        try:
            # Configuración de la conexión
            db_params = {
                'user': 'postgres',
                'password': 'Iforero2011.',
                'host': 'localhost',
                'port': '5432',
                'database': 'flights'
            }
            
            connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
            engine = create_engine(connection_string)
            
            # Verificar conexión y tablas disponibles
            with engine.connect() as conn:
                # Listar tablas disponibles
                tables_query = """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """
                tables = pd.read_sql(tables_query, conn)
                print("Tablas disponibles:", tables['table_name'].tolist())

                # Optimizar la consulta SQL
                query = """
                    SELECT 
                        tiempo_inicial, origen, destino, empresa, nivel, 
                        tipo_aeronave, callsign
                    FROM public.fligths
                    WHERE tiempo_inicial IS NOT NULL
                    ORDER BY tiempo_inicial DESC
                """
                print("Conexión exitosa a la base de datos")
                df = pd.read_sql(query, conn)
                print(f"Datos cargados exitosamente: {len(df)} registros")
                return df
                
        except Exception as e:
            print(f"Error al cargar datos: {str(e)}")
            print("\nVerifique que:")
            print("1. PostgreSQL está en ejecución")
            print("2. Las credenciales son correctas")
            print("3. La base de datos 'flights' existe")
            print("4. La tabla 'fligths' existe y tiene los campos correctos")
            print("\nSi el error persiste, verifique el nombre correcto de la tabla en la base de datos.")
            return pd.DataFrame()
    def preparar_datos(self, df):
        """Prepara los datos con optimizaciones de memoria"""
        if df.empty:
            return df
            
        print("Preparando datos...")
        print(f"Registros iniciales: {len(df)}")
        
        # Verificar valores nulos
        print("\nValores nulos por columna:")
        print(df.isnull().sum())
        
        # Optimizar tipos de datos
        categorical_columns = ['origen', 'destino', 'empresa', 'tipo_aeronave', 'callsign']
        for col in categorical_columns:
            if col in df.columns:
                # Reemplazar valores nulos en columnas categóricas
                df[col] = df[col].fillna('No especificado')
                df[col] = pd.Categorical(df[col])
                print(f"\nValores únicos en {col}: {len(df[col].unique())}")

        # Procesar fechas eficientemente
        df['tiempo_inicial'] = pd.to_datetime(df['tiempo_inicial'])
        df['fecha'] = df['tiempo_inicial'].dt.date
        df['hora'] = df['tiempo_inicial'].dt.hour
        df['dia_semana'] = pd.Categorical(df['tiempo_inicial'].dt.day_name())
        df['mes'] = pd.Categorical(df['tiempo_inicial'].dt.month_name())
        df['año'] = df['tiempo_inicial'].dt.year
        df['trimestre'] = df['tiempo_inicial'].dt.quarter

        # Manejar valores nulos en nivel
        df['nivel'] = df['nivel'].fillna(df['nivel'].mean())
        df['nivel'] = df['nivel'].astype('float32')
        
        print(f"\nRegistros finales: {len(df)}")
        return df
    def configurar_layout(self, df):
        def safe_sort(values):
            # Convert to integers for year values
            try:
                return sorted(set([int(x) for x in values if pd.notna(x)]))
            except:
                return sorted(set([str(x) for x in values if pd.notna(x)]))
        
        self.app.layout = html.Div([
            html.H1('Análisis de Vuelos por Origen'),
            html.Div([
                html.P('Seleccione los filtros y presione "Actualizar" para visualizar los datos',
                      style={'color': '#666', 'marginBottom': '20px'}),
                
                html.Label('Año:'),
                dcc.Dropdown(
                    id='año-dropdown',
                    options=[{'label': str(año), 'value': año} 
                            for año in safe_sort(df['año'].unique())],
                    value=None,
                    multi=True
                ),
                
                html.Label('Trimestre:'),
                dcc.Dropdown(
                    id='trimestre-dropdown',
                    options=[{'label': str(t), 'value': t} 
                            for t in safe_sort(df['trimestre'].unique())],
                    value=None,
                    multi=True
                ),
                
                html.Label('Origen:'),
                dcc.Dropdown(
                    id='origen-dropdown',
                    options=[{'label': str(o), 'value': o} 
                            for o in safe_sort(df['origen'].unique())],
                    value=None,
                    multi=True
                ),
                
                html.Label('Destino:'),
                dcc.Dropdown(
                    id='destino-dropdown',
                    options=[{'label': str(d), 'value': d} 
                            for d in safe_sort(df['destino'].unique())],
                    value=None,
                    multi=True
                ),
                
                html.Label('Empresa:'),
                dcc.Dropdown(
                    id='empresa-dropdown',
                    options=[{'label': str(e), 'value': e} 
                            for e in safe_sort(df['empresa'].unique())],
                    value=None,
                    multi=True
                ),
                
                html.Label('Nivel:'),
                dcc.RangeSlider(
                    id='nivel-slider',
                    min=0,
                    max=100000,
                    step=1000,
                    marks={i: str(i) for i in range(0, 100001, 10000)},
                    value=[0, 100000]
                ),
                
                html.Label('Agrupar por:'),
                dcc.Dropdown(
                    id='group-by-dropdown',
                    options=[
                        {'label': 'Origen', 'value': 'origen'},
                        {'label': 'Destino', 'value': 'destino'},
                        {'label': 'Empresa', 'value': 'empresa'},
                        {'label': 'Tipo de Aeronave', 'value': 'tipo_aeronave'}
                    ],
                    value='origen'
                ),
                
                html.Button(
                    'Actualizar', 
                    id='update-button', 
                    n_clicks=0,
                    style={
                        'backgroundColor': '#007bff',
                        'color': 'white',
                        'padding': '10px 20px',
                        'margin': '20px 0',
                        'border': 'none',
                        'borderRadius': '5px',
                        'cursor': 'pointer'
                    }
                )
            ], style={
                'width': '30%', 
                'display': 'inline-block', 
                'vertical-align': 'top',
                'padding': '20px',
                'backgroundColor': '#f8f9fa',
                'borderRadius': '5px'
            }),
            
            # Single graph container
            # Graph containers
            html.Div([
                # First row with treemaps
                html.Div([
                    # Origin Treemap
                    html.Div([
                        html.H3('Vuelos por Origen'),
                        dcc.Loading(
                            id="loading-treemap-origin",
                            type="circle",
                            children=[dcc.Graph(id='treemap-origin', figure={})]
                        )
                    ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    
                    # Destination Treemap
                    html.Div([
                        html.H3('Vuelos por Destino'),
                        dcc.Loading(
                            id="loading-treemap-dest",
                            type="circle",
                            children=[dcc.Graph(id='treemap-dest', figure={})]
                        )
                    ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'})
                ]),
                
                # Second row with pie chart and bar chart
                html.Div([
                    # Pie chart for companies
                    html.Div([
                        html.H3('Distribución por Empresa'),
                        dcc.Loading(
                            id="loading-pie-empresa",
                            type="circle",
                            children=[dcc.Graph(id='pie-empresa', figure={})]
                        )
                    ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    
                    # Bar chart for aircraft types
                    html.Div([
                        html.H3('Distribución por Tipo de Aeronave'),
                        dcc.Loading(
                            id="loading-bar-aeronave",
                            type="circle",
                            children=[dcc.Graph(id='bar-aeronave', figure={})]
                        )
                    ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'})
                ], style={'marginTop': '20px'})
            ], style={'width': '70%', 'display': 'inline-block', 'verticalAlign': 'top'})
        ])
    def callback_actualizacion(self):
        @self.app.callback(
            [Output('treemap-origin', 'figure'),
             Output('treemap-dest', 'figure'),
             Output('pie-empresa', 'figure'),
             Output('bar-aeronave', 'figure')],
            [Input('update-button', 'n_clicks')],
            [State('año-dropdown', 'value'),
             State('trimestre-dropdown', 'value'),
             State('origen-dropdown', 'value'),
             State('destino-dropdown', 'value'),
             State('empresa-dropdown', 'value'),
             State('nivel-slider', 'value')]
        )
        def update_output(n_clicks, año, trimestre, origenes, destinos, 
                         empresas, nivel_range):
            if n_clicks == 0:
                return {}, {}, {}, {}
            
            nivel_min, nivel_max = nivel_range if nivel_range else (None, None)
            return self.update_treemaps(n_clicks, año, trimestre, origenes, 
                                      destinos, empresas, nivel_min, nivel_max)
    def update_treemaps(self, n_clicks, año, trimestre, origenes, destinos, empresas, nivel_min, nivel_max):
        try:
            df_filtered = self.df.copy()
            
            if año and len(año) > 0:
                # Convert años to integers if they're strings
                años_int = [int(a) if isinstance(a, str) else a for a in año]
                df_filtered = df_filtered[df_filtered['año'].isin(años_int)]
                print(f"Después de filtrar por años {años_int}: {len(df_filtered)} registros")
            
            if trimestre and len(trimestre) > 0:
                df_filtered = df_filtered[df_filtered['trimestre'].isin(trimestre)]
                print(f"Después de filtrar por trimestres {trimestre}: {len(df_filtered)} registros")
            if origenes:
                df_filtered = df_filtered[df_filtered['origen'].isin(origenes)]
            if destinos:
                df_filtered = df_filtered[df_filtered['destino'].isin(destinos)]
            if empresas:
                df_filtered = df_filtered[df_filtered['empresa'].isin(empresas)]
            if nivel_min is not None and nivel_max is not None:
                df_filtered = df_filtered[
                    (df_filtered['nivel'] >= nivel_min) & 
                    (df_filtered['nivel'] <= nivel_max)
                ]

            if len(df_filtered) == 0:
                print("No hay datos para los filtros seleccionados")
                return {}, {}, {}, {}

            # Create counts
            origin_counts = df_filtered['origen'].value_counts().reset_index()
            origin_counts.columns = ['origen', 'count']
            
            dest_counts = df_filtered['destino'].value_counts().reset_index()
            dest_counts.columns = ['destino', 'count']
            
            empresa_counts = df_filtered['empresa'].value_counts().reset_index()
            empresa_counts.columns = ['empresa', 'count']
            
            # Add aircraft type counts
            aeronave_counts = df_filtered['tipo_aeronave'].value_counts().reset_index()
            aeronave_counts.columns = ['tipo_aeronave', 'count']

            # Create origin treemap
            treemap_origin = px.treemap(
                origin_counts,
                path=['origen'],
                values='count',
                title=f'Distribución por Origen ({len(df_filtered)} vuelos)'
            )
            treemap_origin.update_traces(
                textinfo="label+value",
                hovertemplate='<b>%{label}</b><br>Vuelos: %{value}<extra></extra>'
            )
            treemap_origin.update_layout(
                height=500,
                uniformtext=dict(minsize=12),
                clickmode='event+select',
                dragmode=False,
                showlegend=False
            )

            # Create destination treemap
            treemap_dest = px.treemap(
                dest_counts,
                path=['destino'],
                values='count',
                title=f'Distribución por Destino ({len(df_filtered)} vuelos)'
            )
            treemap_dest.update_traces(
                textinfo="label+value",
                hovertemplate='<b>%{label}</b><br>Vuelos: %{value}<extra></extra>'
            )
            treemap_dest.update_layout(
                height=500,
                uniformtext=dict(minsize=12),
                clickmode='event+select',
                dragmode=False,
                showlegend=False
            )

            # Create pie chart for companies
            pie_empresa = px.pie(
                empresa_counts,
                values='count',
                names='empresa',
                title=f'Distribución de Vuelos por Empresa ({len(df_filtered)} vuelos)',
                hole=0.3  # Creates a donut chart effect
            )
            pie_empresa.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Vuelos: %{value}<br>Porcentaje: %{percent}<extra></extra>'
            )
            pie_empresa.update_layout(
                height=400,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.5,
                    xanchor="center",
                    x=0.5
                )
            )

            # Create bar chart for aircraft types
            bar_aeronave = px.bar(
                aeronave_counts,
                x='tipo_aeronave',
                y='count',
                title=f'Distribución por Tipo de Aeronave ({len(df_filtered)} vuelos)',
                labels={'count': 'Número de Vuelos', 'tipo_aeronave': 'Tipo de Aeronave'}
            )
            bar_aeronave.update_traces(
                hovertemplate='<b>%{x}</b><br>Vuelos: %{y}<extra></extra>'
            )
            bar_aeronave.update_layout(
                height=600,
                xaxis_tickangle=-45,
                showlegend=False,
                margin=dict(b=100)  # Add bottom margin for rotated labels
            )

            return treemap_origin, treemap_dest, pie_empresa, bar_aeronave
            
        except Exception as e:
            print(f"Error al actualizar gráficos: {str(e)}")
            return {}, {}, {}, {}
    def ejecutar_dashboard(self):
        try:
            print("Cargando datos...")
            self.df = self.cargar_datos()
            print(f"Shape of loaded data: {self.df.shape}")
            self.df = self.preparar_datos(self.df)
            print(f"Shape after preparation: {self.df.shape}")
            
            if self.df.empty:
                print("Error: No se pudieron cargar los datos")
                return
                
            print(f"Datos cargados: {len(self.df)} registros")
            print("Configurando dashboard...")
            self.configurar_layout(self.df)
            self.callback_actualizacion()
            
            print("\nIniciando servidor...")
            self.app.run_server(debug=True, port=8050)
        except Exception as e:
            print(f"Error al ejecutar el dashboard: {str(e)}")

def main():
    analizador = AnalizadorVuelosInteractivo()
    analizador.ejecutar_dashboard()

if __name__ == "__main__":
    main()