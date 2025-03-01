import pandas as pd
from sqlalchemy import create_engine
import requests
from collections import Counter

def conectar_bd():
    """Conecta a la base de datos PostgreSQL"""
    return create_engine('postgresql://postgres:Iforero2011.@localhost:5432/flights')

def obtener_tipos_aeronaves():
    """Obtiene todos los tipos únicos de aeronaves y vuelos"""
    engine = conectar_bd()
    query = """
        SELECT DISTINCT tipo_aeronave, tipo_vuelo, COUNT(*) as frecuencia
        FROM public.fligths
        GROUP BY tipo_aeronave, tipo_vuelo
        ORDER BY frecuencia DESC
    """
    return pd.read_sql_query(query, engine)

def consultar_api_aircraft(tipo_aeronave):
    """Consulta información de la aeronave en AviationStack API"""
    url = "http://api.aviationstack.com/v1/aircraft_types"
    params = {
        'access_key': '92a5023676fe2188b6a578bfa5805607',  # Registrarse en aviationstack.com para obtener key gratuita
        'search': tipo_aeronave
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['data']:
                aircraft_info = data['data'][0]
                return {
                    "type": tipo_aeronave,
                    "category": aircraft_info.get('aircraft_type', 'No disponible'),
                    "mtow": aircraft_info.get('max_takeoff_weight', 'No disponible'),
                    "engine_type": aircraft_info.get('engine_type', 'No disponible')
                }
        return {"type": tipo_aeronave, "category": "No disponible"}
    except Exception as e:
        print(f"Error consultando API para {tipo_aeronave}: {str(e)}")
        return {"type": tipo_aeronave, "category": "Error en consulta"}

def analizar_tipos():
    # Obtener datos de la base
    df = obtener_tipos_aeronaves()
    
    print("\n=== ANÁLISIS DE TIPOS DE AERONAVES Y VUELOS ===")
    print("\nTipos de aeronaves encontrados:")
    print(df.groupby('tipo_aeronave')['frecuencia'].sum().sort_values(ascending=False))
    
    print("\nTipos de vuelos encontrados:")
    print(df.groupby('tipo_vuelo')['frecuencia'].sum())
    
    # Crear un DataFrame para almacenar la información de la API
    resultados_api = []
    
    print("\nConsultando información detallada de aeronaves en API...")
    for tipo in df['tipo_aeronave'].unique():
        info = consultar_api_aircraft(tipo)
        resultados_api.append({
            'tipo_aeronave': info['type'],
            'categoria_api': info['category'],
            'mtow': info.get('mtow', 'No disponible'),
            'tipo_motor': info.get('engine_type', 'No disponible'),
            'frecuencia_uso': df[df['tipo_aeronave'] == tipo]['frecuencia'].sum()
        })
    
    # Convertir resultados a DataFrame para análisis
    df_resultados = pd.DataFrame(resultados_api)
    
    print("\nResumen de categorías según API:")
    print(df_resultados.groupby('categoria_api')['frecuencia_uso'].sum().sort_values(ascending=False))
    
    print("\nDetalle por tipo de aeronave:")
    print(df_resultados[['tipo_aeronave', 'categoria_api', 'mtow', 'tipo_motor', 'frecuencia_uso']])
if __name__ == "__main__":
    try:
        analizar_tipos()
    except Exception as e:
        print(f"Error durante la ejecución: {str(e)}")