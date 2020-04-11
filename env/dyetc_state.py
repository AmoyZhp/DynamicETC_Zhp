from env.traffic_graph import TrafficGraph
import random
import logging
import math
logging.basicConfig(level=10,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')

class DyETCState():
    """用来表示 DyETC 的一个整体的环境状态。它主要有三个子项
        traffic_state: 是一个 |E| x |V| 的矩阵。 (e,v) 表示路 e 上目的是 v 的车辆的数量
        traffic_graph: 是交通的图表示
        origin_dest_pair_matrix: 是一个 |V| x |V| 的矩阵。
            (row, col) 表示起始点是 row 终点是 col 的origin destination pair 
    """

    def __init__(self, traffic_graph: TrafficGraph, init_data):
        self.traffic_graph = traffic_graph
        edges_cnt = traffic_graph.get_edges_cnt()
        nodes_cnt = traffic_graph.get_nodes_cnt()
        # E x V
        self.traffic_state = [[0 for _ in range(nodes_cnt)]
                              for _ in range(edges_cnt)]
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
                paths = self.traffic_graph.get_paths_between_nodes(
                    origin, dest)
                if len(paths) > 0:
                    od = OriginDestinationPair(origin, dest, paths)
                    self.origin_dest_pair_matrix[origin][dest] = od
                    self.origin_dest_pair_list.append(od)
        
        # 初始化 路 的参数
        roads_data = init_data['roads']
        for road_data in roads_data.values():
            source = road_data['source']
            target = road_data['target']
            self.traffic_graph.init_road_length(source, target,
                road_data['length'])
            self.traffic_graph.set_road_vechicels_val(source, target, road_data['vehicles'])
        
        # 初始化 traffic state
        traffic_state_data = init_data['traffic_state']
        if (len(traffic_state_data) == len(self.traffic_state) and 
            len(traffic_state_data[0]) == len(self.traffic_state[0])):
            for row in range(len(self.traffic_state)):
                vehicles_cnt = 0
                for col in range(len(self.traffic_state[row])):
                    self.traffic_state[row][col] = traffic_state_data[row][col]
                    vehicles_cnt += traffic_state_data[row][col]
                if roads_data[row]['vehicles'] - vehicles_cnt > 5:
                    logging.debug('vehicles on road and vehicles put on state is not matched')
        else:
            logging.debug('traffic state dim is not matched witch init data')
        
        # 初始化 Origin Destination Pair 矩阵
        odp_martix = init_data['odp_matrix']
        if (len(odp_martix) == len(self.origin_dest_pair_matrix) and
                len(odp_martix[0]) == len(self.origin_dest_pair_matrix[0])):
            for row in range(len(self.origin_dest_pair_matrix)):
                for col in range(len(self.origin_dest_pair_matrix[row])):
                    odp = self.origin_dest_pair_matrix[row][col]
                    if odp != None:
                        odp.set_demand(odp_martix[row][col])
        
    def assign_tolls(self, source, target, toll):
        pass

    def get_odp(self, origin, dest):
        pass

    def add_traffic_state_num(self, road_id, dest_id, num):
        pass
    
    def set_demand_of_odp(self, origin, dest, demand):
        pass

    def copy(self):
        pass
    
    def get_all_roads(self):
        return self.traffic_graph.get_all_roads()

    def get_all_nodes(self):
        return self.traffic_graph.get_all_nodes()
                            
    def __update_graph(self):
        # 更新图上每条路的车辆的数目
        roads = self.traffic_graph.get_all_roads()
        for road in roads:
            vehicles = 0
            for num in self.traffic_state[road.edge_id]:
                vehicles += num
            self.traffic_graph.set_road_vechicels_val(
                road.source, road.target, vehicles)


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
        self.demand = num
