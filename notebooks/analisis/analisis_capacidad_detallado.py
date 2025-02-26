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

def calcular_metricas_detalladas(df):
    """
    Calcula métricas detalladas: SCV, TPS, SCV por nivel, TFC por fecha
    """
    # Preparar datos
    df['tiempo_inicial'] = pd.to_datetime(df['tiempo_inicial'])
    df['fecha'] = df['tiempo_inicial'].dt.date
    df['hora'] = df['tiempo_inicial'].dt.hour
    df = df.sort_values('tiempo_inicial')
    
    # Configurar parámetros
    FACTOR_PLANEACION = 1.3
    ventana = 60
    
    # Inicializar listas para almacenar resultados
    resultados = []
    
    # Agrupar por fecha y nivel de vuelo
    for fecha in df['fecha'].unique():
        df_fecha = df[df['fecha'] == fecha]
        
        for hora in range(24):
            df_hora = df_fecha[df_fecha['hora'] == hora]
            
            if len(df_hora) > 0:
                # Calcular TPS por nivel de vuelo
                niveles = df_hora['nivel_vuelo'].unique() if 'nivel_vuelo' in df_hora.columns else ['NA']
                
                for nivel in niveles:
                    df_nivel = df_hora[df_hora['nivel_vuelo'] == nivel] if nivel != 'NA' else df_hora
                    
                    # TPS - Tiempo promedio en el sector
                    tps = df_nivel['duracion'].mean() if 'duracion' in df_nivel.columns else 30
                    
                    # TFC - Tiempo en funciones de control
                    n_vuelos = len(df_nivel)
                    tfc = 15 * (1 + (n_vuelos / 10))  # Ajuste dinámico según número de vuelos
                    
                    # Cálculo del SCV
                    scv = tps / (tfc * FACTOR_PLANEACION)
                    
                    resultados.append({
                        'fecha': fecha,
                        'hora': hora,
                        'nivel_vuelo': nivel,
                        'n_vuelos': n_vuelos,
                        'tps': tps,
                        'tfc': tfc,
                        'scv': scv
                    })
    
    return pd.DataFrame(resultados)

def generar_reportes(df_metricas):
    """
    Genera reportes y visualizaciones de las métricas
    """
    # 1. Reporte por fecha
    reporte_fecha = df_metricas.groupby('fecha').agg({
        'scv': ['mean', 'max', 'min'],
        'tps': 'mean',
        'tfc': 'mean',
        'n_vuelos': 'sum'
    }).round(2)
    
    # 2. Reporte por nivel de vuelo
    reporte_nivel = df_metricas.groupby(['fecha', 'nivel_vuelo']).agg({
        'scv': 'mean',
        'tps': 'mean',
        'n_vuelos': 'sum'
    }).round(2)
    
    # Guardar reportes
    reporte_fecha.to_excel('resultados/reporte_diario.xlsx')
    reporte_nivel.to_excel('resultados/reporte_por_nivel.xlsx')
    
    # Visualizaciones
    plt.figure(figsize=(15, 8))
    sns.boxplot(data=df_metricas, x='fecha', y='scv')
    plt.title('Distribución de SCV por Fecha')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('resultados/scv_distribucion_fecha.png')
    plt.close()
    
    return reporte_fecha, reporte_nivel

def main():
    # Crear directorio para resultados
    import os
    if not os.path.exists('resultados'):
        os.makedirs('resultados')

    # Cargar datos
    print("Cargando datos...")
    df = conectar_bd()
    
    # Calcular métricas
    print("Calculando métricas detalladas...")
    df_metricas = calcular_metricas_detalladas(df)
    
    # Generar reportes
    print("\nGenerando reportes...")
    reporte_fecha, reporte_nivel = generar_reportes(df_metricas)
    
    # Mostrar resumen
    print("\nResumen por fecha:")
    print(reporte_fecha)
    
    print("\nAnálisis completado. Los resultados se han guardado en la carpeta 'resultados'")

if __name__ == "__main__":
    main()