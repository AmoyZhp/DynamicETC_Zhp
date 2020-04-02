from env.dynamic_etc import DynamicETC
from agent.default_agent import DefaultAgent 
from env.graph import Graph
import yaml
import json
import random

GRAPH_CONFIG_PATH = "/Users/zhanghaopeng/CodeHub/2020Spring/DyETC/env/config/"
class Runner():
    def __init__(self):
        super().__init__()
    
    def process_state_to_obs(self, state, i):
        return []

    def run(self,filename):
        graph = self.init_graph(filename)
        dyenv = DynamicETC(graph)
        action_space = dyenv.action_space
        agents = {}
        # each road has an agent to adjust toll
        for i in range(action_space[2]) :
            agents[i] = DefaultAgent()
        cnt = 0
        state = dyenv.reset()
        while True:
            actions = {}
            # get union action
            for key, agent in agents.items():
                obs = self.process_state_to_obs(state, i)
                act = agent.act(obs)
                actions[key] = act
            next_state, reward, terminal, info = dyenv.step(actions)
            if terminal:
                break
            state = next_state
        self.toJsonFile(dyenv)

    def generate_graph(self,node_cnt):
        """ this method focus structue of graph, dose't concern about value of road or node 
        """
        nodes = []
        for i in range(node_cnt):
            nodes.append({"id" : i})
        edges = []
        for i in range(node_cnt):
            for j in range(node_cnt):
                if i == j: continue
                r = random.randint(0,1)
                if r  == 1:
                    edges.append({"source" : i, "target": j})
        data = {
            "nodes" : nodes,
            "edges" : edges,
        }
        filename = "graph-" + str(node_cnt) + ".yml"
        with open(GRAPH_CONFIG_PATH+filename, "w", encoding="utf-8") as f:
            yaml.dump(data, f)
    
    def init_graph(self,filename):
        """ this method focus structue of graph, dose't concern about value of road or node 
        """
        data = self.get_yaml_data(GRAPH_CONFIG_PATH + filename)
        nodes = data['nodes']
        roads = data['edges']
        graph = Graph(nodes, roads)
        return graph

    def get_yaml_data(self, yaml_file):
        file = open(yaml_file, 'r', encoding="utf-8")
        file_data = file.read()
        file.close()
        data = yaml.load(file_data, Loader=yaml.Loader)
        return data

    def toJsonFile(self, dyenv):
        graph = dyenv.graph
        adjacency_list = graph.adjacency_list
        road_martix = graph.road_martix
        odm_list = dyenv.odm_list
        nodes = []
        for node in adjacency_list:
            nodes.append({
                'id': node.id,
                'label': node.id,
            })
        edges = []
        for row in road_martix:
            for road in row:
                if(road != None):
                    edges.append({
                        "id": road.id,
                        'source': road.source,
                        'target': road.target,
                        'vehicles': road.vehicles,
                        'toll': road.toll,
                        'length': road.length,
                        'capacity': road.capacity,
                        'freeFlowTravelTime': road.free_flow_travel_time,
                        'label': road.label
                    })
        
        origin_destination_pairs_list = []
        for odm_in_time in odm_list:
            origin_destination_pairs = []
            for row in odm_in_time:
                for od in row:
                    if(od != None):
                        contained_roads_list = []
                        for road in od.contained_roads.values():
                            contained_roads_list.append([road.source, road.target])
                        origin_destination_pairs.append({
                            'origin': od.origin,
                            'destination': od.destination,
                            'demand' : od.demand,
                            'containedRoads' : contained_roads_list
                        })
            origin_destination_pairs_list.append(origin_destination_pairs)
            
        send_data = {
            "nodes" : nodes,
            "edges" : edges,
            "originDestinationPairsList" : origin_destination_pairs_list,
            "historyStates" : dyenv.history_state
        }
        with open('./ui/public/data.json', 'w') as f:
            json.dump(send_data, f, sort_keys=True, indent=4, separators=(',', ': '))

        
