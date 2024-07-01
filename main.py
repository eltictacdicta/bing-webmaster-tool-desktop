import tkinter as tk
from tkinter import ttk, messagebox
from querys import QueryPanel, get_sites, get_page_stats

data_cache = []


def on_submit():
    global data_cache  # Añadir esta línea
    site_url = site_combobox.get()
    if site_url:
        result = get_page_stats(site_url)
        if isinstance(result, str):
            messagebox.showerror("Error", result)
        else:
            data_cache = result  # Añadir esta línea
            # Limpiar la tabla antes de insertar nuevos datos
            for row in tree.get_children():
                tree.delete(row)
            
            # Insertar los datos en la tabla
            for item in result:
                tree.insert("", "end", values=(
                    item['Query'], 
                    item['Date'], 
                    item['Impressions'], 
                    item['AvgImpressionPosition'], 
                    item['Clicks'], 
                    item['AvgClickPosition']
                ))
    else:
        messagebox.showwarning("Advertencia", "Por favor, seleccione una URL del sitio.")
    


def on_treeview_double_click(event):
    item = tree.selection()[0]
    page_url = tree.item(item, "values")[0]
    site_url = site_combobox.get()
    if site_url and page_url:
        query_panel = QueryPanel(root, site_url, page_url)
        query_panel.show()
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

# Esta parte del código ha sido eliminada según las instrucciones.

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

# Obtener y cargar las URLs de los sitios en el combobox
site_combobox['values'] = get_sites()

# Iniciar el bucle principal de la aplicación
root.mainloop()