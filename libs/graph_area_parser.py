import json
import requests

class GraphArea:
    BASE_URL = "https://raw.githubusercontent.com/Jones-HM/IGI-Research-Data/main/Data/Graphs/Areas-JSON/graph_area_level{}.json"

    @staticmethod
    def _fetch_data(level):
        response = requests.get(GraphArea.BASE_URL.format(level))
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(f"Failed to fetch data for level {level}")

    @staticmethod
    def get_json_data(level):
        data = GraphArea._fetch_data(level)
        return json.dumps(data, indent=4)

    @staticmethod
    def get_csv_data(level):
        data = GraphArea._fetch_data(level)
        csv_data = []
        for entry in data:
            csv_data.append([entry["Area"], entry["Graph"]])
        return csv_data

    @staticmethod
    def get_area_by_graph(level, graph_name):
        data = GraphArea._fetch_data(level)
        for entry in data:
            if entry["Area"] == graph_name:
                return entry["Graph"]
        return None

    @staticmethod
    def get_all_areas(level):
        data = GraphArea._fetch_data(level)
        return [entry["Area"] for entry in data]

    @staticmethod
    def get_all_graphs(level):
        data = GraphArea._fetch_data(level)
        return [entry["Graph"] for entry in data]

    @staticmethod
    def get_area_count(level):
        data = GraphArea._fetch_data(level)
        return len(data)

    @staticmethod
    def get_all_areas_except_cutscene(level):
        data = GraphArea._fetch_data(level)
        return [entry["Area"] for entry in data if entry["Area"] != "Cutscene Area"]

    @staticmethod
    def get_area_by_graph_id(level, graph_id):
        data = GraphArea._fetch_data(level)
        try:
            graph_name = f"Graph #{graph_id}"
            for entry in data:
                if entry["Graph"] == graph_name:
                    return entry["Area"]
            return None
        except:
            return None
