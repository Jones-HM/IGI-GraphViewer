import logging
import struct
import json
from graph_const import material_mapping

class GraphData:
    def __init__(self, name, hex_bytes, data_type, size):
        self.name = name
        self.hex_bytes = hex_bytes.replace(" ", "").lower()
        self.data_type = data_type
        self.size = size
        self.data = []
        
    def clear_data(self):
        self.data = []

    def extract_data(self, binary_data, start_index):
        index = binary_data.find(bytes.fromhex(self.hex_bytes), start_index)  # Search for the full 4-byte hex signature
        if index == -1:
            #logging.info(f"Hex signature {self.hex_bytes} not found after index {start_index}.")
            return start_index  # If not found, return the same index
        data_start_index = index + 8  # Adjusting for the 4 bytes offset
        end_index = data_start_index + self.size

        raw_data = binary_data[data_start_index:end_index]
        if self.data_type == "Stringx18":
            cleaned_data = ''.join([char if 32 <= ord(char) < 127 else '' for char in raw_data.decode(errors='ignore')]).strip()
            self.data.append(cleaned_data)
        elif self.data_type == "Real64x3":
            x, y, z = struct.unpack('ddd', raw_data)
            self.data.append((round(x, 2), round(y, 2), round(z,2)))
        else:
            self.data.append(raw_data)
        
        logging.info(f"Extracted data for {self.name} at index {index}. Data: {self.data[-1]}")
        return end_index

# graph file structure
graphDatList = [
    GraphData("Max Nodes", "04 E6 3A 0D", "Integer", 4),
    GraphData("Node Id", "04 CE 35 07", "Integer", 4),
    GraphData("Node Position", "04 95 42 1D", "Real64x3", 24),
    GraphData("Node Gamma", "04 9C 7E 0F", "Single", 4),
    GraphData("Node Radius", "04 23 30 14", "Single", 4),
    GraphData("Node Material", "04 29 B6 1B", "Integer", 1),
    GraphData("Node Criteria", "04 E5 D3 1B", "Stringx18", 20),
    GraphData("Graph Edge1", "04 4A 10 09", "Integer", 2),
    GraphData("Graph Edge2", "04 F6 18 09", "Integer", 2),
    GraphData("Graph EdgeType", "04 23 A9 0D", "Integer", 1)
]

def convert_to_json(graphDataList):
    nodes = []
    edges = list(zip(graphDataList[7].data, graphDataList[8].data, graphDataList[9].data))  # Combine edge1, edge2, and type

    node_counter = 1  # Counter for node IDs

    for i in range(len(graphDataList[1].data)):
        # Use the node_counter for the node ID
        node_id = node_counter
        node_counter += 1
        
        # Filter edges that are directly connected to the current node
        connected_edges = []
        for edge in edges:
            edge_id_1 = int.from_bytes(edge[0], "little", signed=False)
            edge_id_2 = int.from_bytes(edge[1], "little", signed=False)
            if node_id == edge_id_1:
                connected_edges.append(edge_id_2)
            elif node_id == edge_id_2:
                connected_edges.append(edge_id_1)
        
        material_id = int(graphDataList[5].data[i].hex(), 16)
        material_name = material_mapping.get(material_id, "UNKNOWN")
        
        node_criteria_prefix = "NODECRITERIA_"
        node_criteria_index = graphDataList[6].data[i].lower().find(node_criteria_prefix.lower())
        if node_criteria_index != -1:
            node_criteria = graphDataList[6].data[i][node_criteria_index + len(node_criteria_prefix):]
        else:
            node_criteria = ""
        node = {
            "id": node_id,
            "x": graphDataList[2].data[i][0],
            "y": graphDataList[2].data[i][1],
            "z": graphDataList[2].data[i][2],
            "gamma": struct.unpack('f', graphDataList[3].data[i])[0],
            "radius": struct.unpack('f', graphDataList[4].data[i])[0],
            "material": material_name,
            "criteria": node_criteria,
            "edges": connected_edges
        }
        nodes.append(node)
    return json.dumps(nodes, indent=4)

def select_file(filename):
    binary_data = read_binary_file(filename)
    
    # Clear existing data
    for graphDat in graphDatList:
        graphDat.clear_data()
        
    if binary_data:
        extract_node_data(binary_data, graphDatList)
        extract_edge_data(binary_data, graphDatList)
        json_data = convert_to_json(graphDatList)
        
    return json_data

def read_binary_file(filename):
    try:
        with open(filename, "rb") as file:
            return file.read()
    except Exception as e:
        logging.error(f"Error reading file {filename}: {e}")
        return None

def extract_node_data(binary_data, graphDatList):
    logging.info("Extracting node data...")
    start_index = 0
    while start_index < len(binary_data):
        logging.info(f"Searching for node data at index {start_index}...")
        node_id_index = binary_data.find(bytes.fromhex("04 CE 35 07"), start_index)
        
        if node_id_index == -1:
            logging.info("No more node data found.")
            break
        
        next_node_id_index = binary_data.find(bytes.fromhex("04 CE 35 07"), node_id_index + 4)
        if next_node_id_index == -1:
            next_node_id_index = len(binary_data)
        
        for graphDat in graphDatList:
            if "Edge" not in graphDat.name:  # Skip edge properties for node extraction
                prop_index = graphDat.extract_data(binary_data, node_id_index)
                if prop_index >= next_node_id_index:
                    break
        
        start_index = next_node_id_index



def extract_edge_data(binary_data, graphDatList):
    logging.info("Extracting edge data...")
    start_index = 0
    while start_index < len(binary_data):
        logging.info(f"Searching for edge data at index {start_index}...")
        edge_id_index = binary_data.find(bytes.fromhex("04 4A 10 09"), start_index)
        
        if edge_id_index == -1:
            logging.info("No more edge data found.")
            break
        
        for graphDat in graphDatList:
            if "Edge" in graphDat.name:  # Only process edge properties for edge extraction
                start_index = graphDat.extract_data(binary_data, edge_id_index)
        
def print_results(graphDatList):
    for graphDat in graphDatList:
        if graphDat.data_type == "Stringx18":
            logging.info(f"{graphDat.name}: {graphDat.data}")
        elif graphDat.data_type == "Real64x3":
            logging.info(f"{graphDat.name}: [{' '.join(map(str, pos))}]" for pos in graphDat.data)
        else:
            logging.info(f"{graphDat.name}: [{' '.join(map(lambda x: x.hex().upper(), graphDat.data))}]")
