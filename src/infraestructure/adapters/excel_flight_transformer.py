import pandas as pd
from datetime import datetime, time

class ExcelFlightTransformer:
    def __init__(self, file_path):
        self.file_path = file_path

    def transform_flights(self):
        column_mapping = {
            "fecha": ["Fecha", "fecha"],
            "sid": ["id","ID","sid","SID"],
            "ssr": ["SSR"],
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
            "hora_pv": ["Hora PV"],
            "destino": ["destino", "Destino"],
            "fecha_llegada": ["fecha_llegada", "Fec Lle", "Fecha de Llegada"],
            "hora_llegada": ["hora_llegada", "Hr Lle", "Hora de Llegada"],
            "nivel": ["nivel", "Nivel"],
            "duracion": ["duracion", "Duración"],
            "distancia": ["distancia", "Distancia"],
            "velocidad": ["velocidad", "Velocidad"],
            "eq_ssr": ["Eq SSR"],
            "nombre_origen": ["nombre_origen", "Nombre origen ZZZZ", "Nombre Origen"],
            "nombre_destino": ["nombre_destino", "Nombre destino ZZZZ", "Nombre Destino"],
            "fecha_registro": ["Fecha de Registro"]
        }

        df = pd.read_excel(self.file_path)

        for new_name, old_names in column_mapping.items():
            for old_name in old_names:
                if old_name in df.columns:
                    df.rename(columns={old_name: new_name}, inplace=True)
                    break

        print(df.head())

        flights = []
        for _, row in df.iterrows():
            flight_data = {}
            try: 
                # Validar y formatear cada campo individualmente, manejando NaN y None
                flight_data['fecha'] = self.safe_get_date(row, 'fecha')         
                flight_data['sid'] = self.safe_get_int(row, 'sid')
                flight_data['ssr'] = self.safe_get_int(row,'ssr')                       
                flight_data['callsign'] = self.safe_get_str(row, 'callsign')
                flight_data['matricula'] = self.safe_get_str(row, 'matricula')
                flight_data['tipo_aeronave'] = self.safe_get_str(row, 'tipo_aeronave')
                flight_data['empresa'] = self.safe_get_str(row, 'empresa')
                flight_data['numero_vuelo'] = self.safe_get_int(row, 'numero_vuelo')
                flight_data['tipo_vuelo'] = self.safe_get_str(row, 'tipo_vuelo')
                flight_data['tiempo_inicial'] = self.safe_get_datetime(row, 'tiempo_inicial')
                flight_data['origen'] = self.safe_get_str(row, 'origen')
                flight_data['fecha_salida'] = self.safe_get_date(row, 'fecha_salida')
                flight_data['hora_salida'] = self.safe_get_time(row, 'hora_salida')
                #flight_data['hora_pv'] =self.safe_get_time_as_datetime(row, 'hora_pv', flight_data['fecha_salida'])
                flight_data['hora_pv'] = self.safe_get_time(row, 'hora_pv')
                flight_data['destino'] = self.safe_get_str(row, 'destino')
                flight_data['fecha_llegada'] = self.safe_get_date(row, 'fecha_llegada')
                flight_data['hora_llegada'] = self.safe_get_time(row, 'hora_llegada')
                flight_data['nivel'] = self.safe_get_int(row, 'nivel')
                flight_data['duracion'] = self.safe_get_int(row, 'duracion')
                flight_data['distancia'] = self.safe_get_int(row, 'distancia')
                flight_data['velocidad'] = self.safe_get_int(row, 'velocidad')
                flight_data['eq_ssr'] = self.safe_get_str(row, 'eq_ssr')
                flight_data['nombre_origen'] = self.safe_get_str(row, 'nombre_origen')
                flight_data['nombre_destino'] = self.safe_get_str(row, 'nombre_destino')
                flight_data['fecha_registro'] = self.safe_get_date(row, 'fecha_registro')

                flights.append(flight_data)
                #print(flights)
            except Exception as e:
                print(f"Error general al procesar la fila: {row}. Error: {str(e)}")
                # Si quieres detener el procesamiento en un error, puedes usar 'break' aquí.
                # Si quieres continuar con las siguientes filas a pesar del error, no uses 'break'.
                # break  # Descomenta para detener el procesamiento en el primer error.

        return flights

    def safe_get_date(self, row, column_name):
        date_str = row.get(column_name)
        if pd.isna(date_str) or date_str is None or str(date_str).lower() == 'nan' or not date_str:
            return None
        return self.validar_y_formatear_fecha(str(date_str))

    def safe_get_time_as_time(self, row, column_name):
        time_str = row.get(column_name)
        if pd.isna(time_str) or time_str is None or str(time_str).lower() == 'nan' or not time_str:
            return None
        return self.convertir_hora(str(time_str))



    def safe_get_time(self, row, column_name):
        time_str = row.get(column_name)
        if pd.isna(time_str) or time_str is None or str(time_str).lower() == 'nan' or not time_str:
            return None
        return self.convertir_hora(str(time_str))

    def safe_get_int(self, row, column_name):
        value = row.get(column_name)
        if pd.isna(value) or value is None or str(value).lower() == 'nan' or not value:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            print(f"Valor no válido para {column_name}: {value}")
            return None

    def safe_get_str(self, row, column_name):
        value = row.get(column_name)
        if pd.isna(value) or value is None or str(value).lower() == 'nan' or not value:
            return None
        return str(value)

    def safe_get_datetime(self, row, column_name):        
        value = row.get(column_name)
        value = str(value).replace(".0","")
        if pd.isna(value) or value is None or str(value).lower() == 'nan'or not value:
            return None
        try:
            return pd.to_datetime(value)
        except (ValueError, TypeError):
            print(f"Valor no válido para {column_name}: {value}")
            return None

    def validar_y_formatear_fecha(self, fecha_str):
        fecha_str = str(fecha_str).replace(".0","")

        if pd.isna(fecha_str) or fecha_str is None or str(fecha_str).lower() == 'nan' or not fecha_str:
            return None 

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
            return fecha
        except ValueError:
            pass #Si no tiene este formato, continua con las validaciones anteriores

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d') #Prueba este formato
            return fecha
        except ValueError:
            pass

        if len(fecha_str) == 6:  # Formato DDMMYY
            fecha = datetime.strptime(fecha_str, '%d%m%y')
        elif len(fecha_str) == 5:  # Formato DMMYY (ejemplo: "10919")
            dia = int(fecha_str[:1])
            mes = int(fecha_str[1:3])
            anio = int("20" + fecha_str[3:])  # Asume el siglo XXI
            fecha = datetime(anio, mes, dia)
        elif len(fecha_str) == 4: # Formato MMYY
            mes = int(fecha_str[:2])
            anio = int("20" + fecha_str[2:])  # Asume el siglo XXI
            fecha = datetime(anio, mes, 1) #Asume el dia 1
        elif len(fecha_str) == 3: # Formato DMY
            dia = int(fecha_str[:1]) 
            mes = int(fecha_str[1:2])
            anio = int("20" + fecha_str[2:])  # Asume el siglo XXI
            fecha = datetime(anio, mes, dia)
        elif len(fecha_str) == 2: # Formato MY
            mes = int(fecha_str[:2])
            anio = 2000 + int(fecha_str[0:])
            fecha = datetime(anio, mes, 1) #Asume el dia 1
        else:
            fecha
            raise ValueError(f"Formato de fecha no válido: {fecha_str}")

        return fecha

    def convertir_hora(self, hora_str):
        hora_str = str(hora_str).replace(".0","")
        if pd.isna(hora_str):  # Verifica NaN al inicio de la función
            return None

        if hora_str is None: # Verifica si es None
            return None

        hora_str = str(hora_str) # Convierte a string antes de operar

        try:
            if len(hora_str) == 4:  # Si la cadena tiene 4 dígitos (HHMM)
                hora = time(int(hora_str[:2]), int(hora_str[2:]))
            elif len(hora_str) == 3:  # Si la cadena tiene 3 dígitos (HMM)
                hora = time(int(hora_str[:1]), int(hora_str[1:]))
            elif len(hora_str) == 2:  # Si la cadena tiene 2 dígitos (MM)
                hora = time(0, int(hora_str[0:]))
            elif len(hora_str) > 4 and "." in hora_str: # Si tiene decimales, asumimos que es HHMM.SS
                hora_str = hora_str.split(".")[0] # Nos quedamos con la parte entera
                hora = time(int(hora_str[:2]), int(hora_str[2:]))
            elif len(hora_str) < 2 and "." in hora_str: # Si tiene decimales, asumimos que son los minutos
                hora_str = hora_str.split(".")[0] # Nos quedamos con la parte entera
                hora = time(0, int(hora_str))
            else:
                try: # Intenta convertirlo a datetime, en caso de que ya tenga un formato válido
                    hora = pd.to_datetime(hora_str).time()
                except:
                    return  None
                    # raise ValueError(f"Formato de hora no válido: {hora_str}")  # Lanza una excepción si el formato no es válido
            return hora
        except ValueError as e:
            print(f"Error al convertir la hora: {hora_str}. Error: {e}")
            return None  # O devuelve un valor predeterminado

    def safe_get_time_as_datetime(self, row, column_name, base_date):
        time_str = row.get(column_name)
        if pd.isna(time_str) or time_str is None or str(time_str).lower() == 'nan' or not time_str:
            return None
        try:
            time_value = self.convertir_hora(str(time_str))
            if time_value:
                if base_date:
                    return datetime.combine(base_date, time_value)
                else:
                    # Si base_date es None, usar una fecha por defecto, por ejemplo la fecha actual
                    return datetime.combine(datetime.now().date(), time_value)
            else:
                return None
        except Exception as e:
            print(f"Error al convertir {column_name}: {time_str}. Error: {str(e)}")
            return None
        
    def convertir_hora(self, hora_str):
        hora_str = str(hora_str).replace(".0", "")
        if pd.isna(hora_str) or hora_str is None or hora_str.strip() == '':
            return None

        try:
            if len(hora_str) == 4:  # Si la cadena tiene 4 dígitos (HHMM)
                return time(int(hora_str[:2]), int(hora_str[2:]))
            elif len(hora_str) == 3:  # Si la cadena tiene 3 dígitos (HMM)
                return time(int(hora_str[:1]), int(hora_str[1:]))
            elif len(hora_str) == 2:  # Si la cadena tiene 2 dígitos (MM)
                return time(0, int(hora_str))
            elif len(hora_str) > 4 and "." in hora_str:  # Si tiene decimales, asumimos que es HHMM.SS
                hora_str = hora_str.split(".")[0]
                return time(int(hora_str[:2]), int(hora_str[2:]))
            elif len(hora_str) < 2 and "." in hora_str:  # Si tiene decimales, asumimos que son los minutos
                hora_str = hora_str.split(".")[0]
                return time(0, int(hora_str))
            else:
                # Manejar otros formatos posibles
                return pd.to_datetime(hora_str).time()
        except ValueError as e:
            print(f"Error al convertir la hora: {hora_str}. Error: {e}")
            return None  # O devuelve un valor predeterminado