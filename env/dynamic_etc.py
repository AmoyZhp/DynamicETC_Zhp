import gym
import math
import random
import yaml
from env.graph import Graph

INTERVALS = 10
CONSTANT_A = 0.15
CONSTANT_B = 4
MAX_TIMESTEP = 6
SENSITIVITY_TO_TRAVEL_COST = 0.5
VALUE_OF_TIME = 0.5
ACTION_UPPER_BOUND = 6
LENGTH_INTERVAL = [4, 10]
PEEK_DEMAND = [8, 12]
INIT_VEHICLES_RATE = [0.5, 0.7]
INIT_PEEK_RATE = 0.6




class OriginDestinationPair():
    """ this is origin destination pair

        Parameters:
            origin : it is the origin zone, reprensented as node id
            destination : it is tht destination zone, represented as node id
            demand: the traffic between origin and destination, it is a integer number
            path set: all path connect origin to destination. it is a set. each element is a list. the list element is road, 
                roads concat become a path
    """    
    def __init__(self, origin, destination, paths):
        self.origin = origin
        self.destination = destination
        self.paths = paths
        self.demand = 0
        self.contained_roads = {}
        for path in self.paths:
            for road in path.roads:
                if self.contained_roads.get(road.id) == None:
                    self.contained_roads[road.id] = road

    def get_contained_roads(self):
        return self.contained_roads.values()

    def add_demand(self, num):
        self.demand += 0
    
    def set_demand(self, num):
        self.demand = 0
        

