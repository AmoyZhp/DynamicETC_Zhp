from env.dynamic_etc import DynamicETC
from agent.default_agent import DefaultAgent 
import json
class Runner():
    def __init__(self):
        super().__init__()
    
    def process_state_to_obs(self, state, i):
        return []

    def run(self):
        dyenv = DynamicETC()
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
            print(cnt)
            cnt += 1
            state = next_state
        self.toJsonFile(dyenv)
        graph = dyenv.graph
        adjacency_list = graph.adjacency_list
        road_martix = graph.road_martix
        # state = dyenv.history_state
        # print(json.dumps(state))
        # originDestinationMatrix = dyenv.originDestinationMatrix
    
    def toJsonFile(self, dyenv):
        graph = dyenv.graph
        adjacency_list = graph.adjacency_list
        road_martix = graph.road_martix
        originDestinationMatrix = dyenv.originDestinationMatrix
        nodes = []
        for node in adjacency_list:
            nodes.append({
                'id': node.id,
                'label': node.label,
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
        originDestinationPairs = []
        for row in originDestinationMatrix:
            for od in row:
                if(od != None):
                    originDestinationPairs.append({
                        'origin': od.origin,
                        'destination': od.destination,
                        'demand' : od.demand,
                        'containedRoads' : list(od.contained_roads.keys())
                    })
        send_data = {
            "nodes" : nodes,
            "edges" : edges,
            "originDestinationPairs" : originDestinationPairs,
            "dyetcState" : dyenv.history_state
        }
        with open('./ui/public/data.json', 'w') as f:
            json.dump(send_data, f, sort_keys=True, indent=4, separators=(',', ': '))

        
