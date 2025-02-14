# pylint: disable=syntax-error
# tsis_umb_data_science/src/infraestructure/adapters/excel_flight_transformer.py
import pandas as pd
from datetime import datetime, time
from pathlib import Path

class ExcelFlightTransformer:
    def __init__(self, file_path):
        self.file_path = file_path

    def transform_flights(self):
        # diccionario de listas de posibles nombres de columnas 
        column_mapping = {
            "sid":["id","ID","id"],
            "callsign": ["callsign", "Callsign", "Call sign", "call-sign", "CallSign"],
            "matricula": ["matricula", "Matrícula"],
            "tipo_aeronave": ["tipo_aeronave", "Tip Aer", "Tipo Aeronave"],
            "empresa": ["empresa", "Empresa"],
            "numero_vuelo": ["numero_vuelo", "# Vuelo", "Numero de Vuelo"],
            "tipo_vuelo": ["tipo_vuelo", "Tip Vuel", "Tipo de Vuelo"],
            "tiempo_inicial": ["tiempo_inicial", "Tiempo Inicial"],
            "origen": ["origen", "Origen"],
            "fecha_salida": ["fecha_salida", "Fec Sal", "Fecha de Salida"],
            "hora_salida": ["hora_salida", "Hr Sal", "Hora de Salida"],
            "destino": ["destino", "Destino"],
            "fecha_llegada": ["fecha_llegada", "Fec Lle", "Fecha de Llegada"],
            "hora_llegada": ["hora_llegada", "Hr Lle", "Hora de Llegada"],
            "nivel": ["nivel", "Nivel"],
            "nombre_origen": ["nombre_origen", "Nombre origen ZZZZ", "Nombre Origen"],
            "nombre_destino": ["nombre_destino", "Nombre destino ZZZZ", "Nombre Destino"]
        }
         
        df = pd.read_excel(self.file_path)

                # Renombrar las columnas basadas en el mapeo
        for new_name, old_names in column_mapping.items():
            for old_name in old_names:
                if old_name in df.columns:
                    df.rename(columns={old_name: new_name}, inplace=True)
                    break

        # verificar encabezado            
        print(df.head())
    
        flights = []
        for _, row in df.iterrows():
            # Estandarizar campos y manejar campos adicionales
            # Obtener fecha y hora de salida y llegada
            try:
                fecha_salida_str = str(row.get('fecha_salida', ''))
                if (len(fecha_salida_str)==6):
                    fecha_salida = datetime.strptime(fecha_salida_str, '%d%m%y')
                else:
                    fecha_salida = pd.to_datetime(row.get('fecha_salida', datetime.now().date()))
                    
                hora_salida = row.get('hora_salida', datetime.now().time())
                if not isinstance(hora_salida, time):
                    hora_salida = pd.to_datetime(hora_salida).time()

                #if not isinstance(hora_salida, time):
                #    hora_salida = pd.to_datetime(hora_salida).time()

                #fecha_llegada = pd.to_datetime(row.get('fecha_llegada', datetime.now().date()))
                fecha_llegada_str = str(row.get('fecha_llegada', ''))
                if (len(fecha_llegada_str) == 6):
                    fecha_llegada = datetime.strptime(fecha_llegada_str, '%d%m%y')
                else:
                    fecha_llegada = pd.to_datetime(row.get('fecha_llegada', datetime.now().date()))



                hora_llegada = row.get('hora_llegada', datetime.now().time())
                if not isinstance(hora_llegada, time):
                    hora_llegada = pd.to_datetime(hora_llegada).time()

                # Combinar fecha y hora en un objeto datetime
                datetime_salida = datetime.combine(fecha_salida.date(), hora_salida)
                datetime_llegada = datetime.combine(fecha_llegada.date(), hora_llegada)

                flight_data = {
                    "sid": int(row.get('sid',0)),
                    "callsign": row.get('callsign', ''),
                    "matricula": row.get('matricula', ''),
                    "tipo_aeronave": row.get('tipo_aeronave', ''),
                    "empresa": row.get('empresa', ''),
                    "numero_vuelo": str(row.get('numero_vuelo', '0')),
                    "tipo_vuelo": row.get('tipo_vuelo', ''),
                    "tiempo_inicial": pd.to_datetime(row.get('tiempo_inicial', datetime.now())),
                    "origen": row.get('origen', ''),
                    "pista_origen": row.get('pista_origen', ''),
                    "sid": str(row.get('sid', '0')),
                    "fecha_salida": fecha_salida,
                    "hora_salida": datetime_salida,
                    "destino": row.get('destino', ''),
                    "pista_destino": row.get('pista_destino', '0'),
                    "fecha_llegada": fecha_llegada,
                    "hora_llegada": datetime_llegada,
                    "nivel": int(row.get('nivel', 0)),
                    "ambito": row.get('ambito', ''),
                    "nombre_origen": str(row.get('nombre_origen', '')),
                    "nombre_destino": str(row.get('nombre_destino', ''))
                }
                flights.append(flight_data)
            except Exception as e: 
                print(f"Error al procesar la fila: {row}. Error: {str(e)}")
                print(flights)
        return flights 
