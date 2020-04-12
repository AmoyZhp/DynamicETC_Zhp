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
INTERVALS = 10

class DyETCState():
    """用来表示 DyETC 的一个整体的环境状态。它主要有三个子项
        traffic_state: 是一个 |E| x |V| 的矩阵。 (e,v) 表示路 e 上目的是 v 的车辆的数量
        traffic_graph: 是交通的图表示
        origin_dest_pair_matrix: 是一个 |V| x |V| 的矩阵。
            (row, col) 表示起始点是 row 终点是 col 的origin destination pair
    """

    def __init__(self, graph_data, state_data = None):
        nodes = graph_data['nodes']
        roads = graph_data['edges']
        self.traffic_graph = TrafficGraph(nodes, roads)
        edges_cnt = self.traffic_graph.get_edges_cnt()
        nodes_cnt = self.traffic_graph.get_nodes_cnt()
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
        if state_data == None:
            state_data = self.__random_init_state(self.traffic_graph)
        # 初始化 路 的参数
        roads_data = state_data['roads']
        for road_data in roads_data.values():
            source = road_data['source']
            target = road_data['target']
            self.traffic_graph.init_road_length(source, target,
                                                road_data['length'])
            self.traffic_graph.set_road_vehicles_val(
                source, target, road_data['vehicles'])

        # 初始化 traffic state
        traffic_state_data = state_data['traffic_state']
        if (len(traffic_state_data) == len(self.traffic_state) and
                len(traffic_state_data[0]) == len(self.traffic_state[0])):
            for row in range(len(self.traffic_state)):
                vehicles_cnt = 0
                for col in range(len(self.traffic_state[row])):
                    self.traffic_state[row][col] = traffic_state_data[row][col]
                    vehicles_cnt += traffic_state_data[row][col]
                if roads_data[row]['vehicles'] - vehicles_cnt > 5:
                    logging.debug(
                        'vehicles on road and vehicles put on state is not matched')
        else:
            logging.debug('traffic state dim is not matched witch init data')

        # 初始化 Origin Destination Pair 矩阵
        odp_martix = state_data['odp_matrix']
        if (len(odp_martix) == len(self.origin_dest_pair_matrix) and
                len(odp_martix[0]) == len(self.origin_dest_pair_matrix[0])):
            for row in range(len(self.origin_dest_pair_matrix)):
                for col in range(len(self.origin_dest_pair_matrix[row])):
                    odp = self.origin_dest_pair_matrix[row][col]
                    if odp != None:
                        odp.set_demand(odp_martix[row][col])

    def set_toll_to_road(self, source, target, toll):
        self.traffic_graph.set_road_toll(source, target, toll)

    def get_odp(self, origin, dest):
        if self.traffic_graph.is_legal_node(origin) and self.traffic_graph.is_legal_node(dest):
            return self.origin_dest_pair_matrix[origin][dest]
        else:
            return None

    def add_zone_demand_on_road(self, road_id, dest_id, num):
        road = self.traffic_graph.get_road_by_id(road_id)
        if (self.traffic_graph.is_legal_node(dest_id) and
                road != None):
            self.traffic_state[road_id][dest_id] += num
            self.traffic_graph.add_road_vehicles_val(
                road.source, road.target, num)

    def add_demand_of_odp(self, origin, dest, demand):
        if (self.traffic_graph.is_legal_node(origin) and self.traffic_graph.is_legal_node(dest)):
            self.origin_dest_pair_matrix[origin][dest] += demand
            return True
        else:
            return False

    def copy(self):
        graph_data = self.traffic_graph.to_json_data()
        graph = TrafficGraph(graph_data['nodes'], graph_data['edges'])
        init_data = self.__dict__()
        return DyETCState(graph, init_data=init_data)

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
            self.traffic_graph.set_road_vehicles_val(
                road.source, road.target, vehicles)

    def __random_init_state(self, graph):
        """ 如果没有传入初始状态的设定，则使用该函数随机初始化交通状态

        Arguments:
            graph {TrafficGraph} -- 

        Returns:
            [dict] -- 包含初始化状态所需要的信息
        """
        roads = graph.get_all_roads()
        nodes = graph.get_all_edges()
        edges_cnt = graph.get_edges_cnt()
        nodes_cnt = graph.get_nodes_cnt()
        init_state = {}

        # 初始化路上的车辆数目
        roads_dict = {}
        traffic_state = [[0 for _ in range(nodes_cnt)]
                         for _ in range(edges_cnt)]
        for road in roads:
            # 初始化每条路上的车辆的数目
            length = random.randint(LENGTH_INTERVAL[0], LENGTH_INTERVAL[1])
            road.init_length(length)
            vehicles = int(road.capacity *
                           random.uniform(INIT_VEHICLES_RATE[0], INIT_VEHICLES_RATE[1]))
            roads_dict[road.edge_id] = {
                'source': road.source,
                'target': road.target,
                'length': length,
                'vehicles': vehicles,
            }
            # 将路上的车辆的目的地平均分配到经过的点
            cnt = 0
            for i in range(nodes_cnt):
                if road.source != i:
                    paths = graph.get_paths_between_nodes(
                        road.source, i)
                    if len(paths) != 0:
                        cnt += 1
            for i in range(nodes_cnt):
                if road.source != i:
                    paths = graph.get_paths_between_nodes(
                        road.source, i)
                    if len(paths) != 0:
                        traffic_state[road.edge_id][i] = int(
                            vehicles / cnt)
        init_state['roads'] = roads_dict
        init_state['traffic_state'] = traffic_state

        # 初始化 odp 矩阵
        odp_matrix = []
        for _ in range(nodes_cnt):
            row = []
            for _ in range(nodes_cnt):
                row.append(None)
            odp_matrix.append(row)
        for origin in range(nodes_cnt):
            for dest in range(nodes_cnt):
                paths = graph.get_paths_between_nodes(
                    origin, dest)
                if len(paths) > 0:
                    odp_matrix[origin][dest] = int(random.randint(
                        PEEK_DEMAND[0], PEEK_DEMAND[1]) * INIT_PEEK_RATE * INTERVALS)

        init_state['odp_matrix'] = odp_matrix
        return init_state

    def __dict__(self):
        data = {}
        roads_data = []
        for road in self.traffic_graph.get_all_roads():
            roads_data.append({
                'source': road.source,
                'target': road.target,
                'length': road.length,
                'vehicles': road.vehicles
            })
        nodes_cnt = self.traffic_graph.get_nodes_cnt()
        odp_matrix = [[0 for _ in range(nodes_cnt)]
                      for _ in range(nodes_cnt)]
        for row in range(nodes_cnt):
            for col in range(nodes_cnt):
                odp_matrix[row][col] = self.origin_dest_pair_matrix[row][col].demand

        data['roads'] = roads_data
        data['traffic_state'] = traffic_state
        data['odp_matrix'] = odp_matrix
        return data


class OriginDestinationPair():
    """ this is origin destination pair

        Parameters:
            origin : it is the origin zone, reprensented as node id
            destination : it is tht destination zone, represented as node id
            demand: the traffic between origin and destination, it is a integer number
            path set: all path connect origin to destination. it is a set. each element is a list. the list element is road, 
                roads concat become a path
    """

    def __init__(self, origin, destination, paths, demand=0):
        self.origin = origin
        self.destination = destination
        self.paths = paths
        self.demand = demand
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
