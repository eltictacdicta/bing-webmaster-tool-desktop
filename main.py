import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from querys import QueryPanel
from urls import UrlPanel
from utils import get_date_limit, convertir_fecha_unix, get_sites, get_page_stats
from datetime import datetime
from collections import defaultdict

data_cache = []
showing_queries = False

def export_to_csv():
    if not data_cache:
        messagebox.showwarning("Advertencia", "No hay datos para exportar.")
        return
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title="Guardar archivo CSV"
    )
    if not file_path:
        return
    
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Query/URL", "Impressions", "AvgImpressionPosition", "Clicks"])

        for row in tree.get_children():
            values = tree.item(row, "values")
            writer.writerow(values)

    messagebox.showinfo("Éxito", f"Datos exportados a {file_path}.")

def convertir_fecha_unix(fecha_unix):
    timestamp = int(fecha_unix.split('(')[1].split('-')[0]) / 1000
    return datetime.fromtimestamp(timestamp)

def on_submit(by_query=False):
    global data_cache
    site_url = site_combobox.get()
    if site_url:
        result = get_page_stats(site_url, by_query)
        if isinstance(result, str):
            messagebox.showerror("Error", result)
        else:
            data_cache = result
            filter_data(by_query)
    else:
        messagebox.showwarning("Advertencia", "Por favor, seleccione una URL del sitio.")

def filter_data(by_query):
    date_limit = get_date_limit(date_range_combobox.get())
    query = entry_search.get().lower()

    for row in tree.get_children():
        tree.delete(row)

    grouped_data = defaultdict(lambda: {'Impressions': 0, 'AvgImpressionPosition': 0, 'Clicks': 0, 'Count': 0})
    
    for item in data_cache:
        item_date = convertir_fecha_unix(item['Date'])
        if item_date >= date_limit:
            key = item['Query'] if showing_queries else item.get('Page', item['Query'])
            if query in key.lower():
                grouped_data[key]['Impressions'] += item['Impressions']
                grouped_data[key]['AvgImpressionPosition'] += item['AvgImpressionPosition']
                grouped_data[key]['Clicks'] += item['Clicks']
                grouped_data[key]['Count'] += 1

    for key, data in grouped_data.items():
        avg_position = data['AvgImpressionPosition'] / data['Count'] if data['Count'] > 0 else 0
        avg_position = round(avg_position)
        tree.insert("", "end", values=(key, data['Impressions'], avg_position, data['Clicks']))

def search_query():
    filter_data(showing_queries)

def on_treeview_double_click(event):
    item = tree.selection()[0]
    selected_value = tree.item(item, "values")[0]
    site_url = site_combobox.get()
    range_option = date_range_combobox.get()
    if site_url and selected_value:
        if showing_queries:
            url_panel = UrlPanel(root, site_url, selected_value, range_option)
            url_panel.show()
        else:
            query_panel = QueryPanel(root, site_url, selected_value, range_option)
            query_panel.show()
    else:
        messagebox.showwarning("Advertencia", "Por favor, seleccione la URL del sitio y la URL de la página.")

def sort_column(tree, col, reverse):
    def convert(val):
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                return val

    l = [(convert(tree.set(k, col)), k) for k in tree.get_children('')]
    l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tree.move(k, '', index)

    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))

def toggle_view(by_query):
    global showing_queries
    showing_queries = by_query
    on_submit(by_query)

root = tk.Tk()
root.title("Bing Webmaster Tools")

label = ttk.Label(root, text="Seleccione la URL del sitio:")
label.pack(pady=5)

site_combobox = ttk.Combobox(root, width=50)
site_combobox.pack(pady=5)

label_date_range = ttk.Label(root, text="Seleccione el rango de fechas:")
label_date_range.pack(pady=5)

date_range_combobox = ttk.Combobox(root, values=["Última semana", "Últimos 30 días", "Últimos 3 meses", "Últimos 6 meses"], width=50)
date_range_combobox.set("Últimos 3 meses")
date_range_combobox.pack(pady=5)

button_toggle_query = ttk.Button(root, text="Mostrar estadísticas por queries", command=lambda: toggle_view(True))
button_toggle_query.pack(pady=5)

button_toggle_url = ttk.Button(root, text="Mostrar estadísticas por URLs", command=lambda: toggle_view(False))
button_toggle_url.pack(pady=5)

label_search = ttk.Label(root, text="Buscar en Query/URL:")
label_search.pack(pady=5)

entry_search = ttk.Entry(root, width=50)
entry_search.pack(pady=5)

button_search_query = ttk.Button(root, text="Buscar en Query/URL", command=search_query)
button_search_query.pack(pady=5)

button_export_csv = ttk.Button(root, text="Exportar a CSV", command=export_to_csv)
button_export_csv.pack(pady=5)

columns = ("Query/URL", "Impressions", "AvgImpressionPosition", "Clicks")
tree = ttk.Treeview(root, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=col, command=lambda _col=col: sort_column(tree, _col, False))
tree.pack(pady=5)

tree.bind("<Double-1>", on_treeview_double_click)

site_combobox['values'] = get_sites()

root.mainloop()