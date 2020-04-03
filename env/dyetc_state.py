from env.traffic_graph import TrafficGraph
import random
import logging
import math
logging.basicConfig(level=10,
         format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s') 

LENGTH_INTERVAL = [4, 10]
PEEK_DEMAND = [8, 12]
INIT_VEHICLES_RATE = [0.5, 0.7]
INIT_PEEK_RATE = 0.6

class DyETCState():
    """用来表示 DyETC 的一个整体的环境状态。它主要有三个子项
        traffic_state: 是一个 |E| x |V| 的矩阵。 (e,v) 表示路 e 上目的是 v 的车辆的数量
        traffic_graph: 是交通的图表示
        origin_dest_pair_matrix: 是一个 |V| x |V| 的矩阵。
            (row, col) 表示起始点是 row 终点是 col 的origin destination pair 
    """    
    def __init__(self, traffic_graph:TrafficGraph, traffic_state=None):
        self.traffic_graph = traffic_graph
        edges_cnt = traffic_graph.get_edges_cnt()
        nodes_cnt = traffic_graph.get_nodes_cnt()
        # E x V
        self.traffic_state = [ [0 for _ in range(nodes_cnt)] 
                    for _ in range(edges_cnt) ]
        self.origin_dest_pair_list = []
        self.origin_dest_pair_matrix = []
        for _ in range(nodes_cnt):
                row = []
                for _ in range(nodes_cnt):
                    row.append(None)
                self.origin_dest_pair_matrix.append(row)
        # 初始化 OD list 和 martix
        nodes_cnt = self.traffic_graph.get_nodes_cnt()
        for origin in range(nodes_cnt):
            for dest in range(nodes_cnt):
                paths = self.traffic_graph.get_paths_between_nodes(origin, dest)
                if len(paths) > 0:
                    od = OriginDestinationPair(origin, dest ,paths)
                    self.origin_dest_pair_matrix[origin][dest] = od
                    self.origin_dest_pair_list.append(od)
        # 如果有初始化 state 就用传入的 state 初始化，否则就随机初始化
        if traffic_state != None:
            if (len(traffic_state) > 0 and len(traffic_state) == len(self.traffic_state)
                and len(traffic_state[0]) == len(self.traffic_state[0])):
                self.traffic_state = traffic_state
                self.__update_graph()
                self.__update_od()
        else:
            self.__random_init()

    def update(self, new_state):
        next_state = DyETCState(self.traffic_graph, new_state)
        return next_state
    
    def get_traffic_graph(self):
        return self.traffic_graph

    def __random_init(self):
        roads = self.traffic_graph.get_all_roads()
        # 初始化 traffic state
        for road in roads:
            # 初始化每条路上的车辆的数目
            length = random.randint(LENGTH_INTERVAL[0], LENGTH_INTERVAL[1])
            self.traffic_graph.init_road_length(road.source, road.target, length)
            vehicles = road.capacity * random.uniform(INIT_VEHICLES_RATE[0], INIT_VEHICLES_RATE[1])
            self.traffic_graph.set_road_vechicels_val(road.source, road.target, vehicles)
            self.traffic_graph.set_road_toll(road.source, road.target, random.randint(0, 6))
            # 将路上的车辆的目的地平均分配到经过的点
            cnt = 0
            for i in range(len(self.traffic_state[road.edge_id])):
                if road.source != i:
                    paths = self.traffic_graph.get_paths_between_nodes(road.source, i)
                    if len(paths) != 0:
                        cnt += 1
            for i in range(len(self.traffic_state[road.edge_id])):
                if road.source != i:
                    paths = self.traffic_graph.get_paths_between_nodes(road.source, i)
                    if len(paths) != 0:
                        self.traffic_state[road.edge_id][i] = int(road.vehicles / cnt)

    def __update_od(self):
        # 更新每一个 OD 的 demand 值
        for row in self.origin_dest_pair_matrix:
            for od in row:
                if od == None:
                    continue
                roads = od.get_contained_roads()
                od.set_demand(0)
                for road in roads:
                    if road.source == od.origin:
                        od.add_demand(self.traffic_state[road.edge_id][od.destination])

    def __update_graph(self):
        # 更新图上每条路的车辆的数目
        roads = self.traffic_graph.get_all_roads()
        for road in roads:
            vehicles = 0
            for num in self.traffic_state[road.edge_id]:
                vehicles += num
            self.traffic_graph.set_road_vechicels_val(road.source, road.target, vehicles)
    


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
                if self.contained_roads.get(road.edge_id) == None:
                    self.contained_roads[road.edge_id] = road

    def get_contained_roads(self):
        return self.contained_roads.values()

    def add_demand(self, num):
        self.demand += num
    
    def set_demand(self, num):
        self.demand = 0