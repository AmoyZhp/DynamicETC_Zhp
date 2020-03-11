"""The node of graph
    id : is the key value of node in dict
    next_node : (node, next_node) is the road between two node
    val : if the node is the origin node (the node is in the begin of linked list), the val
            reprensent the val of node
        if it represnets the road between two node, the val is the road val.
"""
class Node():
    def __init__(self):
        self.id = -1
        self.next_node = None
        self.val = 0

class Graph():
    """Graph strcture, adjacency list are used to represent graph
    """    
    def __init__(self):
        self.adjacency_list = {}
        self.id = 0
    """assign id to a node, the id represent the key value in dict

    """    
    def assign_id(self, node):
        node.id = self.id
        self.id += 1

    def add_node(self, info):
        node = Node()
        self.assign_id(node)
        self.adjacency_list[node.id] = node

    def get_nodes_cnt(self):
        pass

    def get_roads_cnt(self):
        pass
    
    """
        val is the road weight
    """    
    def add_road(self, begin, end, val):
        begin_node = self.adjacency_list.get(begin)
        end_node = self.adjacency_list.get(end)
        if( begin_node != None and end_node != None):
            while(begin_node.next_node != None):
                begin_node = begin_node.next_node
            node = Node()
            node.id = end_node.id
            node.val = val
            begin_node.next_node = node


    def get_node_related_roads(self, node_id):
        pass

    def get_road_related_nodes(self,begin, end):
        pass

