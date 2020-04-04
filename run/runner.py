from env.dynamic_etc import DynamicETC
from agent.default_agent import DefaultAgent 
from env.traffic_graph import TrafficGraph
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
        agents = self.init_agents(graph)
        state = dyenv.reset()
        while True:
            actions = {}
            # 获取联合行动
            for key, agent in agents.items():
                obs = self.process_state_to_obs(state, key)
                act = agent.act(obs)
                actions[key] = act
            next_state, reward, terminal, info = dyenv.step(actions)
            if terminal:
                break
            state = next_state
        self.toJsonFile(dyenv)
    
    def init_agents(self, graph:TrafficGraph):
        agents = {}
        roads = graph.get_all_roads()
        for road in roads:
            agent = DefaultAgent(road.edge_id, road.source, road.target)
            agents[road.edge_id] = agent
        return agents

    def init_graph(self,filename):
        """ 初始化的图只有边和节点的信息，具体的 车辆等信息 在 dyetc env 在完成初始化 
        """
        data = self.get_yaml_data(GRAPH_CONFIG_PATH + filename)
        nodes = data['nodes']
        roads = data['edges']
        graph = TrafficGraph(nodes, roads)
        return graph
        
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

    def get_yaml_data(self, yaml_file):
        file = open(yaml_file, 'r', encoding="utf-8")
        file_data = file.read()
        file.close()
        data = yaml.load(file_data, Loader=yaml.Loader)
        return data

    def toJsonFile(self, dyenv: DynamicETC):
        memory = dyenv.memory

        trajectory = []
        for state in memory:
            # state 是一个 Dynamic ETC State 类
            graph = state.traffic_graph
            odp_list = state.origin_dest_pair_list
            zones_list = graph.get_all_nodes()
            road_list = graph.get_all_roads()

            zones = []
            for zone in zones_list:
                zones.append({
                    'id': zone.node_id,
                    'label': zone.node_id,
                })

            roads = []
            for road in road_list:
                roads.append({
                    "id": road.edge_id,
                    'source': road.source,
                    'target': road.target,
                    'vehicles': road.vehicles,
                    'toll': road.toll,
                    'length': road.length,
                    'capacity': road.capacity,
                    'freeFlowTravelTime': road.free_flow_travel_time,
                    'label': road.label
                })
        
            origin_destination_pairs = []
            for od in odp_list:
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
            trajectory.append({
                "zones": zones,
                "roads": roads,
                "trafficState": state.traffic_state,
                "originDestPairs": origin_destination_pairs,
            })
            
        send_data = {
            "trajectory" : trajectory
        }
        with open('./ui/public/data.json', 'w') as f:
            json.dump(send_data, f, sort_keys=True, indent=4, separators=(',', ': '))

        
