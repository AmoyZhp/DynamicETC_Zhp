"""The node of graph
    id : is the key value of node in dict
    next_node : (node, next_node) is the road between two node
    val : if the node is the origin node (the node is in the begin of linked list), the val
            reprensent the val of node
        if it represnets the road between two node, the val is the road val.
"""
class Node():
    def __init__(self, val = -1):
        self.id = -1
        self.next = None
        self.val = val

class Road():
    def __init__(self, begin = -1, end = -1, vechicels = -1, capacity = -1):
        self.id = -1
        self.begin = begin
        self.end = end
        self.vechicels = vechicels
        self.capacity = capacity

class Graph():
    """Graph strcture, adjacency list are used to represent graph
        its a static graph.It means that once finish created this graph
        you should not edit this graph.
    """    
    def __init__(self, node_num):
        self.adjacency_list = []
        self.road_martix = [[]]
        for i in range(node_num):
            self.adjacency_list.append(Node())
            row = []
            for i in range(node_num):
                row.append(Road())
            self.road_martix.append(row)
        self.node_id = 0
        self.road_id = 0
    """assign id to a node, the id represent the key value in dict

    """    
    def assign_node_id(self, node):
        if self.node_id >= len(self.adjacency_list):
            print(" node number is out of capatiry")
        node.id = self.node_id
        self.node_id += 1

    def assign_road_id(self,road):
        road.id = self.road_id
        self.road_id += 1

    def update_road(self, begin, end, vechicels):
        if begin < 0 or begin > len(self.adjacency_list) \
            or end < 0 or end > len(self.adjacency_list):
            print("invalid origin {} or destination {} index", begin, end)
        else:
            road = self.road_martix[begin][end]
            if road.id != -1:
                road.vechicels = vechicels
            else:
                print("invalid road")

    def update_node(self,i, val):
        if i >= 0 and i < len(self.adjacency_list):
            self.adjacency_list[i].val = val
        else:
            print("illegal node index" + i)

    def add_node(self, val):
        node = Node(val)
        self.assign_node_id(node)
        self.adjacency_list[node.id] = node

    def get_nodes_cnt(self):
        self.node_id

    def get_roads_cnt(self):
        self.road_id
     
    def add_road(self, begin, end, val):
        begin_node = self.adjacency_list[begin]
        end_node = self.adjacency_list[end]
        if( begin_node != None and end_node != None):
            node = Node()
            node.id = end_node.id
            node.val = end_node.val
            # insert into list head
            node.next = begin_node.next
            begin_node.next = node
            self.road_martix[begin][end] = Road(begin, end, val)
            self.assign_road_id(self.road_martix[begin][end])
            self.road_martix[end][begin] = Road(end, begin, val)
            self.assign_road_id(self.road_martix[end][begin])
        else:
            print(" graph road is illegal")

    def get_node_related_roads(self, node_id):
        roads = []
        for road in self.road_martix[node_id]
            if (road.begin == node_id or road.end == node_id) and (
                    road.id != -1):
                roads.append(road)
        for row in self.road_martix:
            rowd = row[node_id]
            if (road.begin == node_id or road.end == node_id) and (
                    road.id != -1):
                roads.append(road)
        return roads


    def get_road_by_id(self, id):
        for row in self.road_martix:
            for road in row:
                if road.id == id:
                    return road

    def ger_road(self,origin, destination):
        road = self.road_martix[origin][destination]
        if road.id != -1:
            return road
        else:
            print("in graph : road is not exisit")
            return None

    def get_all_roads(self):
        roads = []
        for row in self.road_martix:
            for road in row:
                if road.id != -1:
                    roads.append(road)
        return roads

    def get_paths_between_two_zone(self,origin, destination):
        pass