import gym
from env.graph import Graph

class DynamicETC(gym.Env):
    """
    Descprtion: 
        The dynamic etc environment
    
    Graph:
        The road network graph

    Observation:
        Type: List(|E| * |V|) |E| reprensent the numbers of road in graph,  |V| represent the numbers
        of node in graph
        (i, j) means the number of vechicels in road i whose destination is node j

    Action : 
        Type: List(|E|)
        i means the toll assign to road i.
    """    
    def __init__(self):
        self.graph = Graph()
        self.state = self.parase_graph_to_state(graph)
        self.action_space = self.graph.get_roads_cnt()
        self.observation_space = self.graph.get_nodes_cnt() * self.graph.get_roads_cnt()
        

    def parase_graph_to_state(self, graph):
        pass

    def step(self, action):
        pass

    def reset(self):
        pass

    def render(self,mode=""):
        pass

    def close(self):
        pass

