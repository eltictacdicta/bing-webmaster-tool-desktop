import tkinter as tk
from tkinter import ttk, messagebox
from querys import QueryPanel, get_sites, get_page_stats
from utils import get_date_limit, convertir_fecha_unix, convertir_fecha  # Importar get_date_limit desde utils.py
from datetime import datetime, timedelta
from collections import defaultdict

data_cache = []
showing_queries = False  # Variable para alternar entre mostrar URLs y queries

# Función que se ejecuta al presionar el botón "Obtener estadísticas"
def on_submit(by_query=False):
    global data_cache  # Permite modificar la variable global data_cache
    site_url = site_combobox.get()  # Obtiene la URL del sitio seleccionada en el combobox
    if site_url:
        result = get_page_stats(site_url, by_query)  # Obtiene las estadísticas de la página o query
        if isinstance(result, str):
            messagebox.showerror("Error", result)  # Muestra un error si el resultado es un string (mensaje de error)
        else:
            data_cache = result  # Guarda los resultados en la caché
            filter_data()  # Filtra los datos según el rango de fechas seleccionado
    else:
        messagebox.showwarning("Advertencia", "Por favor, seleccione una URL del sitio.")  # Muestra una advertencia si no se selecciona una URL

# Función para convertir la fecha del formato '/Date(1705651200000-0800)/' a un objeto datetime
def convertir_fecha_unix(fecha_unix):
    timestamp = int(fecha_unix.split('(')[1].split('-')[0]) / 1000
    return datetime.fromtimestamp(timestamp)

# Función para filtrar y agrupar los datos según el rango de fechas seleccionado
def filter_data():
    date_limit = get_date_limit(date_range_combobox.get())
    query = entry_search.get().lower()  # Obtiene la consulta de búsqueda y la convierte a minúsculas

    # Limpiar la tabla antes de insertar nuevos datos
    for row in tree.get_children():
        tree.delete(row)
    
    # Agrupar los datos por URL o por Query
    grouped_data = defaultdict(lambda: {'Impressions': 0, 'AvgImpressionPosition': 0, 'Clicks': 0, 'Count': 0})
    for item in data_cache:
        item_date = convertir_fecha_unix(item['Date'])
        if item_date >= date_limit and (query in item['Query'].lower() or not query):
            key = item['Query'] if showing_queries else item.get('Page', item['Query'])
            grouped_data[key]['Impressions'] += item['Impressions']
            grouped_data[key]['AvgImpressionPosition'] += item['AvgImpressionPosition']
            grouped_data[key]['Clicks'] += item['Clicks']
            grouped_data[key]['Count'] += 1

    # Insertar los datos agrupados en la tabla
    for key, data in grouped_data.items():
        avg_position = data['AvgImpressionPosition'] / data['Count'] if data['Count'] > 0 else 0
        avg_position = round(avg_position)  # Redondear a entero
        tree.insert("", "end", values=(
            key, 
            data['Impressions'], 
            avg_position, 
            data['Clicks']
        ))

def on_treeview_double_click(event):
    item = tree.selection()[0]  # Obtiene el elemento seleccionado
    page_url = tree.item(item, "values")[0]  # Obtiene la URL de la página del elemento seleccionado
    site_url = site_combobox.get()  # Obtiene la URL del sitio seleccionada en el combobox
    range_option = date_range_combobox.get()  # Obtiene el rango de fechas seleccionado
    if site_url and page_url:
        query_panel = QueryPanel(root, site_url, page_url, range_option)  # Pasa el rango de fechas al QueryPanel
        query_panel.show()  # Muestra el panel de consulta
    else:
        messagebox.showwarning("Advertencia", "Por favor, seleccione la URL del sitio y la URL de la página.")  # Muestra una advertencia si no se selecciona una URL del sitio o de la página
# Función para ordenar las columnas del treeview
def sort_column(tree, col, reverse):
    # Función para convertir los valores a un tipo adecuado para la comparación
    def convert(val):
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                return val

    l = [(convert(tree.set(k, col)), k) for k in tree.get_children('')]  # Convierte los valores antes de ordenar
    l.sort(reverse=reverse)  # Ordena los valores

    for index, (val, k) in enumerate(l):
        tree.move(k, '', index)  # Reordena los elementos en el treeview

    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))  # Cambia la dirección de ordenación al hacer clic en el encabezado de la columna

# Función para alternar entre mostrar estadísticas por URLs y por queries
def toggle_view(by_query):
    global showing_queries
    showing_queries = by_query
    on_submit(by_query)

# Crear la ventana principal
root = tk.Tk()
root.title("Bing Webmaster Tools")

# Crear y colocar los widgets
label = ttk.Label(root, text="Seleccione la URL del sitio:")
label.pack(pady=5)

site_combobox = ttk.Combobox(root, width=50)
site_combobox.pack(pady=5)

label_date_range = ttk.Label(root, text="Seleccione el rango de fechas:")
label_date_range.pack(pady=5)

date_range_combobox = ttk.Combobox(root, values=["Última semana", "Últimos 30 días", "Últimos 3 meses", "Últimos 6 meses"], width=50)
date_range_combobox.set("Últimos 3 meses")  # Valor por defecto
date_range_combobox.pack(pady=5)
date_range_combobox._name = "date_range_combobox"  # Asignar nombre explícito

label_search = ttk.Label(root, text="Buscar en Query:")
label_search.pack(pady=5)

entry_search = ttk.Entry(root, width=50)
entry_search.pack(pady=5)

button_toggle_query = ttk.Button(root, text="Mostrar estadísticas por queries", command=lambda: toggle_view(True))
button_toggle_query.pack(pady=5)

button_toggle_url = ttk.Button(root, text="Mostrar estadísticas por URLs", command=lambda: toggle_view(False))
button_toggle_url.pack(pady=5)

# Definir el widget tree
columns = ("Query/URL", "Impressions", "AvgImpressionPosition", "Clicks")
tree = ttk.Treeview(root, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=col, command=lambda _col=col: sort_column(tree, _col, False))
tree.pack(pady=5)

# Vincular el evento de doble clic en el treeview
tree.bind("<Double-1>", on_treeview_double_click)

# Obtener y cargar las URLs de los sitios en el combobox
site_combobox['values'] = get_sites()

# Iniciar el bucle principal de la aplicación
root.mainloop()