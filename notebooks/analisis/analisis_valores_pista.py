import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sqlalchemy import create_engine

class AnalisisValoresPista:
    def __init__(self):
        self.engine = self.conectar_bd()
        self.tiempos_ocupacion = {
            'aterrizaje': {
                'ligera': 60,  # segundos
                'media': 75,
                'pesada': 90
            },
            'despegue': {
                'ligera': 45,
                'media': 60,
                'pesada': 75
            }
        }
    def conectar_bd(self):
        """
        Establece conexión con la base de datos PostgreSQL
        """
        return create_engine('postgresql://postgres:Iforero2011.@localhost:5432/flights')
    def obtener_datos_operaciones(self, fecha_inicio, fecha_fin, aeropuerto):
        """
        Obtiene datos de operaciones usando SQLAlchemy
        """
        query = """
            SELECT 
                fecha,
                tipo_vuelo,
                tipo_aeronave,
                origen,
                destino,
                hora_salida,
                hora_llegada
            FROM public.fligths
            WHERE fecha BETWEEN %(fecha_inicio)s AND %(fecha_fin)s
                AND (origen = %(aeropuerto)s OR destino = %(aeropuerto)s)
            ORDER BY fecha, hora_salida, hora_llegada
        """
        
        params = {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'aeropuerto': aeropuerto
        }
        
        return pd.read_sql_query(
            query, 
            self.engine, 
            params=params
        )
    def calcular_tiempos_ocupacion(self, df):
        """
        Calcula tiempos de ocupación de pista por tipo de operación
        """
        # Agrupar por tipo de operación y aeronave
        tiempos = df.groupby(['tipo_vuelo', 'tipo_aeronave']).agg({
            'fecha': 'count'  # Contar operaciones
        }).reset_index()
        
        return tiempos
    def analizar_distribucion_horaria(self, df):
        """
        Analiza la distribución horaria de las operaciones
        """
        df['hora'] = pd.to_datetime(df['fecha']).dt.hour
        distribucion = df.groupby('hora').size()
        return distribucion
    def clasificar_aeronave(self, tipo_aeronave):
        """
        Clasifica aeronave según su peso máximo de despegue
        """
        # Implementar clasificación según circular 006
        categorias = {
            'ligera': ['C152', 'C172', 'PA28'],  # ejemplo
            'media': ['A320', 'B737', 'E190'],
            'pesada': ['B747', 'A330', 'B777']
        }
        for categoria, tipos in categorias.items():
            if tipo_aeronave in tipos:
                return categoria
        return 'media'  # default
    def calcular_tiempo_ocupacion_real(self, df):
        """
        Calcula tiempo real de ocupación según tipo de operación y aeronave
        """
        # Crear una copia para evitar modificar el DataFrame original
        df_result = df.copy()
        
        # Clasificar aeronaves
        df_result['categoria'] = df_result['tipo_aeronave'].apply(self.clasificar_aeronave)
        
        # Calcular tiempo de ocupación usando vectorización
        condicion_aterrizaje = df_result['tipo_vuelo'] == 'A'
        
        # Crear arrays de tiempos según el tipo de operación y categoría
        tiempos = np.where(condicion_aterrizaje,
            df_result['categoria'].map(lambda x: self.tiempos_ocupacion['aterrizaje'][x]),
            df_result['categoria'].map(lambda x: self.tiempos_ocupacion['despegue'][x]))
        
        # Asignar los tiempos calculados
        df_result['tiempo_ocupacion'] = tiempos
        
        return df_result
    def calcular_separacion_minima(self, categoria_lider, categoria_seguidor):
        """
        Calcula separación mínima según matriz de la circular 006
        """
        matriz_separacion = {
            ('pesada', 'pesada'): 4,
            ('pesada', 'media'): 5,
            ('pesada', 'ligera'): 6,
            ('media', 'pesada'): 3,
            ('media', 'media'): 3,
            ('media', 'ligera'): 5,
            ('ligera', 'pesada'): 3,
            ('ligera', 'media'): 3,
            ('ligera', 'ligera'): 3
        }
        return matriz_separacion.get((categoria_lider, categoria_seguidor), 3)
    def calcular_capacidad_pista_detallada(self, df):
        """
        Calcula capacidad según metodología de la circular 006
        """
        if len(df) == 0:
            return {
                'capacidad_hora': 0,
                'mix_operaciones': pd.Series(),
                'tiempo_promedio': 0,
                'separacion_promedio': 0
            }
            
        df_ocupacion = self.calcular_tiempo_ocupacion_real(df)
        
        # Calcular mix de operaciones y convertir a DataFrame
        mix_operaciones = (df_ocupacion.groupby(['tipo_vuelo', 'categoria'])
                         .size()
                         .reset_index(name='count'))
        mix_operaciones['proporcion'] = mix_operaciones['count'] / len(df)
        
        # Tiempo promedio de ocupación
        tiempo_promedio = (df_ocupacion['tiempo_ocupacion'] * 
                         df_ocupacion.groupby(['tipo_vuelo', 'categoria'])
                         .size().reset_index(name='count')['count'] / len(df)).sum()
        
        # Separación promedio
        separacion_promedio = 0
        for i, row1 in mix_operaciones.iterrows():
            for j, row2 in mix_operaciones.iterrows():
                separacion = self.calcular_separacion_minima(row1['categoria'], row2['categoria'])
                separacion_promedio += separacion * row1['proporcion'] * row2['proporcion']

        # Capacidad teórica (con manejo de división por cero)
        max_valor = max(tiempo_promedio, separacion_promedio)
        if max_valor > 0:
            capacidad_hora = 3600 / max_valor
        else:
            capacidad_hora = 0
        
        return {
            'capacidad_hora': capacidad_hora,
            'mix_operaciones': mix_operaciones['proporcion'],
            'tiempo_promedio': tiempo_promedio,
            'separacion_promedio': separacion_promedio
        }
    def generar_reporte_completo(self, fecha_inicio, fecha_fin, aeropuerto):
        df = self.obtener_datos_operaciones(fecha_inicio, fecha_fin, aeropuerto)
        
        if len(df) == 0:
            print(f"\nNo se encontraron datos para el aeropuerto {aeropuerto} en el período especificado.")
            return {
                'tiempos': pd.DataFrame(),
                'distribucion': pd.Series(),
                'capacidad_detallada': {
                    'capacidad_hora': 0,
                    'mix_operaciones': pd.Series(),
                    'tiempo_promedio': 0,
                    'separacion_promedio': 0
                }
            }
        
        # Análisis según circular 006
        capacidad_detallada = self.calcular_capacidad_pista_detallada(df)
        
        # Calcular tiempos y distribución
        tiempos = self.calcular_tiempos_ocupacion(df)
        distribucion = self.analizar_distribucion_horaria(df)
        
        # Visualización solo si hay datos
        if len(df) > 0:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Gráfico de tiempos por tipo de operación
            if not tiempos.empty:
                tiempos.plot(kind='bar', ax=ax1)
                ax1.set_title('Tiempos de Ocupación por Tipo de Operación')
                ax1.set_xlabel('Tipo de Operación')
                ax1.set_ylabel('Cantidad de Operaciones')
            
            # Gráfico de distribución horaria
            if not distribucion.empty:
                distribucion.plot(kind='line', ax=ax2)
                ax2.set_title('Distribución Horaria de Operaciones')
                ax2.set_xlabel('Hora del Día')
                ax2.set_ylabel('Número de Operaciones')
            
            plt.tight_layout()
            plt.show()
        
        return {
            'tiempos': tiempos,
            'distribucion': distribucion,
            'capacidad_detallada': capacidad_detallada
        }
    def calcular_TPS(self, tiempo_conflicto, tiempo_coordinacion):
        """
        Calcula el Tiempo Promedio de Sector (TPS)
        """
        return tiempo_conflicto + tiempo_coordinacion
    def calcular_TFC(self, tiempo_comunicacion, numero_comunicaciones):
        """
        Calcula el Tiempo de Fase de Conflicto (TFC)
        """
        return tiempo_comunicacion * numero_comunicaciones
    def calcular_SCV(self, velocidad_crucero, distancia_sector):
        """
        Calcula el Tiempo de Sobrevuelo (SCV)
        """
        return (distancia_sector / velocidad_crucero) * 3600  # convertir a segundos
    def calcular_capacidad_horaria(self, TPS, factor_ocupacion=0.8):
        """
        Calcula la Capacidad Horaria (CH)
        CH = (3600/TPS) * factor_ocupacion
        """
        return (3600/TPS) * factor_ocupacion
    def calcular_numero_referencia_capacidad(self, TPS, SCV):
        """
        Calcula el Número de Referencia de la Capacidad de Sector (N)
        N = SCV/TPS
        """
        return SCV/TPS
    def analisis_capacidad_sector(self, datos_sector):
        """
        Realiza análisis completo de capacidad de sector
        """
        # Cálculos básicos
        tps = self.calcular_TPS(
            datos_sector['tiempo_conflicto'],
            datos_sector['tiempo_coordinacion']
        )
        
        tfc = self.calcular_TFC(
            datos_sector['tiempo_comunicacion'],
            datos_sector['numero_comunicaciones']
        )
        
        scv = self.calcular_SCV(
            datos_sector['velocidad_crucero'],
            datos_sector['distancia_sector']
        )
        
        # Cálculos derivados
        capacidad_horaria = self.calcular_capacidad_horaria(tps)
        numero_referencia = self.calcular_numero_referencia_capacidad(tps, scv)
        
        return {
            'TPS': tps,
            'TFC': tfc,
            'SCV': scv,
            'capacidad_horaria': capacidad_horaria,
            'numero_referencia': numero_referencia
        }
