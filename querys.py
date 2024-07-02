import requests
from dotenv import load_dotenv
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # Importar ttk
from datetime import datetime, timedelta  # Importar datetime y timedelta

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

def convertir_fecha(fecha):
    # Extraer la fecha en milisegundos y el desplazamiento de zona horaria
    timestamp_str, offset_str = fecha.split('(')[1].split(')')[0].split('-')
    timestamp = int(timestamp_str)
    offset = int(offset_str) // 100 * 3600  # Convertir el desplazamiento a segundos

    # Convertir el timestamp a un objeto datetime y ajustar por el desplazamiento de zona horaria
    dt_object = datetime.utcfromtimestamp(timestamp / 1000) - timedelta(seconds=offset)
    return dt_object.strftime('%Y-%m-%d')

class QueryPanel:
    def __init__(self, root, site_url, page_url):
        self.root = root
        self.site_url = site_url
        self.page_url = page_url
        self.window = tk.Toplevel(root)
        self.window.title("Resultados de la Consulta")

    def show(self):
        result = get_page_query_stats(self.site_url, self.page_url)
        if isinstance(result, str):
            messagebox.showerror("Error", result)
        else:
            # Mostrar la URL de la página en la parte superior del panel
            label_page_url = ttk.Label(self.window, text=f"URL de la página: {self.page_url}")
            label_page_url.pack(pady=5)

            # Botón para copiar la URL al portapapeles
            def copiar_url():
                self.window.clipboard_clear()
                self.window.clipboard_append(self.page_url)
                #messagebox.showinfo("Información", "URL copiada al portapapeles")

            button_copiar = ttk.Button(self.window, text="Copiar URL", command=copiar_url)
            button_copiar.pack(pady=5)
            # Crear el campo de búsqueda
            label_search = ttk.Label(self.window, text="Buscar en Query:")
            label_search.pack(pady=5)

            entry_search = ttk.Entry(self.window, width=50)
            entry_search.pack(pady=5)

            def search_query():
                query = entry_search.get().lower()
                for row in tree.get_children():
                    tree.delete(row)
                for item in result:
                    if query in item['Query'].lower():
                        tree.insert("", "end", values=(
                            item['Query'], 
                            convertir_fecha(item['Date']),  # Convertir la fecha
                            item['Impressions'], 
                            item['AvgImpressionPosition'], 
                            item['Clicks'], 
                            item['AvgClickPosition']
                        ))

            button_search = ttk.Button(self.window, text="Buscar", command=search_query)
            button_search.pack(pady=5)

            # Crear el treeview para mostrar los resultados
            columns = ("Query", "Date", "Impressions", "AvgImpressionPosition", "Clicks", "AvgClickPosition")
            tree = ttk.Treeview(self.window, columns=columns, show='headings')
            for col in columns:
                tree.heading(col, text=col)
            tree.pack(pady=5)

            for item in result:
                tree.insert("", "end", values=(
                    item['Query'], 
                    convertir_fecha(item['Date']),  # Convertir la fecha
                    item['Impressions'], 
                    item['AvgImpressionPosition'], 
                    item['Clicks'], 
                    item['AvgClickPosition']
                ))