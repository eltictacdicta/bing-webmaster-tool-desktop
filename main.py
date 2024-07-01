import requests
from dotenv import load_dotenv
import os
import tkinter as tk
from tkinter import ttk, messagebox

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

def get_page_stats(site_url):
    headers = {
        'User-Agent': 'curl/7.12.1',
        'Content-Type': 'application/json'
    }
    try:
        url = f'https://ssl.bing.com/webmaster/api.svc/json/GetPageStats?apikey={API_KEY}&siteUrl={site_url}'
        r = requests.get(url=url, headers=headers)
        if r.status_code == 200:
            global data_cache
            data_cache = r.json()['d']
            # Limpiar la tabla antes de insertar nuevos datos
            for row in tree.get_children():
                tree.delete(row)
            
            # Insertar los datos en la tabla
            for item in data_cache:
                tree.insert("", "end", values=(
                    item['Query'], 
                    item['Date'], 
                    item['Impressions'], 
                    item['AvgImpressionPosition'], 
                    item['Clicks'], 
                    item['AvgClickPosition']
                ))
            return "Datos obtenidos correctamente"
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
            # Limpiar la tabla antes de insertar nuevos datos
            for row in tree.get_children():
                tree.delete(row)
            
            # Insertar los datos en la tabla
            for item in data['d']:
                tree.insert("", "end", values=(
                    item['Query'], 
                    item['Date'], 
                    item['Impressions'], 
                    item['AvgImpressionPosition'], 
                    item['Clicks'], 
                    item['AvgClickPosition']
                ))
            return "Datos obtenidos correctamente"
        else:
            return f"Error: {r.status_code}\n{r.content}"
    except Exception as e:
        return str(e)

def on_submit():
    site_url = site_combobox.get()
    if site_url:
        result = get_page_stats(site_url)
        text_result.delete(1.0, tk.END)
        text_result.insert(tk.END, result)
    else:
        messagebox.showwarning("Advertencia", "Por favor, seleccione una URL del sitio.")

def on_page_query_stats():
    site_url = site_combobox.get()
    page_url = entry_page.get()
    if site_url and page_url:
        result = get_page_query_stats(site_url, page_url)
        text_result.delete(1.0, tk.END)
        text_result.insert(tk.END, result)
    else:
        messagebox.showwarning("Advertencia", "Por favor, seleccione la URL del sitio y la URL de la página.")

def on_treeview_double_click(event):
    item = tree.selection()[0]
    page_url = tree.item(item, "values")[0]
    site_url = site_combobox.get()
    if site_url and page_url:
        entry_page.delete(0, tk.END)  # Limpiar el campo de entrada
        entry_page.insert(0, page_url)  # Autocompletar con la URL seleccionada
        result = get_page_query_stats(site_url, page_url)
        text_result.delete(1.0, tk.END)
        text_result.insert(tk.END, result)
    else:
        messagebox.showwarning("Advertencia", "Por favor, seleccione la URL del sitio y la URL de la página.")

def search_query():
    query = entry_search.get().lower()
    for row in tree.get_children():
        tree.delete(row)
    for item in data_cache:
        if query in item['Query'].lower():
            tree.insert("", "end", values=(
                item['Query'], 
                item['Date'], 
                item['Impressions'], 
                item['AvgImpressionPosition'], 
                item['Clicks'], 
                item['AvgClickPosition']
            ))

def sort_column(tree, col, reverse):
    l = [(tree.set(k, col), k) for k in tree.get_children('')]
    l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tree.move(k, '', index)

    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))

# Crear la ventana principal
root = tk.Tk()
root.title("Bing Webmaster Tools")

# Crear y colocar los widgets
label = ttk.Label(root, text="Seleccione la URL del sitio:")
label.pack(pady=5)

site_combobox = ttk.Combobox(root, width=50)
site_combobox.pack(pady=5)

button = ttk.Button(root, text="Obtener estadísticas", command=on_submit)
button.pack(pady=5)

label_page = ttk.Label(root, text="Ingrese la URL de la página:")
label_page.pack(pady=5)

entry_page = ttk.Entry(root, width=50)
entry_page.pack(pady=5)

button_page_query_stats = ttk.Button(root, text="Obtener estadísticas de la página", command=on_page_query_stats)
button_page_query_stats.pack(pady=5)

label_search = ttk.Label(root, text="Buscar en Query:")
label_search.pack(pady=5)

entry_search = ttk.Entry(root, width=50)
entry_search.pack(pady=5)

button_search = ttk.Button(root, text="Buscar", command=search_query)
button_search.pack(pady=5)

# Definir el widget tree
columns = ("Query", "Date", "Impressions", "AvgImpressionPosition", "Clicks", "AvgClickPosition")
tree = ttk.Treeview(root, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=col, command=lambda _col=col: sort_column(tree, _col, False))
tree.pack(pady=5)

# Vincular el evento de doble clic en el treeview
tree.bind("<Double-1>", on_treeview_double_click)

text_result = tk.Text(root, width=80, height=20)
text_result.pack(pady=5)

# Obtener y cargar las URLs de los sitios en el combobox
site_combobox['values'] = get_sites()

# Iniciar el bucle principal de la aplicación
root.mainloop()