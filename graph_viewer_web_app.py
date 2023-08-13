"""
This is Project IGI Graph Viewer GUI which generate the 3D graph of the game using the graph data file.
This also has the option to export the graph data to JSON file.
This is wriiten in Streamlit framework which is used to create the web app.
date : 12/08/2023
author : HeavenHM
"""

import os
import streamlit as st
import plotly.graph_objects as go
import json
import logging
from libs.graph_data_parser import GraphData,select_file
from libs.graph_area_parser import GraphArea
from graph_const import material_colors, material_mapping
import tempfile
import pandas as pd

logging.basicConfig(filename='graph_gen_app.log', level=logging.DEBUG)

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

def prepare_node_colors_and_sizes(data, node_radius_size):
    colors = []
    sizes = []
    for item in data:
        material = item['material']
        color = material_colors.get(material_mapping.get(material, 'UNKNOWN'), 'purple')
        colors.append(color)
        sizes.append(item['radius'] * node_radius_size)
    return colors, sizes

def prepare_hover_text(data, show_links, show_material, show_gamma_radius, show_criteria, show_position):
    text_data = []
    for item in data:
        text = f"Node ID: {item['id']}"
        if show_links:
            text += f"<br>Links: {', '.join(map(str, item['edges']))}"
        if show_material:
            text += f"<br>Material: {item['material']}"
        if show_gamma_radius:
            text += f"<br>Gamma: {item['gamma']}<br>Radius: {item['radius']}"
        if show_criteria:
            text += f"<br>Criteria: {item['criteria']}"
        if show_position:
            text += f"<br>Position: ({item['x']}, {item['y']}, {item['z']})"
        text_data.append(text)
    return text_data

def plot_graph(data):
    if st.session_state.graph_type == "Scatter":
        plot_3d(data, plot_type='scatter', symbol=st.session_state.node_symbol, show_links=st.session_state.show_links, show_material=st.session_state.show_material, show_gamma_radius=st.session_state.show_gamma_radius, show_criteria=st.session_state.show_criteria, show_position=st.session_state.node_position, node_radius_size=st.session_state.node_radius_size, scene_aspectmode=st.session_state.scene_aspectmode)
    elif st.session_state.graph_type == "Surface":
        plot_3d(data, plot_type='surface', symbol=st.session_state.node_symbol, show_links=st.session_state.show_links, show_material=st.session_state.show_material, show_gamma_radius=st.session_state.show_gamma_radius, show_criteria=st.session_state.show_criteria, show_position=st.session_state.node_position, node_radius_size=st.session_state.node_radius_size, scene_aspectmode=st.session_state.scene_aspectmode)
    elif st.session_state.graph_type == "Line":
        plot_3d(data, plot_type='line', symbol=st.session_state.node_symbol, show_links=st.session_state.show_links, show_material=st.session_state.show_material, show_gamma_radius=st.session_state.show_gamma_radius, show_criteria=st.session_state.show_criteria, show_position=st.session_state.node_position, node_radius_size=st.session_state.node_radius_size, scene_aspectmode=st.session_state.scene_aspectmode)
    elif st.session_state.graph_type == "Mesh":
        plot_3d(data, plot_type='mesh', symbol=st.session_state.node_symbol, show_links=st.session_state.show_links, show_material=st.session_state.show_material, show_gamma_radius=st.session_state.show_gamma_radius, show_criteria=st.session_state.show_criteria, show_position=st.session_state.node_position, node_radius_size=st.session_state.node_radius_size, scene_aspectmode=st.session_state.scene_aspectmode)

