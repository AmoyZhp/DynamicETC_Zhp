from env.static_graph import StaticGraph, Node, Edge
import logging
logging.basicConfig(level=10,
         format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s') 

class TrafficGraph(StaticGraph):
    def __init__(self, node_dict_list, edge_dict_list):
        super().__init__()
        self._init_graph(node_dict_list, edge_dict_list)
    
    def get_all_roads(self):
        return self.edges_list
    
    def get_road(self,source, target):
        if self.is_legal_edge(source, target):
            return self.edges_martix[source][target]

    def get_road_by_id(self, road_id):
        return self.edges_list[road_id]
        
    def get_paths_between_nodes(self, origin_node_id, dest_node_id):
        """ 使用 DFS 的方式搜索两个点之间的所有路径
        
        """
        if not self.is_legal_node(origin_node_id) or not self.is_legal_node(dest_node_id):
            logging.debug("illegal input of get_paths_between_two_zone "
                + "source {} target {}".format(origin_node_id, dest_node_id))
            return []
        if origin_node_id == dest_node_id:
            return []
        paths = []
        nodes = []
        # DFS
        self.__dfs_paths_finding(origin_node_id, dest_node_id, nodes, paths)
        return paths

    def __dfs_paths_finding(self, origin_node_id, dest_node_id, nodes, paths):
        # 如果节点已经在列表中，表示访问到了一个环
        if nodes.count(origin_node_id) > 0:
            return
        nodes.append(origin_node_id)
        node = self.nodes_adjacency_list[origin_node_id]
        if origin_node_id == dest_node_id:
            roads = []
            for i in range(len(nodes)-1):
                road = self.get_road(nodes[i], nodes[i+1])
                roads.append(road)
            paths.append(Path(origin=roads[0].source, 
                        destination=roads[-1].target, roads=roads))
        else:
            neighbor = node.next
            while neighbor != None:
                self.__dfs_paths_finding(neighbor.node_id, dest_node_id, nodes, paths)
                neighbor = neighbor.next
        if len(nodes) > 0 :
            nodes.pop()
                

    def set_road_vechicels_val(self, source, target, vehicles):
        if self.is_legal_edge(source, target):
            self.edges_martix[source][target].set_vechiceles(vehicles)
    
    def set_road_toll(self, source, target, toll):
       if self.is_legal_edge(source, target):
           self.edges_martix[source][target].set_toll(toll)
    
    def init_road_length(self,source, target, length):
        if self.is_legal_edge(source, target):
            self.edges_martix[source][target].init_length(length)

    def _init_graph(self, node_dict_list, edge_dict_list):
        # temp_node_key_id_map 用来将原本的 node id 映射到新的 node id 上
        # 新的 node id 就是根据 node 在数组里的长度设置
        temp_node_key_id_map = {}
        self.nodes_adjacency_list = []
        for node_dict in node_dict_list:
            # 这里的 node 是 Zone
            zone_id = len(self.nodes_adjacency_list)
            zone_label = node_dict.get('label', "")
            zone = Zone(zone_id, zone_label)
            temp_node_key_id_map[node_dict['id']] = zone.node_id
            self.nodes_list.append(zone)
            self.nodes_adjacency_list.append(zone)
        self.nodes_cnt = len(self.nodes_adjacency_list)

        self.edges_list = []
        self.edges_martix = []
        # 边矩阵 (i,j) 指向起点是 i 终点是 j 的边
        for _ in range(self.nodes_cnt):
            row = []
            for _ in range(self.nodes_cnt):
                row.append(None)
            self.edges_martix.append(row)
        self.edges_cnt = 0
        for edge_dict in edge_dict_list:
            # 这里的 egde 是 road
            source = temp_node_key_id_map[edge_dict['source']]
            target = temp_node_key_id_map[edge_dict['target']]
            if self.is_legal_node(source) and self.is_legal_node(target):
                road = Road(edge_id=len(self.edges_list),
                            source=source, target=target)
                self.edges_list.append(road)
                self.edges_martix[road.source][road.target] = road
                # 将边的信息也存进邻接矩阵里
                self._add_edge_to_adjacency_list(source, target)
        self.edges_cnt = len(self.edges_list)
    
    

class Path():
    def __init__(self, origin, destination, roads):
        # roads 是这条路径上的所有路
        self.roads = roads
        self.origin = origin
        self.destination = destination
        self.length = len(roads)
        if self.path_legality_self_check() == False:
            logging.debug("illegal path {}".format(self))
    
    def is_edge_in_path(self, edge):
        for e in self.roads:
            if edge.source == e.source and edge.target == e.target:
                return True
        return False

    def path_legality_self_check(self):
        if len(self.roads) == 0:
            return False

        if self.roads[0].source != self.origin or self.roads[-1].target != self.destination:
            return False

        for i in range(len(self.roads)-1):
            edge_prev = self.roads[i]
            edge_next = self.roads[i+1]
            if edge_prev.target != edge_next.source:
                return False
        return True

    def __str__(self):
        s = "Path : origin : {} , destination : {}, length {} \n".format(
            self.origin, self.destination, self.length)
        for edge in self.roads:
            s += " source : {}, target : {} ".format(edge.source, edge.target)
        s += '\n'
        return s


class Zone(Node):
    def __init__(self, node_id, label=''):
        super().__init__(node_id, label=label)


class Road(Edge):
    def __init__(self, edge_id, source, target, label=''):
        super().__init__(source, target, edge_id=edge_id, label=label)
        self.length = 0
        self.capacity = 0
        self.free_flow_travel_time = 0
        self.vehicles = 0
        self.toll = 0.0

    def init_length(self, length):
        self.length = length
        self.capacity = self.length * 50
        self.free_flow_travel_time = self.length * 0.5

    def set_toll(self, toll):
        if toll < 0:
            logging.debug(" illegal toll number {}".format(toll))
            return False
        self.toll = toll
        return True
 
    def set_vechiceles(self, vehicles):
        if vehicles > self.capacity or vehicles < 0:
            logging.debug("vechicles is out of capacity {}".format(self.capacity) + 
                " coming vechicles {}".format(vehicles))
            return False
        self.vehicles = int(vehicles)
        return True

    def __str__(self):
        s = "Road : id {}, source {} , target {}, vechicles {}".format(
            self.id, self.source, self.target, self.vehicles)
        s += "length {}, capacity {}, free_flow_travel_time {}, toll {}, label {} \n".format(
            self.length, self.capacity, self.free_flow_travel_time, self.toll, self.label)
        return s



