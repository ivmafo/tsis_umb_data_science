import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from datetime import datetime, timedelta

def conectar_bd():
    engine = create_engine('postgresql://postgres:Iforero2011.@localhost:5432/flights')
    query = "SELECT * FROM public.fligths"
    return pd.read_sql(query, engine)

def calcular_scv(df):
    """
    Calcula el Valor de Capacidad del Sector (SCV) según Circular 006
    SCV = TPS/(TFC × 1.3)
    """
    # 1. Preparar datos
    df['tiempo_inicial'] = pd.to_datetime(df['tiempo_inicial'])
    df = df.sort_values('tiempo_inicial')
    
    # 2. Calcular ventanas de tiempo (intervalos de 60 minutos)
    ventana = 60  # minutos
    df['ventana_tiempo'] = df['tiempo_inicial'].dt.floor('H')
    
    # 3. Calcular métricas por ventana
    metricas_ventana = []
    FACTOR_PLANEACION = 1.3  # Factor constante según circular
    
    for ventana_inicio in df['ventana_tiempo'].unique():
        ventana_fin = ventana_inicio + pd.Timedelta(minutes=ventana)
        vuelos_ventana = df[(df['tiempo_inicial'] >= ventana_inicio) & 
                           (df['tiempo_inicial'] < ventana_fin)]
        
        if len(vuelos_ventana) > 0:
            # TPS - Tiempo promedio de vuelo en el Sector
            tps = vuelos_ventana['duracion'].mean() if 'duracion' in vuelos_ventana.columns else 30
            
            # TFC - Tiempo promedio en funciones de control (estimado)
            # Este valor debería ser medido durante 10 días según la circular
            tfc = 15  # Valor ejemplo, debe ser reemplazado por mediciones reales
            
            # Cálculo del SCV según fórmula oficial
            scv = tps / (tfc * FACTOR_PLANEACION)  # Corregido aquí
            
            metricas_ventana.append({
                'ventana_inicio': ventana_inicio,
                'n_vuelos': len(vuelos_ventana),
                'tps': tps,
                'tfc': tfc,
                'scv': scv
            })
    
    return pd.DataFrame(metricas_ventana)

def visualizar_resultados(df_scv):
    # Extraer fecha y hora
    df_scv['fecha'] = df_scv['ventana_inicio'].dt.date
    df_scv['hora'] = df_scv['ventana_inicio'].dt.hour
    
    # 1. Heatmap de capacidad por fecha y hora
    plt.figure(figsize=(20, 10))
    pivot_table = df_scv.pivot_table(
        values='scv', 
        index='hora',
        columns='fecha',
        aggfunc='mean'
    )
    
    sns.heatmap(pivot_table, cmap='YlOrRd', annot=True, fmt='.2f')
    plt.title('Capacidad del Sector (SCV) por Fecha y Hora')
    plt.xlabel('Fecha')
    plt.ylabel('Hora del Día')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('resultados/scv_heatmap_fecha_hora.png')
    plt.close()

def generar_tabla_scv(df_scv):
    """
    Genera una tabla detallada de SCV por fecha y hora
    """
    # Asegurar que tenemos las columnas fecha y hora
    df_scv['fecha'] = df_scv['ventana_inicio'].dt.date
    df_scv['hora'] = df_scv['ventana_inicio'].dt.hour
    
    # Crear tabla pivote con valores de SCV
    tabla_scv = df_scv.pivot_table(
        values='scv',
        index='hora',
        columns='fecha',
        aggfunc='mean'
    ).round(2)
    
    # Agregar promedios
    tabla_scv['Promedio_Hora'] = tabla_scv.mean(axis=1).round(2)
    tabla_scv.loc['Promedio_Fecha'] = tabla_scv.mean().round(2)
    
    # Guardar tabla en diferentes formatos
    tabla_scv.to_csv('resultados/tabla_scv_fecha_hora.csv')
    tabla_scv.to_excel('resultados/tabla_scv_fecha_hora.xlsx')
    
    # Versión HTML con estilo
    html_content = """
    <html>
    <head>
        <style>
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid black; padding: 8px; text-align: right; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            tr:hover { background-color: #f5f5f5; }
        </style>
    </head>
    <body>
    """
    html_content += "<h2>Tabla de SCV por Fecha y Hora</h2>"
    html_content += tabla_scv.to_html()
    html_content += "</body></html>"
    
    with open('resultados/tabla_scv_fecha_hora.html', 'w') as f:
        f.write(html_content)
    
    return tabla_scv

    
# Modificar la función main para incluir la generación de la tabla
def main():
    # Crear directorio para resultados
    import os
    if not os.path.exists('resultados'):
        os.makedirs('resultados')

    # Cargar datos
    print("Cargando datos...")
    df = conectar_bd()
    
    # Calcular SCV
    print("Calculando SCV...")
    df_scv = calcular_scv(df)
    
    # Mostrar resultados estadísticos
    print("\nEstadísticas del SCV:")
    print(df_scv['scv'].describe())
    
    print("\nValores máximos por ventana:")
    max_scv = df_scv.loc[df_scv['scv'].idxmax()]
    print(f"SCV máximo: {max_scv['scv']:.2f}")
    print(f"Fecha/Hora: {max_scv['ventana_inicio']}")
    print(f"Número de vuelos: {max_scv['n_vuelos']}")
    
    # Agregar estadísticas por fecha
    df_scv['fecha'] = df_scv['ventana_inicio'].dt.date
    print("\nEstadísticas de SCV por fecha:")
    stats_fecha = df_scv.groupby('fecha')['scv'].agg(['mean', 'max', 'min', 'count']).round(2)
    print(stats_fecha)
    stats_fecha.to_csv('resultados/estadisticas_scv_por_fecha.csv')
    
    # Generar visualizaciones y tabla
    visualizar_resultados(df_scv)
    tabla_scv = generar_tabla_scv(df_scv)
    print("\nTabla de SCV por fecha y hora (primeras 5 horas):")
    print(tabla_scv.head())
    print("\nAnálisis completado. Los resultados se han guardado en la carpeta 'resultados'")

if __name__ == "__main__":
    main()