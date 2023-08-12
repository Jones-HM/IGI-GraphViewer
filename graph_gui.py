"""
This is Project IGI Graph Generator GUI which generate the 3D graph of the game using the graph data file.
This also has the option to export the graph data to JSON file.
date : 12 - Aug - 2023
author : @heaven_hm
"""

import json
import logging
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import plotly.graph_objects as go
import tkinter as tk
from tkinter import ttk
from graph_data_parser import select_file,material_mapping
from graph_const import material_colors,material_mapping

# Constants
NODE_RADIUS_SIZE = 30
NODE_SYMBOL = 'square'

logging.basicConfig(filename='graph_generator.log', level=logging.DEBUG)

def load_json_data(data_str):
    try:
        return json.loads(data_str)
    except json.JSONDecodeError:
        logging.error("Invalid JSON data")
        messagebox.showerror("Error", "Invalid JSON data")
        return None

def get_edges(data):
    edge_x = []
    edge_y = []
    edge_z = []
    for item in data:
        if "edges" in item:
            for edge in item["edges"]:
                target_node = next((node for node in data if node["id"] == edge), None)
                if target_node:
                    edge_x.extend([item["x"], target_node["x"], None])
                    edge_y.extend([item["y"], target_node["y"], None])
                    edge_z.extend([item["z"], target_node["z"], None])
    return edge_x, edge_y, edge_z
 
def prepare_node_colors_and_sizes(data):
   
    logging.debug(f"material_colors list: {material_colors}")
    NODE_RADIUS_SIZE = int(node_radius_entry.get())
    
    colors = []
    sizes = []
    for item in data:
        material = item['material']
        color = material_colors.get(material_mapping.get(material, 'UNKNOWN'), 'purple')  # Default to 'gray' if material isn't found
        logging.debug(f"Material: {material}, Color: {color}")
        colors.append(color)
        sizes.append(item['radius'] * NODE_RADIUS_SIZE) 
        logging.debug(f"Radius: {item['radius']}")
    
    return colors, sizes


def prepare_hover_text(data):
    text_data = []
    for item in data:
        text = f"Node ID: {item['id']}"
        if show_links.get():
            text += f"<br>Links: {', '.join(map(str, item['edges']))}"
        if show_material.get():
            text += f"<br>Material: {item['material']}"
        if show_gamma_radius.get():
            text += f"<br>Gamma: {item['gamma']}<br>Radius: {item['radius']}"
        if show_criteria.get():
            text += f"<br>Criteria: {item['description']}"
        text_data.append(text)
    return text_data


def plot_3d(data, plot_type='scatter',symbol=None):
    logging.info(f"Generating 3D {plot_type} plot")
    x_data = [item['x'] for item in data]
    y_data = [item['y'] for item in data]
    z_data = [item['z'] for item in data]
    edge_x, edge_y, edge_z = get_edges(data)
    hover_texts = prepare_hover_text(data)
    colors, sizes = prepare_node_colors_and_sizes(data)
    
    fig = go.Figure()
    if plot_type == 'scatter':
        fig.add_trace(go.Scatter3d(x=x_data, y=y_data, z=z_data, mode='markers', marker=dict(color=colors, size=sizes, symbol=symbol, sizemode='diameter'), text=hover_texts, hoverinfo='text'))
    elif plot_type == 'surface':
        fig.add_trace(go.Scatter3d(x=x_data, y=y_data, z=z_data, mode='markers', marker=dict(color=colors, size=sizes, sizemode='diameter'), text=hover_texts, hoverinfo='text'))
    elif plot_type == 'line':
        fig.add_trace(go.Scatter3d(x=x_data, y=y_data, z=z_data, mode='lines+markers', marker=dict(color=colors, size=sizes, sizemode='diameter'), line=dict(color='red'), text=hover_texts, hoverinfo='text'))
    elif plot_type == 'mesh':
        # Use intensity to map colors to a colorscale
        intensity = list(range(len(colors)))
        fig.add_trace(go.Mesh3d(x=x_data, y=y_data, z=z_data, opacity=0.5, hoverinfo='text', hovertext=hover_texts, intensity=intensity, colorscale='Viridis', cmin=0, cmax=len(colors)-1))
        fig.add_trace(go.Scatter3d(x=x_data, y=y_data, z=z_data, mode='markers', marker=dict(color=colors, size=sizes, sizemode='diameter'), text=hover_texts, hoverinfo='text'))
    else:
        logging.error(f"Invalid plot type: {plot_type}")
        return

    fig.add_trace(go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode='lines', line=dict(color='red')))
    fig.show()
    logging.info(f"3D {plot_type} plot generated successfully")

def on_select_file():
    try:
        file_path = filedialog.askopenfilename(filetypes=[("Graph files", "*.dat"), ("All files", "*.*")])
        if file_path:
            json_data = select_file(file_path)
                    
            json_input.delete("1.0", tk.END)
            json_input.insert(tk.END, json_data)
            
            json_label['text'] = file_path.split('/')[-1]
    except Exception as e:
        logging.error(f"Error selecting file: {e}")
        messagebox.showerror("Error", "Error selecting file")

def on_export_to_json():
    data_str = json_input.get("1.0", tk.END)
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'w') as file:
            file.write(data_str)
        messagebox.showinfo("Success", "Graph exported to JSON successfully!")

