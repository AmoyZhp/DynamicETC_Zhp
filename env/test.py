from graph import *
import yaml
import os
import random

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

def get_yaml_data(yaml_file):
    file = open(yaml_file, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    data = yaml.load(file_data, Loader=yaml.Loader)
    return data
if __name__ == "__main__":
    data = get_yaml_data("/Users/zhanghaopeng/CodeHub/2020Spring/DyETC/env/graph_config.yml")
    nodes = data['nodes']
    roads = data['roads']
    for road in roads:
        road['length'] = random.randint(LENGTH_INTERVAL[0], LENGTH_INTERVAL[1])
        road['toll'] = random.randint(0, 6)
    graph = Graph(nodes, roads)
    roads = graph.get_all_roads()
    for road in roads:
        print(road.__str__())
        
    for i in range(len(nodes)):
        for j in range(len(nodes)):
            paths = graph.get_paths_between_two_zone(i,j)
            if len(paths) > 0:
                for path in paths:
                    print(path.__str__())
    roads = graph.get_node_related_in_roads(0)
    for road in roads:
        print(road.__str__())
    roads = graph.get_node_related_out_roads(0)
    for road in roads:
        print(road.__str__())