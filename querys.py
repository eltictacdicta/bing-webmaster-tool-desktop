
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # Importar ttk
from tkinter import filedialog
from collections import defaultdict
from utils import get_date_limit, convertir_fecha_unix, get_page_query_stats
import csv  # Importar el módulo CSV


class QueryPanel:
    def __init__(self, root, site_url, page_url, range_option):
        self.root = root
        self.site_url = site_url
        self.page_url = page_url
        self.range_option = range_option  # Guardar el rango de fechas
        self.window = tk.Toplevel(root)
        self.window.title("Resultados de la Consulta")

    def show(self):
        result = get_page_query_stats(self.site_url, self.page_url)
        if isinstance(result, str):
            messagebox.showerror("Error", result)
        else:
            # Obtener el límite de fecha del panel principal
            date_limit = get_date_limit(self.range_option)

            # Filtrar y agrupar los resultados por query
            grouped_data = defaultdict(lambda: {'Impressions': 0, 'AvgImpressionPosition': 0, 'Clicks': 0, 'Count': 0})
            for item in result:
                item_date = convertir_fecha_unix(item['Date'])
                if item_date >= date_limit:
                    key = item['Query'].lower()  # Agrupar por query
                    grouped_data[key]['Impressions'] += item['Impressions']
                    grouped_data[key]['AvgImpressionPosition'] += item['AvgImpressionPosition']
                    grouped_data[key]['Clicks'] += item['Clicks']
                    grouped_data[key]['Count'] += 1

            # Mostrar la URL de la página en la parte superior del panel
            label_page_url = ttk.Label(self.window, text=f"URL de la página: {self.page_url}")
            label_page_url.pack(pady=5)

            # Botón para copiar la URL al portapapeles
            def copiar_url():
                self.window.clipboard_clear()
                self.window.clipboard_append(self.page_url)

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
                for key, data in grouped_data.items():
                    if query in key:
                        avg_position = data['AvgImpressionPosition'] / data['Count'] if data['Count'] > 0 else 0
                        avg_position = round(avg_position)  # Redondear a entero
                        tree.insert("", "end", values=(
                            key, 
                            data['Impressions'], 
                            avg_position, 
                            data['Clicks']
                        ))

            button_search = ttk.Button(self.window, text="Buscar", command=search_query)
            button_search.pack(pady=5)

            def export_to_csv():
                # Abrir un cuadro de diálogo para seleccionar la ubicación y nombre del archivo
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                    title="Guardar como"
                )

                if file_path:  # Verificar que el usuario no canceló
                    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow(columns)  # Escribir encabezados

                        for key, data in grouped_data.items():
                            avg_position = data['AvgImpressionPosition'] / data['Count'] if data['Count'] > 0 else 0
                            avg_position = round(avg_position)  # Redondear a entero
                            writer.writerow([key, data['Impressions'], avg_position, data['Clicks']])

                    messagebox.showinfo("Exportar a CSV", f"Los resultados se han exportado correctamente a {file_path}.")

            button_export = ttk.Button(self.window, text="Exportar a CSV", command=export_to_csv)
            button_export.pack(pady=5)

            # Crear el treeview para mostrar los resultados
            columns = ("Query", "Impressions", "AvgImpressionPosition", "Clicks")  # Cambiar "Fecha" a "Query"
            tree = ttk.Treeview(self.window, columns=columns, show='headings')
            for col in columns:
                tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(tree, _col, False))  # Habilitar ordenación
            tree.pack(pady=5)

            for key, data in grouped_data.items():
                avg_position = data['AvgImpressionPosition'] / data['Count'] if data['Count'] > 0 else 0
                avg_position = round(avg_position)  # Redondear a entero
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
