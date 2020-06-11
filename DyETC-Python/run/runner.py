from env.dynamic_etc import DynamicETC
from agent.default_agent import DefaultAgent
from env.traffic_graph import TrafficGraph
from env.dyetc_state import DyETCState
from agent.de_mcts_agent import DeMctsAgent
from agent.random_agent import RandomAgent
import constant.const as const
import yaml
import json
import random
import logging
import time
logging.basicConfig(level=logging.INFO,
         format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s') 
GRAPH_CONFIG_PATH = "/Users/zhanghaopeng/CodeHub/2020Spring/DyETC/DyETC-Python/env/config/"

class Runner():
    def __init__(self):
        super().__init__()

    def process_state_to_obs(self, state, road_source, road_target):
        return []

    def train(self, iteration : int, tau : int, agents):
        all_action_seqs_wrapper_list = []
        
        for i in range(len(agents)):
            all_action_seqs_wrapper_list.append(agents[i].select_set_of_seq())
        other_actions_seq_wrapper = []
        for i in range(len(agents)):
            other_actions_seq_wrapper.append(
                all_action_seqs_wrapper_list[:i] + all_action_seqs_wrapper_list[i+1:])

        for it in range(iteration):
            start = time.clock()
            for i in range(len(agents)):
                agents[i].optimize_policy(
                    all_action_seqs_wrapper_list, other_actions_seq_wrapper[i])
            end = time.clock()
            #logging.debug('iteration {} finish in {} s'.format(it, end-start))

    def test(self, iteration, agents, template_env: DynamicETC):
        env = template_env.clone()
        total_average_reward = 0.0
        for i in iteration:
            state = env.reset()
            action_seqs = []
            for agent in agents:
                action_seqs.append(agent.get_best_action_seq())
            cumulative_reward = 0
            for step in range(const.MAX_TIME_STEP):
                actions = []
                for action_seq in action_seqs:
                    actions.append({
                        'source': action_seq.get_id()['source'],
                        'target': action_seq.get_id()['target'],
                        'toll': action_seq.get_action(step)
                    })
                state, reward, terminal, info = env.step(actions)
                cumulative_reward += reward
            average_reward = cumulative_reward / const.MAX_TIME_STEP
            logging.info(
                "average cumulative reward is {}".format(average_reward))
            total_average_reward = total_average_reward * (i / (i+1)) + average_reward / (i+1)

        logging.info(
            "total average reward is {}".format(total_average_reward))
        return env
    
    def random_test(self, iteration, graph_data, template_env: DynamicETC):
        agents = []
        for road in graph_data['edges']:
            agent = RandomAgent(
                road['source'], road['target'], const.ACTION_SPACE, const.MAX_TIME_STEP)
            agents.append(agent)
        env = template_env.clone()
        total_average_reward = 0.0
        for i in range(iteration):
            
            state = env.reset()
            action_seqs = []
            for agent in agents:
                action_seqs.append(agent.act())
            cumulative_reward = 0
            for step in range(const.MAX_TIME_STEP):
                actions = []
                for action_seq in action_seqs:
                    actions.append({
                        'source': action_seq.get_id()['source'],
                        'target': action_seq.get_id()['target'],
                        'toll': action_seq.get_action(step)
                    })
                state, reward, terminal, info = env.step(actions)
                cumulative_reward += reward

            average_reward = cumulative_reward / const.MAX_TIME_STEP
            logging.info(
                "average cumulative reward is {}".format(average_reward))
            total_average_reward = total_average_reward * (i / (i+1)) + average_reward / (i+1)

        logging.info(
            "total average reward is {}".format(total_average_reward))
            

    def run(self, filename, init_state_from_file=False):
        graph_data = self.read_graph_data(filename)
        state_data = None
        if init_state_from_file:
            state_data = self.read_init_state_from_file(filename)
        dyenv = DynamicETC(graph_data, state_data)
        agents = self.init_agents(graph_data, dyenv)
        state = dyenv.reset()
        if init_state_from_file == False:
            self.write_init_state_to_file(state, filename)

        for i in range(const.EPISODE):
            # self.train(const.TRAIN_ITERATION, const.TAU, agents)
            # self.test(agents, dyenv)
            self.random_test(50, graph_data, dyenv)
        # 做一轮测试并保存本轮的迭代结果
        #self.write_history_to_json(self.test(agents, dyenv))

    def init_agents(self, graph_data, env):
        agents = []
        for road in graph_data['edges']:
            agent = DeMctsAgent(
                road['source'], road['target'], const.ACTION_SPACE, const.MAX_TIME_STEP, env)
            agents.append(agent)
        return agents
        
    def read_graph_data(self, filename):
        """ 初始化的图只有边和节点的信息，具体的 车辆等信息 在 dyetc env 在完成初始化 
        """
        data = self.get_yaml_data(GRAPH_CONFIG_PATH + filename + '.yml')
        nodes_data = []
        for node in  data['nodes']:
            nodes_data.append({
                'node_id': node['id'],
                'label': node['id'],
            })
        roads = data['edges']
        return {'nodes': nodes_data, 'edges': roads}

    def generate_graph(self, node_cnt):
        """ this method focus structue of graph, dose't concern about value of road or node 
        """
        nodes = []
        for i in range(node_cnt):
            nodes.append({"id": i})
        edges = []
        for i in range(node_cnt):
            for j in range(node_cnt):
                if i == j:
                    continue
                r = random.randint(0, 1)
                if r == 1:
                    edges.append({"source": i, "target": j})
        data = {
            "nodes": nodes,
            "edges": edges,
        }
        filename = "graph-" + str(node_cnt) + ".yml"
        with open(GRAPH_CONFIG_PATH+filename + '.yml', "w", encoding="utf-8") as f:
            yaml.dump(data, f)

    def get_yaml_data(self, yaml_file):
        file = open(yaml_file, 'r', encoding="utf-8")
        file_data = file.read()
        file.close()
        data = yaml.load(file_data, Loader=yaml.Loader)
        return data

    def write_history_to_json(self, dyenv: DynamicETC):
        env_data = dyenv.data()
        trajectory = []
        for state_dict in env_data['trajectory']:
            roads_data = []
            for road_dict in state_dict['state']['roads']:
                roads_data.append({
                    'id': road_dict['edge_id'],
                    'source': road_dict['source'],
                    'target': road_dict['target'],
                    'capacity': road_dict['capacity'],
                    'label': road_dict['label'],
                    'length': road_dict['length'],
                    'freeFlowTravelTime': road_dict['free_flow_travel_time'],
                    'toll': road_dict['toll'],
                    'vehicles': road_dict['vehicles']
                })
            zones_data = []
            for zone_dict in state_dict['graph']['nodes']:
                zones_data.append({
                    'id': zone_dict['node_id'],
                    'label': zone_dict['label']
                })
            
            odp_data = []
            for odp_dict in state_dict['state']['origin_dest_pairs']:
                contained_roads_data = []
                for road_dict in odp_dict['contained_roads']:
                    contained_roads_data.append({
                        'source': road_dict['source'],
                        'target': road_dict['target'],
                    })
                odp_data.append({
                    'origin': odp_dict['origin'],
                    'destination': odp_dict['destination'],
                    'demand': odp_dict['demand'],
                    'containedRoads': contained_roads_data
                })
            trajectory.append({
                'zones': zones_data,
                'roads': roads_data,
                'trafficState': state_dict['state']['traffic_state'],
                'originDestPairs': odp_data
            })
        written_data = {'trajectory': trajectory}
        with open('./ui/public/data.json', 'w') as f:
            json.dump(written_data, f, sort_keys=True,
                      indent=4, separators=(',', ': '))

    def write_init_state_to_file(self, env: DynamicETC, filename):
        pass

    def read_init_state_from_file(self, filename):
        with open(GRAPH_CONFIG_PATH + filename + '-init_state.data', 'r') as f:
            data = json.loads(f.read())
            state = data['state']
            return state
