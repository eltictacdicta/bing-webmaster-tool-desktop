from datetime import datetime, timedelta

def get_date_limit(range_option):
    if range_option == "Última semana":
        return datetime.now() - timedelta(weeks=1)
    elif range_option == "Últimos 30 días":
        return datetime.now() - timedelta(days=30)
    elif range_option == "Últimos 3 meses":
        return datetime.now() - timedelta(days=90)
    elif range_option == "Últimos 6 meses":
        return datetime.now() - timedelta(days=180)
    else:
        return datetime.now() - timedelta(days=90)  # Por defecto, últimos 3 meses
    
# Función para convertir la fecha del formato '/Date(1705651200000-0800)/' a un objeto datetime
def convertir_fecha_unix(fecha_unix):
    timestamp = int(fecha_unix.split('(')[1].split('-')[0]) / 1000
    return datetime.fromtimestamp(timestamp)

def convertir_fecha(fecha):
    # Extraer la fecha en milisegundos y el desplazamiento de zona horaria
    timestamp_str, offset_str = fecha.split('(')[1].split(')')[0].split('-')
    timestamp = int(timestamp_str)
    offset = int(offset_str) // 100 * 3600  # Convertir el desplazamiento a segundos

    # Convertir el timestamp a un objeto datetime y ajustar por el desplazamiento de zona horaria
    dt_object = datetime.utcfromtimestamp(timestamp / 1000) - timedelta(seconds=offset)
    return dt_object.strftime('%Y-%m-%d')
