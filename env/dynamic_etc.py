import gym
import math
from env.graph import Graph

INTERVALS = 10
CONSTANT_A = 0.15
CONSTANT_B = 4
MAX_TIMESTEP = 6
SENSITIVITY_TO_TRAVEL_COST = 0.5
VALUE_OF_TIME = 0.5
ACTION_UPPER_BOUND = 6

class Path():
    def __init__(self):
        self.roads = []
        self.begin = -1
        self.end = -1
        self.length = 0

    def add_road(self, road):
        if len(self.roads) == 0:
            self.roads.append(road)
            self.begin = road.begin
            self.end = road.end
        else:
            if self.roads[-1].end == road.begin:
                self.roads.append(road)
                self.end = road.end
            else:
                print(" added road begin point don't equal to last road end point")
        self.length = len(self.roads)
    
    def is_road_in_path(self, road):
        for r in self.roads:
            if r.id == road.id:
                return True
        return False


class OriginDestinationPair():
    """ this is origin destination pair

        Parameters:
            origin : it is the origin zone, reprensented as node id
            destination : it is tht destination zone, represented as node id
            demand: the traffic between origin and destination, it is a integer number
            path set: all path connect origin to destinaion. it is a set. each element is a list. the list element is road, 
                roads concat become a path
    """    
    def __init__(self, origin, destination, paths):
        self.origin = origin
        self.destinaion = destinaion
        self.paths = paths
        self.demand = 0
        self.contained_road = {}
        for path in self.paths:
            for road in path.roads:
                if contained_road.get(road.id) == None:
                    contained_road[road.id] = road

    def update_demand(self):
        # update deman depand on traffic deman on each road
        pass

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

    Para
    """    
    def __init__(self):
        self.graph = Graph()
        self.initGraph(self.graph)

        # state, od, graph should be in same sisutation.
        # only state will be directly updated
        # od and graph updated based on state 
        self.max_timestep = MAX_TIMESTEP
        self.timestep = 0

        # this is a list whose len equals to max_timestep which store the states
        # its dimension is max_timestep * road cnt * node cnt
        self.history_state = [] 
        for _ in range(self.max_timestep):
            self.history_state.append([ 
                [0 for _ in range(self.graph.get_nodes_cnt)] 
                    for _ in range(self.graph.get_roads_cnt) ])

        # this represent the current state of environment
        self.state = self.history_state[0]
        self.init_state(self.state)

        # a matrix sotre the originDesntion. 
        # (i,j) represnet the OD whose origin is i and destination is j
        self.originDestinationMatrix = []
        for i in range(self.graph.get_nodes_cnt()):
            self.originDestinationMatrix.append([])
            for j in range(self.graph.get_nodes_cnt()):
                self.originDestinationMatrix[i].append(
                    OriginDestinationPair(origin=i, destinaion=j,paths=self.graph.get_paths_between_two_zone(origin, destinaion))

        # update originDestinationMatrix based on state
        self.update_od()

        # graph attribute is based on state
        self.update_graph()

        # indivicudal action value bewteen 0 and 1
        # and it is a joint action which has roads_cnt actions
        self.action_space = [0, 1, self.graph.get_roads_cnt()]
        self.observation_space = [self.graph.get_roads_cnt(), self.graph.get_nodes_cnt()]

        self.tau = INTERVALS
        self.omega = VALUE_OF_TIME
        self.omega_prime = SENSITIVITY_TO_TRAVEL_COST
        self.constant_a = CONSTANT_A
        self.constant_b = CONSTANT_B

    def step(self, action):
        for i in len(self.state):
            s_e = self.state[i]
            for j in len(s_e):
                s_e_j = s_e[j]
                self.history_state[self.timestep+1][i][j] = s_e_j - self.cal_road_out(i, j) + self.cal_road_in(i, j)
        self.timestep += 1
        self.state = self.history_state[self.timestep]
        reward = self.cal_reward()
        terminal = False
        if self.timestep == self.max_timestep:
            terminal = True
        info = {}
        return self.state, reward, terminal, info

    def reset(self):
        pass

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

        related_roads = self.graph.get_node_related_roads(target_road.begin)
        secondary_od_demand = 0
        # find the road which end point is begin point of target road
        for r in related_roads:
            if r.end == target_road.begin:
                secondary_od_demand += self.cal_road_out(r, destination)

        # paths contain target road
        paths_contains_target_road = self.find_contain_road_paths(target_road.begin, destination, target_road)
        result = 0
        for path in paths_contains_target_road:
            result = result + (primary_od_demand + secondary_od_demand) * self.portion_of_traffic_demand(target_road.begin, destination, path)
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
        result = self.state[e][destination] * self.tau / (road.t_0 * 
                    ( 1 + self.constant_a *（vechicels_in_e / road.capacity）** self.constant_b) )
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
        paths = self.originDestinationMatrix[begin][end].paths
        base = 0
        for path in paths:
            base = base + math.exp(-self.omega_prime * self.cal_travel_cost(path))
        portion = math.exp(-self.omega_prime * self.cal_travel_cost(target_path)) / base
        return portion
    
    def cal_travel_cost(self, path):
        """calculate travel cost in path
        
        Arguments:
            path {Path} -- target path
        
        Returns:
            int -- travel cost
        """        
        cost = 0
        for road in path.roads:
            cost += road.e + self.omega * self.cal_travel_time(road)
        return cost
    
    def cal_travel_time(self, road):
        """calculate travel time on road e
        
        Arguments:
            road {Road} -- target road
        
        Returns:
            [int] -- [travel time]
        """        
        vechicels_in_road = road.vechicels
        travel_time = road.t_0 * (1 + self.constant_a 
            * (vechicels_in_road / road.capacity) ** self.constant_b)
        return travel_time

    def cal_reward(self):
        roads = self.graph.get_roads()
        reward = 0
        for road in roads:
            vechicels_number = self.state[road.id][end]
            reward += vechicels_number * self.tau / (road.t_0 * (1 + self.constant_a 
                * (vechicels_number / road.capacity) ** self.constant_b))
        return reward

    def update_od(self):
        for row in self.originDestinationMatrix:
            for od in row:
                roads = od.contained_road
                od.demand = 0
                for road in roads
                    od.demand += road.vechicels
            
    def update_graph(self):
        roads = self.graph.get_roads()
        for road in roads:
            road.vechicels = 0
            for num in self.state[road.id]:
                road.vechicels += num

    def init_state(self,state):
        pass

    def init_graph(self):
        pass
