import json
import requests

class GraphArea:
    BASE_URL = "https://raw.githubusercontent.com/Jones-HM/IGI-Research-Data/main/Data/Graphs/Areas-JSON/graph_area_level{}.json"

    def __init__(self, level):
        self.level = level
        self.data = self._fetch_data()

    def _fetch_data(self):
        response = requests.get(self.BASE_URL.format(self.level))
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(f"Failed to fetch data for level {self.level}")
    
    def get_json_data(self):
        # return the json with indentation of 4 spaces
        return json.dumps(self.data, indent=4)

    def get_csv_data(self):
        csv_data = []
        for entry in self.data:
            csv_data.append([entry["Area"], entry["Graph"]])
        return csv_data
    
    def get_area_by_graph(self, graph_name):
        for entry in self.data:
            if entry["Area"] == graph_name:
                return entry["Graph"]
        return None

    def get_all_areas(self):
        return [entry["Area"] for entry in self.data]

    def get_all_graphs(self):
        return [entry["Graph"] for entry in self.data]

    def get_area_count(self):
        return len(self.data)

    def get_all_areas_except_cutscene(self):
        return [entry["Area"] for entry in self.data if entry["Area"] != "Cutscene Area"]
    
    def get_area_by_graph_id(self, graph_id):
        try:
            graph_name = f"Graph #{graph_id}"
            for entry in self.data:
                if entry["Graph"] == graph_name:
                    return entry["Area"]
            return None
        except:
            return None