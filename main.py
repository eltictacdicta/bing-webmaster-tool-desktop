import tkinter as tk
from tkinter import ttk, messagebox
from querys import QueryPanel, get_sites, get_page_stats, convertir_fecha

data_cache = []

# Función que se ejecuta al presionar el botón "Obtener estadísticas"
def on_submit():
    global data_cache  # Permite modificar la variable global data_cache
    site_url = site_combobox.get()  # Obtiene la URL del sitio seleccionada en el combobox
    if site_url:
        result = get_page_stats(site_url)  # Obtiene las estadísticas de la página
        if isinstance(result, str):
            messagebox.showerror("Error", result)  # Muestra un error si el resultado es un string (mensaje de error)
        else:
            data_cache = result  # Guarda los resultados en la caché
            # Limpiar la tabla antes de insertar nuevos datos
            for row in tree.get_children():
                tree.delete(row)
            
            # Insertar los datos en la tabla
            for item in result:
                tree.insert("", "end", values=(
                    item['Query'], 
                    convertir_fecha(item['Date']),  
                    item['Impressions'], 
                    item['AvgImpressionPosition'], 
                    item['Clicks']
                ))
    else:
        messagebox.showwarning("Advertencia", "Por favor, seleccione una URL del sitio.")  # Muestra una advertencia si no se selecciona una URL

# Función que se ejecuta al hacer doble clic en un elemento del treeview
def on_treeview_double_click(event):
    item = tree.selection()[0]  # Obtiene el elemento seleccionado
    page_url = tree.item(item, "values")[0]  # Obtiene la URL de la página del elemento seleccionado
    site_url = site_combobox.get()  # Obtiene la URL del sitio seleccionada en el combobox
    if site_url and page_url:
        query_panel = QueryPanel(root, site_url, page_url)  # Crea un panel de consulta con la URL del sitio y la URL de la página
        query_panel.show()  # Muestra el panel de consulta
    else:
        messagebox.showwarning("Advertencia", "Por favor, seleccione la URL del sitio y la URL de la página.")  # Muestra una advertencia si no se selecciona una URL del sitio o de la página

# Función que se ejecuta al presionar el botón "Buscar"
def search_query():
    query = entry_search.get().lower()  # Obtiene la consulta de búsqueda y la convierte a minúsculas
    for row in tree.get_children():
        tree.delete(row)  # Limpia la tabla
    for item in data_cache:
        if query in item['Query'].lower():  # Filtra los resultados que contienen la consulta de búsqueda
            tree.insert("", "end", values=(
                item['Query'], 
                convertir_fecha(item['Date']), 
                item['Impressions'], 
                item['AvgImpressionPosition'], 
                item['Clicks']
            ))

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
columns = ("Query", "Date", "Impressions", "AvgImpressionPosition", "Clicks")
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