def plot_3d(data, plot_type='scatter', symbol=None, show_links=False, show_material=False, show_gamma_radius=False, show_criteria=False,show_position=False, node_radius_size=50,scene_aspectmode='cube'):
    logging.info(f"Generating 3D {plot_type} plot")
    x_data = [item['x'] for item in data]
    y_data = [item['y'] for item in data]
    z_data = [item['z'] for item in data]
    
    # Get edges only if show_links is True
    edge_x, edge_y, edge_z = get_edges(data) if show_links else ([], [], [])
    
    hover_texts = prepare_hover_text(data, show_links, show_material, show_gamma_radius, show_criteria,show_position)
    colors, sizes = prepare_node_colors_and_sizes(data, node_radius_size)
    
    fig = go.Figure()
    fig.update_layout(scene=dict(xaxis=dict(title=dict(text='X')), yaxis=dict(title=dict(text='Y')), zaxis=dict(title=dict(text='Z'))))
    fig.layout.scene.aspectmode = scene_aspectmode
    fig.layout.width = 800
    fig.layout.height = 600
    
    if plot_type == 'scatter':
        fig.add_trace(go.Scatter3d(x=x_data, y=y_data, z=z_data, mode='markers', marker=dict(color=colors, size=sizes, symbol=symbol, sizemode='diameter'), text=hover_texts, hoverinfo='text'))
    elif plot_type == 'surface':
        fig.add_trace(go.Scatter3d(x=x_data, y=y_data, z=z_data, mode='markers', marker=dict(color=colors, size=sizes, sizemode='diameter'), text=hover_texts, hoverinfo='text'))
    elif plot_type == 'line':
        fig.add_trace(go.Scatter3d(x=x_data, y=y_data, z=z_data, mode='lines+markers', marker=dict(color=colors, size=sizes, sizemode='diameter'), line=dict(color='red'), text=hover_texts, hoverinfo='text'))
    elif plot_type == 'mesh':
        intensity = list(range(len(colors)))
        fig.add_trace(go.Mesh3d(x=x_data, y=y_data, z=z_data, opacity=0.5, hoverinfo='text', hovertext=hover_texts, intensity=intensity, colorscale='Viridis', cmin=0, cmax=len(colors)-1))
        fig.add_trace(go.Scatter3d(x=x_data, y=y_data, z=z_data, mode='markers', marker=dict(color=colors, size=sizes, sizemode='diameter'), text=hover_texts, hoverinfo='text'))
    else:
        logging.error(f"Invalid plot type: {plot_type}")
        return

    # Add edges only if show_links is True
    if show_links:
        fig.add_trace(go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode='lines', line=dict(color='red')))
    
    # Embed the Plotly graph in the Streamlit app
    st.plotly_chart(fig)

    logging.info(f"3D {plot_type} plot generated successfully")



def adjust_node_height_data(data, node_height):
    if not node_height:
        for item in data:
            item["z"] = 0  # Set Z position to 0 or any other default value
    return data

