from agent.default_agent import DefaultAgent
from env.dynamic_etc import DynamicETC
from policy.de_mcts import DeMCTS,TreeNode
import random
import math
import numpy as np
import time
import logging

SAMPLE_NUM = 10

class DeMctsAgent():
    def __init__(self, road_source, road_target, action_range, max_time_step, template_env : DynamicETC):
        self.agent_id = {'source' : road_source, 'target' : road_target}
        self.action_range = action_range
        self.max_time_step = max_time_step
        self.simulator = template_env.clone()
        self.mcts_policy = DeMCTS(action_range, max_time_step)
        self.action_seq_wrapper_list = None
        self.root = TreeNode(-1,0)
        self.beta = 1
    
    def act(self, obs):
        # 返回 action seqs 中概率最高的 seq 就可以了。
        pass
    
    def init_tree(self):
        self.mcts_policy.traverse_grow_tree(self.root, 360)
        
    def get_best_action_seq(self):
        max_prob = 0.0
        best_action = None
        for action in self.action_seq_wrapper_list:
            if action.get_action_prob() > max_prob:
                max_prob = action.get_action_prob()
                best_action = action
        return best_action

    def get_id(self):
        return self.agent_id
    
    def select_set_of_seq(self):
        # action_seq_wrapper_list = self.mcts_policy.sample_act_seqs(self.root)
        action_seq_list = []
        for action in self.action_range:
            action_seq_list.append(
                [action for _ in range(self.max_time_step)])
        prob = 1.0 / len(action_seq_list)
        new_action_seqs_wrapper_list = []
        for action_seqs in action_seq_list:
            new_action_seqs_wrapper_list.append(
                ActionSeqWrapper(self.agent_id, action_seqs, prob))
        self.action_seq_wrapper_list = new_action_seqs_wrapper_list
        return self.action_seq_wrapper_list

    def optimize_policy(self, all_action_seq_wrapper_list, other_action_seq_wrapper_list):
        # self.root = self.mcts_policy.grow_tree(self.root, self.simulator, whole_action_seqs_list, self.agent_id)
        self.update_act_seq_prob(
            self.action_seq_wrapper_list, all_action_seq_wrapper_list, 
            other_action_seq_wrapper_list, self.beta)
        self.beta = self.cool_beta(self.beta)

    def update_act_seq_prob(self, own_action_seq_wrapper_list, all_action_seq_wrapper_list, 
                                other_action_seq_wrapper_list, beta):
        alpha = 0.01
        for own_action_seqs_wrapper in own_action_seq_wrapper_list:
            joint_action_seq_wrapper_list = self.generate_joint_action(
                all_action_seq_wrapper_list)
            excepted_val = self.get_excepted_val(joint_action_seq_wrapper_list)
            con_joint_action_seq_wrapper_list = self.generate_joint_action(
                other_action_seq_wrapper_list, own_action_seqs_wrapper)
            con_excepted_val = self.get_con_excepted_val(
                con_joint_action_seq_wrapper_list, self.agent_id)

            actions_seqs_prob_entropy = self.cal_entropy(own_action_seq_wrapper_list)

            old_prob = own_action_seqs_wrapper.get_action_prob()
            prob = old_prob - alpha * old_prob * ((excepted_val - con_excepted_val) 
                    / self.beta + actions_seqs_prob_entropy + math.log(old_prob))
            own_action_seqs_wrapper.set_action_prob(prob)

            self.normalise(own_action_seq_wrapper_list)

    def get_excepted_val(self, joint_action_seq_wrapper_list):
        # joint action 其实 joint 的是 seq。这个 joint action 其实是个矩阵。
        # 行的坐标是时间步， 列的坐标是 agent。
        episode_joint_action_list = []
        episode_joint_action_prob = []
        for joint_action_seq_wrapper in joint_action_seq_wrapper_list:
            cal_reward = 0.0
            probability = 1.0
            episode_joint_action = [[] for _ in range(self.max_time_step)]
            for action_seq_wrapper in joint_action_seq_wrapper:
                for i in range(len(action_seq_wrapper.get_action_seq())):
                    episode_joint_action[i].append({
                        'source': action_seq_wrapper.get_id()['source'],
                        'target': action_seq_wrapper.get_id()['target'],
                        'toll': action_seq_wrapper.get_action(i)
                    })
                probability *= action_seq_wrapper.get_action_prob()
            episode_joint_action_list.append(episode_joint_action)
            episode_joint_action_prob.append(probability)
        
        excepeted_val = self.cal_excepted_val_by_times(episode_joint_action_list,
                            episode_joint_action_prob)

        return excepeted_val
    
    def get_con_excepted_val(self, joint_action_seq_wrapper_list, agent_id):
        excepeted_val = 0.0
        # joint action 其实 joint 的是 seq。这个 joint action 其实是个矩阵。
        # 行的坐标是时间步， 列的坐标是 agent。
        episode_joint_action_list = []
        episode_joint_action_prob = []
        for joint_action_seq_wrapper in joint_action_seq_wrapper_list:
            cal_reward = 0.0
            probability = 1.0
            episode_joint_action = [[] for _ in range(self.max_time_step)]
            for action_seq_wrapper in joint_action_seq_wrapper:
                for i in range(len(action_seq_wrapper.get_action_seq())):
                    episode_joint_action[i].append({
                        'source': action_seq_wrapper.get_id()['source'],
                        'target': action_seq_wrapper.get_id()['target'],
                        'toll': action_seq_wrapper.get_action(i)
                    })
                if action_seq_wrapper.get_id()['source'] != agent_id['source'] and action_seq_wrapper.get_id()['target'] != agent_id['target']:
                    probability *= action_seq_wrapper.get_action_prob()
            episode_joint_action_list.append(episode_joint_action)
            episode_joint_action_prob.append(probability)
        excepeted_val = self.cal_excepted_val_by_times(
            episode_joint_action_list, episode_joint_action_prob)
        return excepeted_val
        
    def cal_excepted_val_by_sample(self, episode_joint_action_list, episode_joint_action_prob, sample_times):
        excepeted_val = 0.0
        episode_joint_action_sample = np.random.choice(
            [i for i in range(len(episode_joint_action_list))], sample_times, p=episode_joint_action_prob)

        for index in episode_joint_action_sample:
            episode_joint_action = episode_joint_action_list[index]
            cal_reward = self.mcts_policy.cal_local_reward(
                episode_joint_action, self.agent_id, self.simulator)
            excepeted_val += cal_reward
        excepeted_val /= sample_times
        return excepeted_val
    
    def cal_excepted_val_by_times(self, episode_joint_action_list, episode_joint_action_prob):
        excepeted_val = 0.0
        for index in range(len(episode_joint_action_list)):
            episode_joint_action = episode_joint_action_list[index]
            reward = self.mcts_policy.cal_local_reward(
                episode_joint_action, self.agent_id, self.simulator)
            excepeted_val = reward * episode_joint_action_prob[index]
        return excepeted_val

    def generate_joint_action(self, action_seq_wrapper_list, own_action_seq_wrapper = None):
        joint_action_seq_wrapper_list = []
        if own_action_seq_wrapper == None:
            self.recur_generate_joint_action(
                action_seq_wrapper_list, 0, [], joint_action_seq_wrapper_list)
        else:
            self.recur_generate_joint_action(action_seq_wrapper_list, 0, [
                                            own_action_seq_wrapper], joint_action_seq_wrapper_list)
        return joint_action_seq_wrapper_list

    def recur_generate_joint_action(self, all_action_seqs_wrapper_list, index, joint_action: list, joint_action_set):
        if index == len(all_action_seqs_wrapper_list):
            joint_action_set.append(joint_action.copy())
            return
        action_seq_wrapper_list = all_action_seqs_wrapper_list[index]
        for action_seqs_wrapper in action_seq_wrapper_list:
            joint_action.append(action_seqs_wrapper)
            self.recur_generate_joint_action(
                all_action_seqs_wrapper_list, index+1, joint_action, joint_action_set)
            joint_action.pop()


    def cal_local_reward(self, joint_action, agent_id):
        local_sim = self.simulator.clone()
        state,terminal,reward,info = local_sim.step(joint_action)
        local_sim =  self.simulator.clone()
        for action in joint_action:
            if action['source'] == agent_id['source'] and action['target'] == agent_id['target']:
                action['toll'] = 0.0
                break
        isolated_reward = local_sim.step(joint_action)
        return reward - isolated_reward



    def cal_entropy(self, action_seq_wrapper_list):
        entropy = 0.0
        for action in action_seq_wrapper_list:
            prob = action.get_action_prob()
            entropy += prob * math.log(prob)
        return entropy

    def cool_beta(self, beta):
        return beta * 0.95

    def normalise(self, own_action_seqs):
        max_prob = -1000000
        min_prob = 10000000
        for action_seq in own_action_seqs:
            max_prob = max(max_prob, action_seq.get_action_prob())
            min_prob = min(min_prob, action_seq.get_action_prob())
        for action_seq in own_action_seqs:
            action_seq.set_action_prob(action_seq.get_action_prob() - min_prob + 0.1)
        prob_sum = 0.0
        for action_seq in own_action_seqs:
            prob_sum += action_seq.get_action_prob()
        prob_factor = 1 / prob_sum
        for action_seq in own_action_seqs:
            action_seq.set_action_prob(action_seq.get_action_prob() * prob_factor)
        return own_action_seqs


class ActionSeqWrapper():
    def __init__(self, agent_id, action_seq, atcion_prob):
        # {'source': source, 'target' : target}
        self.agent_id = agent_id
        self.action_seq = action_seq
        self.action_prob = atcion_prob

    def get_action(self, time):
        return self.action_seq[time]

    def get_action_seq(self):
        return self.action_seq

    def get_action_prob(self):
        return self.action_prob
    
    def set_action_prob(self, prob):
        self.action_prob = prob
    
    def get_id(self):
        return self.agent_id
