import requests
from dotenv import load_dotenv
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from collections import defaultdict
from utils import get_date_limit, convertir_fecha_unix

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la API key desde las variables de entorno
API_KEY = os.getenv('BING_API_KEY')

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

class UrlPanel:
    def __init__(self, root, site_url, query, range_option):
        self.root = root
        self.site_url = site_url
        self.query = query
        self.range_option = range_option
        self.window = tk.Toplevel(root)
        self.window.title("Resultados de URLs por Query")

    def show(self):
        result = get_query_urls(self.site_url, self.query)
        if isinstance(result, str):
            messagebox.showerror("Error", result)
        else:
            date_limit = get_date_limit(self.range_option)

            grouped_data = defaultdict(lambda: {'Impressions': 0, 'AvgImpressionPosition': 0, 'Clicks': 0, 'Count': 0})
            for item in result:
                item_date = convertir_fecha_unix(item['Date'])
                if item_date >= date_limit:
                    key = item['Query'].lower()  # Cambiar 'Url' a 'Query'
                    grouped_data[key]['Impressions'] += item['Impressions']
                    grouped_data[key]['AvgImpressionPosition'] += item['AvgImpressionPosition']
                    grouped_data[key]['Clicks'] += item['Clicks']
                    grouped_data[key]['Count'] += 1

            label_query = ttk.Label(self.window, text=f"Query: {self.query}")
            label_query.pack(pady=5)

            columns = ("Query", "Impressions", "AvgImpressionPosition", "Clicks")
            tree = ttk.Treeview(self.window, columns=columns, show='headings')
            for col in columns:
                tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(tree, _col, False))
            tree.pack(pady=5)

            for key, data in grouped_data.items():
                avg_position = data['AvgImpressionPosition'] / data['Count'] if data['Count'] > 0 else 0
                avg_position = round(avg_position)
                tree.insert("", "end", values=(
                    key, 
                    data['Impressions'], 
                    avg_position, 
                    data['Clicks']
                ))

    def sort_treeview(self, tree, col, reverse):
        l = [(tree.set(k, col), k) for k in tree.get_children('')]
        l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            tree.move(k, '', index)

        tree.heading(col, command=lambda: self.sort_treeview(tree, col, not reverse))