class DynamicETC(gym.Env):
    """
    Descprtion: 
        The dynamic etc environment
    
    Graph:
        The road network graph

    State :
        Type: List(|E| * |V|) |E| reprensent the numbers of road in graph,  |V| represent the numbers
        of node in graph
        (i, j) means the number of vechicels in road i whose destination is node j

    Action : 
        Type: List(|E|)
        i means the toll assign to road i.

    Para
    """    
    def __init__(self):
        self.graph = self.init_graph()

        self.max_timestep = MAX_TIMESTEP
        self.timestep = 0
        self.history_state = self.init_state(self.graph, self.max_timestep) 
        # this represent the current state of environment
        self.state = self.history_state[0]

        # a matrix sotre the originDesntion. 
        # (i,j) represnet the OD whose origin is i and destination is j
        self.originDestinationMatrix = self.init_od(self.graph)
        # state, od, graph should be in same sisutation.
        # only state will be directly updated
        # od and graph updated based on state 
        # this is a list whose len equals to max_timestep which store the states
        # its dimension is max_timestep * road cnt * node cnt
        self.update_graph(self.state)
        self.update_od(self.state)


        # indivicudal action value bewteen 0 and 1
        # and it is a joint action which has roads_cnt actions
        self.action_space = [0, 1, self.graph.get_roads_cnt()]
        self.observation_space = [self.graph.get_roads_cnt(), self.graph.get_nodes_cnt()]

        self.tau = INTERVALS
        self.omega = VALUE_OF_TIME
        self.omega_prime = SENSITIVITY_TO_TRAVEL_COST
        self.constant_a = CONSTANT_A
        self.constant_b = CONSTANT_B
        self.peek_rate = 0.6

    def step(self, actions):
        # assign toll to each road
        for key, value in actions.items():
            road = self.graph.get_road_by_id(key)
            self.graph.set_toll_in_road(road.begin, road.end, value)

        for i in range(len(self.state)):
            s_e = self.state[i]
            for j in range(len(s_e)):
                s_e_j = s_e[j]
                road = self.graph.get_road_by_id(i)
                if road.begin == j:
                    continue
                od = self.originDestinationMatrix[road.begin][j]
                if od != None:
                    # state transition function
                    updated_value = - self.cal_road_out(i, j) + self.cal_road_in(i, j)
                    self.history_state[self.timestep+1][i][j] = s_e_j  + updated_value
                    # # new vehilces added to road
                    self.history_state[self.timestep+1][i][j] += random.randint(8, 12) * self.tau * self.peek_rate
        self.timestep += 1

        if self.timestep <= 3:
            self.peek_rate += 0.1
        else:
            self.peek_rate -= 0.1

        self.state = self.history_state[self.timestep]
        self.update_od(self.state)
        self.update_graph(self.state)
        reward = self.cal_reward()
        terminal = False
        if self.timestep == self.max_timestep:
            terminal = True
        info = {}
        return self.state, reward, terminal, info

    def reset(self):
        self.history_state = self.init_state(self.graph, self.max_timestep) 
        self.state = self.history_state[0]
        self.update_graph(self.state)
        self.update_od(self.state)
        return self.state

    def render(self,mode=""):
        pass

    def close(self):
        pass

    def cal_road_in(self, e, destination):
        """calcualate the vehicles enter road e
        
        Arguments:
            e {int} -- index of road
            destination {int} -- index of zone
        
        Returns:
            int -- number of vehicles enter road e
        """        
        target_road = self.graph.get_road_by_id(e)

        primary_od_demand = self.originDestinationMatrix[target_road.begin][destination].demand

        related_in_roads = self.graph.get_node_related_in_roads(target_road.begin)
        secondary_od_demand = 0
        # find the road which end point is begin point of target road
        for r in related_in_roads:
            if r.end != destination:
                secondary_od_demand += self.cal_road_out(r.id, destination)

        # paths contain target road
        paths_contains_target_road = self.find_contain_road_paths(target_road.begin, destination, target_road)
        result = 0
        for path in paths_contains_target_road:
            result = (result + (primary_od_demand + secondary_od_demand) 
                * self.portion_of_traffic_demand(target_road.begin, destination, path))
        return result

    def cal_road_out(self, e, destination):
        """calcualte the vechicles levae road e
        
        Arguments:
            e {int} -- index of road e
            destination {int} -- index of zone
        
        Returns:
            int -- number of vechicles leava road e
        """        
        # last num is sum of col in row e
        road = self.graph.get_road_by_id(e)
        vechicels_in_e = road.vechicels
        result = self.state[e][destination] * self.tau / (road.free_flow_travel_time 
            * ( 1 + self.constant_a * (vechicels_in_e / road.capacity) ** self.constant_b ))
        return result
    
    def find_contain_road_paths(self, begin, end, road):
        """find the paths which contain target road
        
        Arguments:
            begin {int} -- index of begin node
            end {int} -- index of end node
            road {Road} -- target road, want to find the path
                contain this road

        Returns:
            List<Path> -- a path list whose path contains target road
        """        
        paths = self.originDestinationMatrix[begin][end].paths
        result = []
        for path in paths:
            if path.is_road_in_path(road):
                result.append(path)
        return result

    def portion_of_traffic_demand(self, begin, end, target_path):
        """calulcat the portion of traffic demand in target_path, target_path is one of the path in
            path set between begin point and end point
        
        Arguments:
            begin {int} -- index of begin node
            end {int} -- index of end  node
            target_path {[Path]} -- target path
        """
        if begin == end:
            return 0
        paths = self.originDestinationMatrix[begin][end].paths
        base = 0.0
        for path in paths:
            base = base + math.exp(-self.omega_prime * self.cal_travel_cost(path)) 
        if base == 0.0:
            print(" error")
        portion = math.exp(-self.omega_prime * self.cal_travel_cost(target_path))/ base
        return portion
    
    def cal_travel_cost(self, path):
        """calculate travel cost in path
        
        Arguments:
            path {Path} -- target path
        
        Returns:
            int -- travel cost
        """        
        cost = 0.0
        for road in path.roads:
            cost += road.toll * 1.0 + self.omega * self.cal_travel_time(road)
        return cost
    
    def cal_travel_time(self, road):
        """calculate travel time on road e
        
        Arguments:
            road {Road} -- target road
        
        Returns:
            [int] -- [travel time]
        """        
        vechicels_in_road = road.vechicels * 1.0
        travel_time = road.free_flow_travel_time * (1 + self.constant_a 
            * (vechicels_in_road / road.capacity) ** self.constant_b)
        return travel_time

    def cal_reward(self):
        roads = self.graph.get_all_roads()
        reward = 0
        for road in roads:
            vechicels_number = self.state[road.id][road.end]
            reward += vechicels_number * self.tau / (road.free_flow_travel_time * (1 + self.constant_a 
                * (vechicels_number / road.capacity) ** self.constant_b))
        return reward

    def update_od(self, state):
        for row in self.originDestinationMatrix:
            for od in row:
                if od == None:
                    continue
                roads = od.get_contained_roads()
                od.set_demand(0)
                for road in roads:
                    od.add_demand(state[road.id][od.destination])
            
    def update_graph(self, state):
        roads = self.graph.get_all_roads()
        for road in roads:
            vechicels = 0
            for num in state[road.id]:
                vechicels += num
            self.graph.set_vechicels_in_road(road.begin, road.end, vechicels)
    
    def init_od(self, graph):
        originDestinationMatrix = []
        node_cnt = graph.get_nodes_cnt()
        for _ in range(node_cnt):
            row = []
            for j in range(node_cnt):
                row.append(None)
            originDestinationMatrix.append(row)
        for i in range(node_cnt):
            for j in range(node_cnt):
                paths = graph.get_paths_between_two_zone(i, j)
                if len(paths) > 0:
                    originDestinationMatrix[i][j] = OriginDestinationPair(i, j ,paths)
        return originDestinationMatrix
        

    def init_state(self, graph, max_timestep):
        history_state = []
        road_cnt = graph.get_roads_cnt()
        node_cnt = graph.get_nodes_cnt()
        for _ in range(max_timestep+1):
            # E x V
            state = [ [0 for _ in range(node_cnt)] 
                        for _ in range(road_cnt) ]
            history_state.append(state)
        init_state = history_state[0]
        roads = graph.get_all_roads()
        for road in roads:
            vechicels = road.capacity * random.uniform(INIT_VEHICLES_RATE[0], INIT_VEHICLES_RATE[1])
            graph.set_vechicels_in_road(road.begin, road.end, vechicels)
            # assume this is full connected graph
            cnt = 0
            for i in range(len(state[road.id])):
                if road.end != i:
                    paths = graph.get_paths_between_two_zone(road.begin, i)
                    if len(paths) != 0:
                        cnt += 1
            for i in range(len(state[road.id])):
                if road.end != i:
                    paths = graph.get_paths_between_two_zone(road.begin, i)
                    if len(paths) != 0:
                        init_state[road.id][i] = int(road.vechicels / cnt)
        return history_state

    def init_graph(self):
        """ this method focus structue of graph, dose't concern about value of road or node 
        """        
        data = self.get_yaml_data("/Users/zhanghaopeng/CodeHub/2020Spring/DyETC/env/graph_config.yml")
        nodes = data['nodes']
        roads = data['roads']
        for road in roads:
            road['length'] = random.randint(LENGTH_INTERVAL[0], LENGTH_INTERVAL[1])
            road['toll'] = random.randint(0, 6)
        graph = Graph(nodes, roads)
        return graph
    
    def get_yaml_data(self, yaml_file):
        file = open(yaml_file, 'r', encoding="utf-8")
        file_data = file.read()
        file.close()
        data = yaml.load(file_data, Loader=yaml.Loader)
        return data

if __name__ == "__main__":
    dyenv = DynamicETC()
    print(dyenv.state)