# Código principal de ejecución
if __name__ == "__main__":
    try:
        # Crear instancia del analizador
        analisis = AnalisisValoresPista()
        
        # Parámetros de análisis
        fecha_inicio = '2000-01-01'
        fecha_fin = '2024-01-07'  # Una semana de análisis
        aeropuerto = 'SKBO'
        
        # Generar reporte
        resultados = analisis.generar_reporte_completo(fecha_inicio, fecha_fin, aeropuerto)
        
        # Imprimir resultados detallados
        print("\n=== REPORTE DE ANÁLISIS DE CAPACIDAD AEROPORTUARIA ===")
        print(f"\nAeropuerto: {aeropuerto}")
        print(f"Período: {fecha_inicio} a {fecha_fin}")
        
        print("\n1. Análisis de Tiempos de Ocupación:")
        print(resultados['tiempos'])
        
        print("\n2. Distribución Horaria de Operaciones:")
        print(resultados['distribucion'])
        
        print("\n3. Capacidad Detallada:")
        cap = resultados['capacidad_detallada']
        print(f"- Capacidad por hora: {cap['capacidad_hora']:.2f} operaciones/hora")
        print(f"- Tiempo promedio de ocupación: {cap['tiempo_promedio']:.2f} segundos")
        print(f"- Separación promedio: {cap['separacion_promedio']:.2f} millas náuticas")
        print("\nMix de Operaciones:")
        print(cap['mix_operaciones'])

        # Análisis de sector
        datos_sector = {
            'tiempo_conflicto': 120,      # segundos
            'tiempo_coordinacion': 60,     # segundos
            'tiempo_comunicacion': 15,     # segundos
            'numero_comunicaciones': 8,
            'velocidad_crucero': 450,      # nudos
            'distancia_sector': 100        # millas náuticas
        }
        
        print("\n4. Análisis de Capacidad de Sector:")
        analisis_sector = analisis.analisis_capacidad_sector(datos_sector)
        print(f"- TPS (Tiempo Promedio Sector): {analisis_sector['TPS']} segundos")
        print(f"- TFC (Tiempo Fase Conflicto): {analisis_sector['TFC']} segundos")
        print(f"- SCV (Tiempo Sobrevuelo): {analisis_sector['SCV']:.2f} segundos")
        print(f"- Capacidad Horaria: {analisis_sector['capacidad_horaria']:.2f} aeronaves/hora")
        print(f"- Número de Referencia: {analisis_sector['numero_referencia']:.2f}")
        
    except Exception as e:
        print(f"\nError durante la ejecución: {str(e)}")