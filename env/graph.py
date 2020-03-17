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

class Path():
    def __init__(self, origin, destination):
        self.roads = []
        self.origin = origin
        self.destination = destination
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

class Graph():
    """Graph strcture, adjacency list are used to represent graph
        its a static graph.It means that once finish created this graph
        you should not edit this graph.
    """    
    def __init__(self, node_num):
        self.adjacency_list = []
        self.road_martix = []
        for i_ in range(node_num):
            self.adjacency_list.append(None)
            row = []
            for _ in range(node_num):
                row.append(None)
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

    def add_node(self, val):
        node = Node(val)
        node.next = None
        self.assign_node_id(node)
        self.adjacency_list[node.id] = node

    def get_nodes_cnt(self):
        return self.node_id

    def get_roads_cnt(self):
        return self.road_id
     
    def add_road(self, begin, end, val):
        begin_node = self.adjacency_list[begin]
        end_node = self.adjacency_list[end]
        if begin_node != None and end_node != None:
            node = Node()
            node.id = end_node.id
            node.val = end_node.val
            # insert into list head
            node.next = begin_node.next
            begin_node.next = node
            self.road_martix[begin][end] = Road(begin, end, val)
            self.assign_road_id(self.road_martix[begin][end])
        else:
            print(" graph road is illegal")

    def get_node_related_out_roads(self, node_id):
        roads = []
        for road in self.road_martix[node_id]:
            if road != None and road.begin == node_id:
                roads.append(road)
        return roads
    
    def get_node_related_in_roads(self, node_id):
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

    def get_road(self,origin, destination):
        road = self.road_martix[origin][destination]
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
        if not self.legal_node(origin) or not self.legal_node(destination):
            print("illegal input of get_paths_between_two_zone")
            return None
        paths = []
        stack = []
        vis =  [[ False for _ in range(len(self.adjacency_list))] for _ in range(len(self.adjacency_list)) ]
        origin_node = self.adjacency_list[origin]
        stack.append(origin_node)
        # DFS
        while len(stack) > 0:
            node = stack[-1]
            if node.id == destination:
                path = Path(origin, destination)
                for i in range(len(stack)-1):
                    road = self.get_road(stack[i].id, stack[i+1].id)
                    path.add_road(road)
                paths.append(path)
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

    def legal_road(self,origin, destination):
        if origin == destination:
            return False

        if origin < 0 or origin >= self.node_id \
            or destination < 0 or destination >= self.node_id:
            return False
        
        road = self.road_martix[origin][destination]
        if road == None:
            return False
        
        return True

    def legal_node(self,node_id):
        if node_id < 0 or node_id >= self.node_id:
            return False
        return True



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
