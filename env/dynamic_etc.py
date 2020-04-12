import gym
import math
import random
import json
from env.traffic_graph import TrafficGraph
from env.dyetc_state import DyETCState
import logging
logging.basicConfig(level=10,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')

LENGTH_INTERVAL = [4, 10]
PEEK_DEMAND = [8, 12]
INIT_VEHICLES_RATE = [0.5, 0.7]
INIT_PEEK_RATE = 0.6
MAX_TIMESTEP = 6
INTERVALS = 10
CONSTANT_A = 0.15
CONSTANT_B = 4
SENSITIVITY_TO_TRAVEL_COST = -0.5
VALUE_OF_TIME = 0.5
ACTION_UPPER_BOUND = 6


class DynamicETC(gym.Env):
    """DyETC 的环境容器，主要的属性有
        state: 是 DyETCState 类别。用来表示当前环境的状态
        timestep: 当前环境经历的时间步
        max_timestep: 环境最多经历的时间步
        memory: 存放 timestep 及之前的状态

    """

    def __init__(self, graph_data, state_data=None):
        self.tau = INTERVALS
        self.omega = VALUE_OF_TIME
        self.omega_prime = SENSITIVITY_TO_TRAVEL_COST
        self.constant_a = CONSTANT_A
        self.constant_b = CONSTANT_B
        self.peek_rate = INIT_PEEK_RATE
        self.max_timestep = MAX_TIMESTEP

        self.state = DyETCState(graph_data, state_data)
        self.memory = [self.state]

        self.timestep = 0

    def step(self, actions):
        self.timestep += 1
        tolls = []
        for key, value in actions.items():
            tolls.append({
                "source": value['source'],
                "target": value['target'],
                "toll": value['toll']
            })
        next_state = self.__update_state(tolls)
        self.state = next_state
        self.memory.append(self.state.copy())
        reward = self.__cal_reward()
        terminal = False
        if self.timestep == self.max_timestep:
            terminal = True
        info = {}
        return self.state, reward, terminal, info

    def reset(self):
        self.state = self.memory[0]
        self.timestep = 0
        self.memory = [self.state]
        return self.state

    def render(self, mode=""):
        pass

    def close(self):
        pass

    def __cal_reward(self):
        roads = self.state.get_all_roads()
        reward = 0
        for road in roads:
            vechicels_number = self.state.get_zone_demand_on_road(road.edge_id, road.target)
            reward += vechicels_number * self.tau / (road.free_flow_travel_time * (1 + self.constant_a
                                                                                   * (vechicels_number / road.capacity) ** self.constant_b))
        return reward

    def __update_state(self, tolls):
        roads = self.state.get_all_roads()
        nodes = self.state.get_all_nodes()
        for road in roads:
            toll = tolls[road.edge_id]
            self.state.set_toll_to_road(road.source, road.target, toll)
            for node in nodes:
                # 如果路的起点等于目的则跳过
                if road.source == node.node_id:
                    continue
                road_id = road.edge_id
                dest_id = node.node_id
                od = self.state.get_odp(road.source, dest_id)
                if od != None:
                    road_out = self.__cal_road_out(road_id, dest_id)
                    road_in = self.__cal_road_in(road_id, dest_id)
                    add_vehicles = road_in - road_out
                    self.state.add_zone_demand_on_road(
                        road_id, dest_id, add_vehicles)
        return self.state

    def __cal_road_in(self, road_id, dest_zone_id):
        """[计算进入路 road 上到达特定目的地的车数量]

        Arguments:
            road_id {[int]} -- 
            dest_zone_id {[int]} -- 

        Returns:
            [int] -- 计算进入路 road 上到达特定目的地的车数量
        """
        graph = self.state.traffic_graph
        traffic_state = self.state.traffic_state
        origin_dest_pair_matrix = self.state.origin_dest_pair_matrix

        target_road = graph.get_road_by_id(road_id)
        primary_od_demand = origin_dest_pair_matrix[target_road.source][dest_zone_id].demand
        related_in_roads = graph.get_edges_target_is_node(target_road.source)
        secondary_od_demand = 0
        # find the road which target point is source point of target road
        for road in related_in_roads:
            if road.target != dest_zone_id:
                secondary_od_demand += self.__cal_road_out(
                    road.edge_id, dest_zone_id)

        # paths contain target road
        paths_contains_target_road = self.__get_paths_contain_road(
            target_road.source, dest_zone_id, target_road)
        result = 0
        for path in paths_contains_target_road:
            portion = self.__portion_of_traffic_demand(
                target_road.source, dest_zone_id, path)
            result = (result + (primary_od_demand +
                                secondary_od_demand) * portion)
        return result

    def __cal_road_out(self, road_id, dest_zone_id):
        """[计算离开路 road 上到达特定目的地的车数量]

        Arguments:
            road_id {[type]} -- [description]
            dest_zone_id {[type]} -- [description]
        Returns:
            [int] -- 计算来路 road 上到达特定目的地的车数量
        """
        graph = self.state.traffic_graph
        traffic_state = self.state.traffic_state

        road = graph.get_road_by_id(road_id)
        vechicels_in_road = road.vehicles
        num_in_road_to_zone = traffic_state[road_id][dest_zone_id]
        result = num_in_road_to_zone * self.tau / (road.free_flow_travel_time
                                                   * (1 + self.constant_a * (vechicels_in_road / road.capacity) ** self.constant_b))
        result = min(result, num_in_road_to_zone)
        return result

    def __get_paths_contain_road(self, origin, destination, road):
        """获取两点之间的所有的路径

        Arguments:
            origin {int} -- [description]
            destination {int}} -- [description]
            road {Road} -- [description]

        Returns:
            set --  paths set
        """
        origin_dest_pair_matrix = self.state.origin_dest_pair_matrix

        paths = origin_dest_pair_matrix[origin][destination].paths
        result = set()
        for path in paths:
            if path.is_edge_in_path(road):
                result.add(path)
        return result

    def __portion_of_traffic_demand(self, origin, destination, target_path):
        """根据论文的公式，计算路径 target_path 上应该转移的车数量比例

        Arguments:
            origin {int} -- [description]
            destination {int} -- [description]
            target_path {Path} -- [description]

        Returns:
            [type] -- [description]
        """
        origin_dest_pair_matrix = self.state.origin_dest_pair_matrix

        if origin == destination:
            return 0
        # origin -> dest 上的所有路径
        # target path 是其中一条
        paths = origin_dest_pair_matrix[origin][destination].paths
        base = 0.0
        for path in paths:
            base = base + math.exp(-self.omega_prime *
                                   self.__cal_travel_cost(path))
        if base == 0.0:
            print(" error")
        portion = math.exp(-self.omega_prime *
                           self.__cal_travel_cost(target_path)) / base
        if portion < 0.01:
            print("in")
        return portion

    def __cal_travel_cost(self, path):
        """根据公式计算行驶代价

        Arguments:
            path {Path} -- [description]
        """
        cost = 0.0
        for road in path.roads:
            cost += road.toll * 1.0 + self.omega * self.__cal_travel_time(road)
        return cost

    def __cal_travel_time(self, road):
        """根据公式计算形式时间

        Arguments:
            road {Road} -- [description]
        """
        vechicels_in_road = road.vehicles * 1.0
        travel_time = road.free_flow_travel_time * (1 + self.constant_a
                                                    * (vechicels_in_road / road.capacity * 1.0) ** self.constant_b)
        return travel_time