def adjust_data_based_on_input(data):
    ignore_z = ignore_node_height.get()
    if ignore_z:
        for item in data:
            item["z"] = 0  # Set Z position to 0 or any other default value
    return data

def on_generate_graph():
    try:
        data_str = json_input.get("1.0", tk.END)
        data = json.loads(data_str)
        if not data:
            return

        # Adjust data based on user's input
        data = adjust_data_based_on_input(data)

        graph_type = graph_type_combobox.get()

        if graph_type == "3D Scatter":
            plot_3d(data, plot_type='scatter',symbol=node_symbol_combobox.get())
        elif graph_type == "3D Surface":
            plot_3d(data, plot_type='surface',symbol=node_symbol_combobox.get())
        elif graph_type == "3D Line":
            plot_3d(data, plot_type='line',symbol=node_symbol_combobox.get())
        elif graph_type == "3D Mesh":
            plot_3d(data, plot_type='mesh',symbol=node_symbol_combobox.get())
    except Exception as e:
        logging.error(f"Error generating graph: {e}")
        messagebox.showerror("Error", "Error generating graph")

# Functions
def on_quit():
    app.quit()

def on_help():
    help_message = "This is a GUI for Project IGI Graph Generator which generate the 3D graph of the game using the graph data file.\nSelect the graph file like graph4019.dat (Binary file) and click on Generate Graph button to generate the 3D graph.\nThis also has the option to export the graph data to JSON file.\n\nAuthor: @heaven_hm\nDate: 12 - Aug - 2023"
    messagebox.showinfo("Help", help_message)

# Main App
app = tk.Tk()
app_name = "IGI 3D Graph Generator - HM"
app.title(app_name)
app.geometry("700x600")
app.resizable(True, True)

# Create a notebook (tabs)
notebook = ttk.Notebook(app)
notebook.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

# Create frames for the tabs
main_frame = ttk.Frame(notebook)
settings_frame = ttk.Frame(notebook)

notebook.add(main_frame, text="Main")
notebook.add(settings_frame, text="Settings")

json_label = ttk.Label(main_frame, text="Graph JSON :")
json_label.grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
json_label['text'] = "Graph JSON :"

json_input = tk.Text(main_frame, height=10, width=60, wrap=tk.WORD, font=("Courier New", 14))
json_input.grid(row=1, column=0, columnspan=4, pady=5, padx=5, sticky=tk.W+tk.E+tk.N+tk.S)
scroll_x = tk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=json_input.xview)
scroll_x.grid(row=2, column=0, columnspan=4, sticky=tk.W+tk.E)
scroll_y = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=json_input.yview)
scroll_y.grid(row=1, column=4, sticky=tk.N+tk.S)
json_input['xscrollcommand'] = scroll_x.set
json_input['yscrollcommand'] = scroll_y.set
json_input.tag_configure("json", background="yellow")

# Configure the rows and columns of the main frame to expand and fill the available space
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

# Configure the window to resize with the main frame
app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=1)

ttk.Label(main_frame, text="Graph Type:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
graph_type_combobox = ttk.Combobox(main_frame, values=["3D Scatter", "3D Surface", "3D Line", "3D Mesh"])
graph_type_combobox.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
graph_type_combobox.set("3D Scatter")

# Settings Tab
show_links = tk.BooleanVar()
show_material = tk.BooleanVar()
show_gamma_radius = tk.BooleanVar()
show_criteria = tk.BooleanVar()

ttk.Checkbutton(settings_frame, text="Node Links", variable=show_links).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
ttk.Checkbutton(settings_frame, text="Node Material", variable=show_material).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
ttk.Checkbutton(settings_frame, text="Node Gamma/Radius", variable=show_gamma_radius).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
ttk.Checkbutton(settings_frame, text="Node Criteria", variable=show_criteria).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

ignore_node_height = tk.BooleanVar()
ignore_height_checkbox = ttk.Checkbutton(settings_frame, text="Node Ignore Height", variable=ignore_node_height)
ignore_height_checkbox.grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)

ttk.Label(settings_frame, text="Node Radius Size:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
node_radius_entry = tk.Entry(settings_frame)
node_radius_entry.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
node_radius_entry.insert(0, "50")

ttk.Label(settings_frame, text="Node Symbol:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=5)
node_symbol_combobox = ttk.Combobox(settings_frame, values=['circle', 'circle-open', 'cross', 'diamond', 'diamond-open', 'square', 'square-open', 'x'])
node_symbol_combobox.grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
node_symbol_combobox.set("square")


# Buttons
button_frame = ttk.Frame(app)
button_frame.pack(pady=20)

ttk.Button(button_frame, text="Generate Graph", command=on_generate_graph).grid(row=0, column=0, padx=10)
ttk.Button(button_frame, text="Select Graph", command=on_select_file).grid(row=0, column=1, padx=10)
ttk.Button(button_frame, text="Export JSON", command=on_export_to_json).grid(row=0, column=2, padx=10)
ttk.Button(button_frame, text="Help", command=on_help).grid(row=0, column=3, padx=10)
ttk.Button(button_frame, text="Quit", command=on_quit).grid(row=0, column=4, padx=10)

# Status Bar
status_bar = ttk.Label(app, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(fill=tk.X)

Settings_data_frame = ttk.Frame(main_frame)
Settings_data_frame.grid(row=6, column=0, columnspan=4, sticky=tk.W, padx=5, pady=5)

app.mainloop()