def main():
    #st.title('Project IGI Graph Viewer')

    # Initialize session state variables if they don't exist
    if 'show_links' not in st.session_state:
        st.session_state.show_links = False
    if 'show_material' not in st.session_state:
        st.session_state.show_material = False
    if 'show_gamma_radius' not in st.session_state:
        st.session_state.show_gamma_radius = False
    if 'show_criteria' not in st.session_state:
        st.session_state.show_criteria = False
    if 'show_table_data' not in st.session_state:
        st.session_state.show_table_data = False
    if 'node_height' not in st.session_state:
        st.session_state.node_height = False
    if 'node_radius_size' not in st.session_state:
        st.session_state.node_radius_size = 30
    if 'graph_type' not in st.session_state:
        st.session_state.graph_type = 'Scatter'
    if 'node_symbol' not in st.session_state:
        st.session_state.node_symbol = 'square'
    if 'node_position' not in st.session_state:
        st.session_state.node_position = False
    if 'scene_aspectmode' not in st.session_state:
        st.session_state.scene_aspectmode = 'cube'
    if 'game_level' not in st.session_state:
        st.session_state.game_level = 1
    if 'show_area_data' not in st.session_state:
        st.session_state.show_area_data = False
    if 'single_space' not in st.session_state:
        st.session_state.single_space = False

    # Sidebar header
    st.sidebar.header('Project IGI Graph Viewer')
    st.sidebar.markdown('This is Project IGI Graph Viever which can view the 3D graph of the game using the graph data file.')

    # Sidebar settings
    with st.sidebar.expander('Legend Settings',expanded=False):
        st.session_state.show_material = st.checkbox('Node Material', st.session_state.show_material)
        st.session_state.show_gamma_radius = st.checkbox('Node Gamma/Radius', st.session_state.show_gamma_radius)
        st.session_state.show_criteria = st.checkbox('Node Criteria', st.session_state.show_criteria)
        st.session_state.node_position = st.checkbox('Node Position', st.session_state.node_position)
        
    with st.sidebar.expander('View Settings',expanded=False):
        st.session_state.show_table_data = st.checkbox('Node Table', st.session_state.show_table_data)
        st.session_state.show_area_data = st.checkbox('Area Table', st.session_state.show_area_data)
        st.session_state.show_links = st.checkbox('Node Links', st.session_state.show_links)
        st.session_state.single_space = st.checkbox('Single Space', False)
        st.session_state.scene_aspectmode = st.selectbox('Aspect Mode', ['auto', 'cube', 'data', 'manual'], index=['auto', 'cube', 'data', 'manual'].index(st.session_state.scene_aspectmode))
    
    with st.sidebar.expander('Graph & Node Settings',expanded=False):
        st.session_state.node_height = st.checkbox('Node Height', st.session_state.node_height)
        st.session_state.node_radius_size = st.slider("Node Radius Size:", 10, 100, st.session_state.node_radius_size)
        st.session_state.graph_type = st.selectbox('Graph Type', ['Scatter', 'Surface', 'Line', 'Mesh'], index=['Scatter', 'Surface', 'Line', 'Mesh'].index(st.session_state.graph_type))
        st.session_state.node_symbol = st.selectbox('Node Symbol', ['circle', 'circle-open', 'cross', 'diamond', 'diamond-open', 'square', 'square-open', 'x'], index=['circle', 'circle-open', 'cross', 'diamond', 'diamond-open', 'square', 'square-open', 'x'].index(st.session_state.node_symbol))

    with st.sidebar.expander('Game Settings', expanded=False):
        st.session_state.game_level = st.selectbox('Game Level', list(range(1, 15)), index=st.session_state.game_level - 1)
        
    # File uploader
    uploaded_files = st.file_uploader('Upload Graph Files', type=['dat'], accept_multiple_files=True)

    # Display the area data in a table if the checkbox is checked
    if st.session_state.show_area_data:
        area_json_data = GraphArea.get_json_data(st.session_state.game_level)
        data = json.loads(area_json_data)
        df = pd.DataFrame(data)
        st.subheader(f"Level {st.session_state.game_level} Area Data")
        st.dataframe(df)
    
    all_data = []

    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            uploaded_path = temp_file.name

        try:
            json_data = select_file(uploaded_path)
            if not json_data:
                st.error(f"Failed to parse the uploaded file: {uploaded_file.name}")
            else:
                data = json.loads(json_data)
                data = adjust_node_height_data(data, st.session_state.node_height)
                all_data.append(data)
            
             # Display the data in a table if the checkbox is checked
                if st.session_state.show_table_data:
                    df = pd.DataFrame(data)
                    st.subheader(f"Graph # {uploaded_file.name.split('graph')[1].split('.')[0]} Data")
                    st.dataframe(df)
                    
            # Set the title of Plot and the page
            graph_id = int(uploaded_file.name.split('graph')[1].split('.')[0])
            graph_name = GraphArea.get_area_by_graph_id(st.session_state.game_level, graph_id) if GraphArea.get_area_by_graph_id(st.session_state.game_level, graph_id) else 'Unknown Area'
            plot_name = 'Graph #' + str(graph_id) + '\t' + graph_name
            # set this name to the title of plotting graph
            st.title(plot_name)
            # set title font size
            st.markdown('<style>h1{font-size: 20px;}</style>', unsafe_allow_html=True)
            
        finally:
            os.remove(uploaded_path)

    if st.session_state.single_space:
        combined_data = [item for sublist in all_data for item in sublist]
        plot_graph(combined_data)
    else:
        for data in all_data:
            plot_graph(data)

if __name__ == "__main__":
    main()
