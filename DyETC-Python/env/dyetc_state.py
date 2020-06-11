from env.traffic_graph import TrafficGraph
import random
import logging
import math
import copy

LENGTH_INTERVAL = [6, 15]
INIT_VEHICLES_RATE = [0.5, 0.7]
PEEK_DEMAND = [8, 12]
INIT_PEEK_RATE = 0.6
INTERVALS = 10
CONSTANT_A = 0.15
CONSTANT_B = 4
SENSITIVITY_TO_TRAVEL_COST = 0.5
VALUE_OF_TIME = 0.05
ACTION_UPPER_BOUND = 6


class DyETCState():

    def __init__(self, graph_data, state_data=None):
        """ DyETC 的状态表示

        Args:
            graph_data (dict): graph data 的字典表示
            state_data (dic, optional): 状态值的字典表示，如路的长度，汽车的多少等. Defaults to None.
        """
        self.graph_data = graph_data
        # 构建交通图
        nodes = graph_data['nodes']
        roads = graph_data['edges']
        self.traffic_graph = TrafficGraph(nodes, roads)

        edges_cnt = self.traffic_graph.get_edges_cnt()
        nodes_cnt = self.traffic_graph.get_nodes_cnt()

        # 初始化 traffic state
        self.traffic_state = [[0 for _ in range(nodes_cnt)]
                              for _ in range(edges_cnt)]
        
        # 初始化 OD list 和 martix
        self.origin_dest_pair_list = []
        self.origin_dest_pair_matrix = []
        for _ in range(nodes_cnt):
            row = []
            for _ in range(nodes_cnt):
                row.append(None)
            self.origin_dest_pair_matrix.append(row)
        
        nodes_cnt = self.traffic_graph.get_nodes_cnt()
        for origin in range(nodes_cnt):
            for dest in range(nodes_cnt):
                paths = self.traffic_graph.get_paths_between_nodes(
                    origin, dest)
                if len(paths) > 0:
                    od = OriginDestinationPair(origin, dest, paths)
                    self.origin_dest_pair_matrix[origin][dest] = od
                    self.origin_dest_pair_list.append(od)
        # 初始化 state data
        if state_data == None:
            state_data = self.__random_init_state(self.traffic_graph)
            self.state_data = state_data
        else :
            self.state_data = state_data
        # 初始化 路 的参数
        roads_data = state_data['roads']
        for road_data in roads_data:
            source = road_data['source']
            target = road_data['target']
            self.traffic_graph.init_road_length(source, target,
                                                road_data['length'])
            self.traffic_graph.set_road_vehicles_val(
                source, target, road_data['vehicles'])
            self.traffic_graph.set_road_toll(source, target, road_data['toll'])

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
        origin_dest_pairs = state_data['origin_dest_pairs']
        if len(origin_dest_pairs) == len(self.origin_dest_pair_list):
            for opd_dict in origin_dest_pairs:
                origin = opd_dict['origin']
                dest = opd_dict['destination']
                demand = opd_dict['demand']
                assert(self.origin_dest_pair_matrix[origin][dest] != None)
                self.origin_dest_pair_matrix[origin][dest].set_demand(demand)

    
    def update(self, tolls):
        assert(len(tolls) == self.traffic_graph.get_edges_cnt())
        for toll in tolls:
            source = toll['source']
            target = toll['target']
            self.traffic_graph.set_road_toll(source, target, toll['toll'])
        # 将所有的路的价格都更新以后再进行
        for road in self.traffic_graph.get_all_roads():
            for node in self.traffic_graph.get_all_nodes():
                if road.source == node.node_id:
                    continue
                # 更新 road 路上到达 zone 的车的数量
                self.__update_traffic_state(road, node)

        # 更新 Origin Destination Pairs Matrix
        for odp in self.origin_dest_pair_list:
            demand = random.randint(
                PEEK_DEMAND[0], PEEK_DEMAND[1]) * INIT_PEEK_RATE * INTERVALS
            odp.set_demand(0)

    def value(self):
        roads = self.traffic_graph.get_all_roads()
        value = 0
        for road in roads:
            vechicels_number = self.traffic_state[road.edge_id][road.target]
            value += min(vechicels_number, 
                int(vechicels_number * INTERVALS / (road.free_flow_travel_time 
                    * (1 + CONSTANT_A * (road.vehicles / road.capacity) ** CONSTANT_B))))
        return value

    def copy(self):
        graph_data = self.traffic_graph.copy()
        traffic_state = self.traffic_state.copy()
        origin_dest_pair_list = self.origin_dest_pair_list.copy()
        origin_dest_pair_matrix = self.origin_dest_pair_matrix.copy()
        init_data = self.data()
        return DyETCState(init_data['graph'], init_data['state'])

    def __update_traffic_state(self, road, zone):
        # 获取起点是 source 终点是 dest_id 的 OD
        source = road.source
        target = road.target
        road_id = road.edge_id
        dest_id = zone.node_id
        odp = self.origin_dest_pair_matrix[source][dest_id]
        if odp != None:
            road_out = self.__cal_road_out(road, zone, odp)
            road_in = self.__cal_road_in(road, zone, odp)
            add_vehicles = int(road_in - road_out)
            self.traffic_state[road_id][dest_id] += add_vehicles
            self.traffic_graph.add_road_vehicles_val(source, target, add_vehicles)

    def __cal_road_in(self, road, zone, odp):
        primary_odp_demand = odp.demand
        # 计算 sceonday_od_demand
        realted_in_roads = self.traffic_graph.get_edges_target_is_node(
            road.source)
        secondary_odp_demand = 0
        for item in realted_in_roads:
            secondary_odp_demand += self.__cal_road_out(item, zone, odp)

        # 将包含目标 road 的路径选出来
        road_in_num = 0
        paths = odp.paths
        for path in paths:
            if path.is_edge_in_path(road):
                portion = self.__portion_of_traffic_demand(path, paths)
                road_in_num += (primary_odp_demand +
                                secondary_odp_demand) * portion

        return road_in_num

    def __cal_road_out(self, road, zone, odp):
        road_id = road.edge_id
        zone_id = zone.node_id
        vehicles_in_road = road.vehicles
        if vehicles_in_road == 0:
            return 0
        vehicles_in_road_to_zone = self.traffic_state[road_id][zone_id]
        road_out_num = vehicles_in_road_to_zone * INTERVALS / (
            road.free_flow_travel_time * (1 + CONSTANT_A * (
                vehicles_in_road / road.capacity
            ) ** CONSTANT_B)
        )
        road_out_num = min(road_out_num, vehicles_in_road_to_zone)
        return road_out_num

    def __portion_of_traffic_demand(self, target_path, all_path):
        """[summary]

        Arguments:
            target_path {Path} -- 需要计算的 protion 的 path
            all_path {List<Path>} -- 包含 target_path 的同样起点和终点的所有路径
        """

        base = 0.0
        for path in all_path:
            base += math.exp(-SENSITIVITY_TO_TRAVEL_COST *
                             self.__cal_travel_cost(path))

        portion = math.exp(-SENSITIVITY_TO_TRAVEL_COST *
                           self.__cal_travel_cost(target_path)) / base

        return portion

    def __cal_travel_cost(self, path):
        """根据公式计算行驶代价

        Arguments:
            path {Path} -- [description]
        """
        cost = 0.0
        for road in path.roads:
            cost += road.toll * 1.0 + VALUE_OF_TIME * \
                self.__cal_travel_time(road)

        return cost

    def __cal_travel_time(self, road):
        """根据公式计算形式时间

        Arguments:
            road {Road} -- [description]
        """
        vehicles = road.vehicles * 1.0
        travel_time = road.free_flow_travel_time * (1 + CONSTANT_A * (
            vehicles / road.capacity * 1.0) ** CONSTANT_B
        )
        return travel_time

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
        roads_list = []
        traffic_state = [[0 for _ in range(nodes_cnt)]
                         for _ in range(edges_cnt)]
        for road in roads:
            # 初始化每条路上的车辆的数目
            length = random.randint(LENGTH_INTERVAL[0], LENGTH_INTERVAL[1])
            road.init_length(length)
            vehicles = int(road.capacity *
                           random.uniform(INIT_VEHICLES_RATE[0], INIT_VEHICLES_RATE[1]))
            roads_list.append({
                'source': road.source,
                'target': road.target,
                'length': length,
                'vehicles': vehicles,
                'toll': 0.0
            })
            # 将路上的车辆的目的地平均分配到经过的点
            # 1 是边到 target 的数量
            cnt = 1 
            for i in range(nodes_cnt):
                    paths = graph.get_paths_between_nodes(
                        road.target, i)
                    if len(paths) != 0:
                        cnt += 1
            for i in range(nodes_cnt):
                    paths = graph.get_paths_between_nodes(
                        road.target, i)
                    if len(paths) != 0 or road.target == i:
                        traffic_state[road.edge_id][i] = int(
                            vehicles / cnt)
        init_state['roads'] = roads_list
        init_state['traffic_state'] = traffic_state

        # 初始化 odp 矩阵
        odp_data = []
        for origin in range(nodes_cnt):
            for dest in range(nodes_cnt):
                paths = graph.get_paths_between_nodes(
                    origin, dest)
                if len(paths) > 0:
                    demand = int(random.randint(
                        PEEK_DEMAND[0], PEEK_DEMAND[1]) * INIT_PEEK_RATE * INTERVALS)
                    odp_data.append({
                        'origin': origin,
                        'destination': dest,
                        'demand': demand,
                    })

        init_state['origin_dest_pairs'] = odp_data
        return init_state

    def data(self):
        # graph data 包含 roads 和 zones  以及 super 的信息
        # super 是静态图，包含 edges 和 zones 的信息
        graph_data = self.traffic_graph.data()
        odp_data = []
        for odp in self.origin_dest_pair_list:
            if odp != None:
                odp_data.append(odp.data())
        traffic_state_data = [[0 for _ in range(len(self.traffic_state[i]))]
                              for i in range(len(self.traffic_state))]
        for i in range(len(self.traffic_state)):
            for j in range(len(self.traffic_state[i])):
                traffic_state_data[i][j] = self.traffic_state[i][j]
        return {
            'state': {
                'roads': graph_data['roads'],
                'traffic_state': traffic_state_data,
                'origin_dest_pairs': odp_data,
            },
            'graph': {
                'edges': graph_data['super']['edges'],
                'nodes': graph_data['super']['nodes'],
            }
        }
        # graph data 包含 roads



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

    def data(self):
        contained_roads_list = []
        for road in self.contained_roads.values():
            contained_roads_list.append(road.__dict__)
        
        paths_list = []
        for path in self.paths:
            paths_list.append(path.data())
        return {
            'origin': self.origin,
            'destination': self.destination,
            'demand': copy.deepcopy(self.demand),
            'paths': paths_list,
            'contained_roads': contained_roads_list
        }

