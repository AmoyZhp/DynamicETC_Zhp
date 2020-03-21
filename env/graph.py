
import logging
logging.basicConfig(level=10,
         format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')      
class Node():
    """The node of graph
    id : is the key value of node in dict
    next_node : (node, next_node) is the road between two node
    """
    def __init__(self, id, label = ""):
        self.id = id
        self.next = None
        self.label = label
    
    def get_copy(self):
        return Node(self.id, self.label)
        

class Road():
    def __init__(self,id, begin, end, length,
                vechicels = 0, toll = 0.0, label = ""):
        self.id = id
        self.begin = begin
        self.end = end
        self.length = length
        self.capacity = self.length * 50
        self.free_flow_travel_time = self.length * 0.5
        self.vechicels = vechicels
        self.toll = toll
        self.label = label
    
    def road_legality_self_check(self):
        if self.capacity != self.length * 50:
            return False
        if self.free_flow_travel_time != self.length * 0.5:
            return False
        if self.toll < 0:
            return False
        return True

    def set_toll(self, toll):
        if toll < 0:
            logging.debug(" illegal toll number %d" %(toll))
        self.toll = toll
 
    def set_vechiceles(self, vechicels):
        if vechicels > self.capacity or vechicels < 0:
            logging.debug("vechicles is out of capacity now vechicles {}".format(self.vechicels) + 
                "and new vechicles {}".format(vechicels))
            return False
        else:
            self.vechicels = vechicels
            return True
    
    def __str__(self):
        s = "Road : id {}, begin {} , end {}, vechicles {}".format(
            self.id, self.begin, self.end, self.vechicels)
        s += "length {}, capacity {}, free_flow_travel_time {}, toll {}, label {} \n".format(
            self.length, self.capacity, self.free_flow_travel_time, self.toll, self.label)
        return s

class Path():
    def __init__(self, roads):
        self.roads = []
        self.origin = -1
        self.destination = -1
        self.length = 0
        for road in roads:
            self.add_road(road)
            
    def path_legality_self_check(self):
        if len(self.roads) == 0:
            return True

        if self.roads[0].begin != self.origin or self.roads[-1].end != self.destination:
            return False

        for i in range(len(self.roads)-1):
            road1 = self.roads[i]
            road2 = self.roads[i+1]
            if road1.end != road2.begin:
                return False
        return True

    def add_road(self, road):
        if len(self.roads) == 0:
            self.roads.append(road)
            self.origin = road.begin
            self.destination = road.end
        else:
            if self.roads[-1].end == road.begin:
                self.roads.append(road)
                self.destination = road.end
            else:
                logging.debug(" added road begin point don't equal to last road end point")
        self.length = len(self.roads)
        if not self.path_legality_self_check():
            logging.debug("illegal path")
            logging.debug(self.__str__)
    
    def is_road_in_path(self, road):
        for r in self.roads:
            if r.id == road.id:
                return True
        return False
    
    def __str__(self):
        s = "Path : origin : {} , destination : {}, length {} \n".format(
            self.origin, self.destination, self.length)
        for road in self.roads:
            s += " begin : {}, end : {} ".format(road.begin, road.end)
        s += '\n'
        return s

class Graph():
    """Graph strcture, adjacency list are used to represent graph
        its a static graph.It means that once finish created this graph
        you should not edit this graph.
    """    
    def __init__(self, node_dict_list, road_dict_list):
        self.adjacency_list = []
        self.road_martix = []

        temp_node_key_id_map = {}
        for node_dict in node_dict_list:
            node_id = len(self.adjacency_list)
            node_label = node_dict.get('label',"")
            node = Node(node_id, node_label)
            temp_node_key_id_map[node_dict['id']] = node.id
            self.adjacency_list.append(node)

        self.node_cnt = len(self.adjacency_list)

        # init road matrix
        for _ in range(len(node_dict_list)):
            row = []
            for _ in range(len(node_dict_list)):
                row.append(None)
            self.road_martix.append(row)

        self.road_cnt = 0
        for road_dict in road_dict_list:
            begin = temp_node_key_id_map[road_dict['begin']]
            end = temp_node_key_id_map[road_dict['end']]
            road = Road(id = self.road_cnt, begin=begin, end=end, 
                    length=road_dict['length'], vechicels=road_dict.get('vechicels', 0),
                    toll=road_dict.get('toll', 0.0), label=road_dict.get('label', ""))
            if (road.begin < 0 or road.begin >= self.node_cnt
                    or road.end < 0 or road.end >= self.node_cnt):
                logging.debug("illegal road in init graph")
            self.road_martix[road.begin][road.end] = road
            self.add_road_to_adjacency_list(begin, end)
            self.road_cnt += 1
        
    def set_vechicels_in_road(self, begin, end, vechicels):
        if self.legal_road(begin, end):
            self.road_martix[begin][end].set_vechiceles(vechicels)
    
    def set_toll_in_road(self, begin, end, toll):
       if self.legal_road(begin, end):
           self.road_martix[begin][end].set_toll(toll)

    def get_node_related_out_roads(self, node_id):
        """get road whose origin is node_id
        
        Arguments:
            node_id {int} -- node
        
        Returns:
            [List] -- [related road list]
        """        
        roads = []
        for road in self.road_martix[node_id]:
            if road != None and road.begin == node_id:
                roads.append(road)
        return roads
    
    def get_node_related_in_roads(self, node_id):
        """get road whose destination is node_id
        
        Arguments:
            node_id {int} -- node
        
        Returns:
            [List] -- [related road list]
        """    
        roads = []
        for row in self.road_martix:
            road = row[node_id]
            if road != None and road.end == node_id:
                roads.append(road)
        return roads


    def get_road_by_id(self, road_id):
        for row in self.road_martix:
            for road in row:
                if  road != None and road.id == road_id:
                    return road

    def get_road(self, begin, end):
        road = self.road_martix[begin][end]
        if road != None:
            return road
        else:
            print("in graph : road is not exisit")
            return None

    def get_all_roads(self):
        roads = []
        for row in self.road_martix:
            for road in row:
                if road != None:
                    roads.append(road)
        return roads

    def get_paths_between_two_zone(self,origin, destination):
        """ implemented by dfs to find path
        
        """
        if not self.legal_node(origin) or not self.legal_node(destination):
            print("illegal input of get_paths_between_two_zone")
            return None
        paths = []
        if origin == destination:
            return paths
        stack = []
        vis =  [[ False for _ in range(len(self.adjacency_list))] for _ in range(len(self.adjacency_list)) ]
        origin_node = self.adjacency_list[origin]
        stack.append(origin_node)
        # DFS
        while len(stack) > 0:
            node = stack[-1]
            if node.id == destination:
                roads = []
                for i in range(len(stack)-1):
                    road = self.get_road(stack[i].id, stack[i+1].id)
                    roads.append(road)
                paths.append(Path(roads))
                stack.pop()
                continue
            neighbor = node.next
            while neighbor != None:
                if not vis[node.id][neighbor.id]: 
                    stack.append(self.adjacency_list[neighbor.id])
                    vis[node.id][neighbor.id] = True
                    break
                neighbor = neighbor.next
            if neighbor == None :
                stack.pop()
        return paths
    
    def add_road_to_adjacency_list(self, begin, end):
        if begin == end:
            print(" begin and end should not be the same")
            return False
        begin_node = self.adjacency_list[begin]
        end_node = self.adjacency_list[end]
        if begin_node != None and end_node != None:
            node = Node(end_node.id, end_node.label)
            # insert into list head
            node.next = begin_node.next
            begin_node.next = node
            return True
        else:
            print(" graph road is illegal in add road")
            return False
    
    def legal_road(self,begin, end):
        if (begin == end or begin < 0 or begin >= self.node_cnt 
                or end < 0 or end >= self.node_cnt):
            logging.debug("invalid origin {} or destination {} index", begin, end)
            return False
        
        road = self.road_martix[begin][end]
        if road == None:
            logging.debug("road is not exists origin {}  destination {} ", begin, end)
            return False
        return True

    def legal_node(self,node_id):
        if node_id < 0 or node_id >= self.node_cnt:
            return False
        return True

    def get_nodes_cnt(self):
        return self.node_cnt

    def get_roads_cnt(self):
        return self.road_cnt

if __name__ == "__main__":
    graph = Graph(7)
    for _ in range(7):
        graph.add_node(1)
    graph.add_road(0,1,1)
    graph.add_road(0,2,1)
    graph.add_road(1,3,1)
    graph.add_road(1,5,1)
    graph.add_road(0,6,1)
    graph.add_road(2,4,1)
    graph.add_road(2,6,1)
    graph.add_road(3,5,1)
    graph.add_road(4,6,1)
    graph.add_road(6,5,1)
    adjacency_list = graph.adjacency_list
    for i in range(len(adjacency_list)):
        node = adjacency_list[i]
        print("root : %s" % (node.id) , end=" ")
        neighbor = node.next
        while neighbor != None:
            print(neighbor.id, end=" ")
            neighbor = neighbor.next
        print()
    
    print("node cnt %d" % (graph.get_nodes_cnt()))
    print("road cnt %d " % (graph.get_roads_cnt()))

    print("test get road  and update road")
    road = graph.get_road_by_id(0)
    print("road val %d" % (road.vechicels))
    road = graph.get_road(0,1)
    print("road val %d" % (road.vechicels))
    graph.update_road(road.begin, road.end, 20)
    print("road val %d" % (road.vechicels))
    road = graph.get_road(0,4)
    print(road)
    print()

    print(" test get_node_related_out_roads")
    roads = graph.get_node_related_out_roads(0)
    for road in roads:
        print("(begin : %d, end : %d)" % (road.begin, road.end) , end =" ")
    
    print(" test get_node_related_in_roads")
    roads = graph.get_node_related_in_roads(5)
    for road in roads:
        print("(begin : %d, end : %d)" % (road.begin, road.end) , end =" ")
    print()

    print(" test find path ")
    paths = graph.get_paths_between_two_zone(0,5)
    for path in paths:
        for road in path.roads:
            print("%d -> " % (road.begin), end="")
        print("%d" % (path.roads[-1].end), end="")
        print()
    # adjacency_list = graph.adjacency_list
