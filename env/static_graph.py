import logging
logging.basicConfig(level=10,
                    format='%(filename)s[line:%(lineno)d] %(levelname)s %(message)s')


class StaticGraph():
    """该类是静态图的实现
        静态图的意思是图完成初始化后，点和边的结构就不再改变了（但是值可以变）
    """

    def __init__(self):
        """初始化图

        Arguments:
            node_dict_list {list} -- 是一个 node 的列表。每个元素包含两个属性，id 和 label，其实 id 是必须的
            edge_dict_list {[list]} -- 是一个 list 的列表。每个元素包含四个属性，id，source，target，label。其中 source 和 target 是必须的。
        """
        self.nodes_cnt = 0
        self.edges_cnt = 0
        self.nodes_list = []
        self.nodes_adjacency_list = []
        self.edges_list = []
        self.edges_martix = []

    def _init_graph(self, node_dict_list, edge_dict_list):
        # temp_node_key_id_map 用来将原本的 node id 映射到新的 node id 上
        # 新的 node id 就是根据 node 在数组里的长度设置
        temp_node_key_id_map = {}
        self.nodes_adjacency_list = []
        for node_dict in node_dict_list:
            node_id = len(self.nodes_adjacency_list)
            node_label = node_dict.get('label', "")
            node = Node(node_id, node_label)
            temp_node_key_id_map[node_dict['id']] = node.node_id
            self.nodes_list.append(node)
            self.nodes_adjacency_list.append(node)
        self.nodes_cnt = len(self.nodes_list)

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
            source = temp_node_key_id_map[edge_dict['source']]
            target = temp_node_key_id_map[edge_dict['target']]
            if self.is_legal_edge(source, target):
                edge = Edge(edge_id=len(self.edges_list),
                            source=source, target=target)
                self.edges_list.append(edge)
                self.edges_martix[edge.source][edge.target] = edge
                # 将边的信息也存进邻接矩阵里
                self._add_edge_to_adjacency_list(source, target)
        self.edges_cnt = len(self.edges_list)

    def _add_edge_to_adjacency_list(self, source, target):
        if (source == target or 
            self.is_legal_node(source) == False or 
            self.is_legal_node(target) == False):
            return False
        source_node = self.nodes_adjacency_list[source]
        end_node = self.nodes_adjacency_list[target]
        node = Node(end_node.node_id, end_node.label)
        # insert into list head
        node.next = source_node.next
        source_node.next = node
        return True

    def get_node_by_id(self, node_id):
        if self.is_legal_node(node_id):
            return self.nodes_adjacency_list[node_id]
        else:
            return None

    def get_edge(self, source, target):
        if self.is_legal_edge(source , target):
            return self.edges_martix[source][target]
        else:
            return  None

    def get_edge_by_id(self, edge_id):
        if edge_id >= 0 and edge_id < self.edges_cnt:
            return self.edges_list[edge_id]
        else:
            return None

    def get_all_edges(self):
        return self.edges_list

    def get_all_nodes(self):
        return self.nodes_list

    def get_node_related_edges(self, node_id):
        return self.get_edges_source_is_node(node_id) + self.get_edges_target_is_node(node_id)

    def get_edges_target_is_node(self, target_node_id):
        if self.is_legal_node(target_node_id):
            edges = []
            for row in self.edges_martix:
                edge = row[target_node_id]
                if edge != None:
                    edges.append(edge)
            return edges
        else:
            return None

    def get_edges_source_is_node(self, source_node_id):
        if self.is_legal_node(source_node_id):
            edges = []
            for edge in self.edges_martix[source_node_id]:
                if edge != None:
                    edges.append(edge)
            return edges
        else:
            return None

    def get_nodes_cnt(self):
        return self.nodes_cnt

    def get_edges_cnt(self):
        return self.edges_cnt

    def is_legal_edge(self, source, target):
        if (source == target or self.is_legal_node(source) == False 
                or self.is_legal_node(target) == False ):
            logging.debug("invalid source {} or target {} index".format(source, target))
            return False
        
        edge = self.edges_martix[source][target]
        if edge == None:
            logging.debug("road is not exists, source {}  target {} ".format(source, target))
            return False
        return True

    def is_legal_node(self, node_id):
        if node_id < 0 or node_id >= self.nodes_cnt:
            return False
        else:
            return True


class Node():
    def __init__(self, node_id, label=""):
        self.node_id = node_id
        self.next = None
        self.label = label


class Edge():
    def __init__(self, source, target, edge_id=-1, label=""):
        self.source = source
        self.target = target
        self.edge_id = edge_id
        self.lable = label
