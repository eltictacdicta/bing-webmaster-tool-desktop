
import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
from tkinter import messagebox

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

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la API key desde las variables de entorno
API_KEY = os.getenv('BING_API_KEY')

def get_sites():
    headers = {
        'User-Agent': 'curl/7.12.1',
        'Content-Type': 'application/json'
    }
    try:
        url = f'https://ssl.bing.com/webmaster/api.svc/json/GetUserSites?apikey={API_KEY}'
        r = requests.get(url=url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            return [site['Url'] for site in data['d']]
        else:
            messagebox.showerror("Error", f"Error: {r.status_code}\n{r.content}")
            return []
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return []

def get_page_stats(site_url, by_query=False):
    headers = {
        'User-Agent': 'curl/7.12.1',
        'Content-Type': 'application/json'
    }
    try:
        if by_query:
            url = f'https://ssl.bing.com/webmaster/api.svc/json/GetQueryStats?apikey={API_KEY}&siteUrl={site_url}'
        else:
            url = f'https://ssl.bing.com/webmaster/api.svc/json/GetPageStats?apikey={API_KEY}&siteUrl={site_url}'
        
        r = requests.get(url=url, headers=headers)
        if r.status_code == 200:
            global data_cache
            data_cache = r.json()['d']
            return data_cache
        else:
            return f"Error: {r.status_code}\n{r.content}"
    except Exception as e:
        return str(e)

def get_page_query_stats(site_url, page_url):
    headers = {
        'User-Agent': 'curl/7.12.1',
        'Content-Type': 'application/json'
    }
    try:
        url = f'https://ssl.bing.com/webmaster/api.svc/json/GetPageQueryStats?apikey={API_KEY}&siteUrl={site_url}&page={page_url}'
        r = requests.get(url=url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            return data['d']
        else:
            return f"Error: {r.status_code}\n{r.content}"
    except Exception as e:
        return str(e)

def get_query_urls(site_url, query):
    headers = {
        'User-Agent': 'curl/7.12.1',
        'Content-Type': 'application/json'
    }
    try:
        url = f'https://ssl.bing.com/webmaster/api.svc/json/GetQueryPageStats?siteUrl={site_url}&query="{query}"&apikey={API_KEY}'
        print(f"Generated URL: {url}")  # Agregar mensaje de depuración
        r = requests.get(url=url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            return data['d']
        else:
            return f"Error: {r.status_code}\n{r.content}"
    except Exception as e:
        return str(e)
