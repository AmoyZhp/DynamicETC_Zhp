import math
import random


class TreeNode():
    def __init__(self, action_path, time_step, parent=None):
        self.action_path = action_path
        self.visit_cnt = 0
        self.cal_reward = 0.0
        self.val = 0.0
        self.parent = parent
        self.children = []
        self.time_step = time_step

    def set_children(self, children):
        self.children = children

    def get_val(self):
        return self.val

    def get_action_path(self):
        return self.action_path

    def get_vist_cnt(self):
        return self.visit_cnt

    def get_time_step(self):
        return self.time_step

    def get_parent(self):
        return self.parent
    
    def get_children(self):
        return self.children

    def get_best_child(self):
        if self.children == None or len(self.children) == 0:
            return None
        best_child = None
        max_val = 0.0
        for child in self.children:
            if child.get_val() > max_val:
                max_val = child.get_val()
                best_child = child
        return child

    def back_propagation(self, reward):
        self.visit_cnt += 1
        self.cal_reward += reward
        if self.parent != None:
            self.parent.back_propagation(reward)
            self.val = (self.cal_reward / self.visit_cnt) + \
                math.sqrt(
                    1.96 * math.log(self.parent.get_vist_cnt() / self.visit_cnt))


class DeMCTS():
    def __init__(self, action_range, max_time_step):
        self.action_range = action_range
        self.max_time_step = max_time_step

    def sample_act_seqs(self, root : TreeNode):
        action_seqs_list = []
        self.recur_sample_act(root, [], action_seqs_list)
        return action_seqs_list

    def recur_sample_act(self, root : TreeNode,
        action_seq : list, action_seqs_list : list):
        action = root.get_action_path()
        if action != -1:
            action_seq.append(action)
        if root.get_children() == None or len(root.get_children()) == 0:
            for i in range(self.max_time_step - len(action_seq)):
                index = random.randint(0, len(self.action_range) - 1)
                action_seq.append(self.action_range[index])
            action_seqs_list.append(action_seq.copy())
        else:
            for child in root.get_children():
                self.recur_sample_act(child, action_seq, action_seqs_list)
        if action != -1:
            action_seq.pop()

    def traverse_grow_tree(self, root, max_time):
        stack = []
        stack.append(root)
        cnt = 0
        while len(stack) > 0 and cnt < max_time:
            node = stack.pop()
            if node.get_children() == None or len(node.get_children()) == 0:
                self.expandsion(node)
            for child in node.get_children():
                stack.append(child)
            cnt += 1
            
    def grow_tree(self, root, simulator, whole_action_seqs_list, agent_id):
        selection_node = self.selection(root)
        expandsion_node = self.expandsion(selection_node)
        # list [ {source, target, action_seq} ]
        other_joint_seq = self.sample_other_actions(whole_action_seqs_list, agent_id)
        action_seq = self.simulation(expandsion_node)
        one_episode_joint_action = self.concat_action(other_joint_seq, {
            'source': agent_id['source'],
            'target': agent_id['target'],
            'action_seq': action_seq,
        })
        local_reward = self.cal_local_reward(
            one_episode_joint_action, agent_id, simulator)
        self.back_propagation(expandsion_node, local_reward)
        return root
    
    def selection(self, root):
        while root.get_best_child() != None:
            root = root.get_best_child()
        return root
    
    def expandsion(self, root : TreeNode):
        if(root.get_time_step() == self.max_time_step):
            return root
        children = []
        for action in self.action_range:
            children.append(TreeNode(action, root.get_time_step() + 1, root))
        root.set_children(children)
        return root.get_best_child()
    
    def simulation(self, expandsion_node : TreeNode):
        action_seq = []
        node = expandsion_node
        while node != None :
            action = node.get_action_path()
            if action != -1:
                action_seq.append(action)
            node = node.get_parent()
        action_seq.reverse()
        for i in range(self.max_time_step - len(action_seq)):
            index = random.randint(0, len(self.action_range) - 1)
            action_seq.append(self.action_range[index])
        return action_seq

    def back_propagation(self, node : TreeNode, reward):
        node.back_propagation(reward)

    def sample_other_actions(self, whole_action_seqs_list, agent_id):
        joint_action = []
        for action_seqs_list in whole_action_seqs_list:
            if (action_seqs_list[0].get_id()['source'] == agent_id['source'] 
                and action_seqs_list[0].get_id()['target'] == agent_id['target']):
                continue
            max_prob = 0.0
            best_action = None
            for action in action_seqs_list:
                if action.get_action_prob() > max_prob:
                    max_prob = action.get_action_prob()
                    best_action = action
            joint_action.append({
                'source': best_action.get_id()['source'],
                'target': best_action.get_id()['target'],
                'action_seq': best_action.get_action_seq(),
            })
        return joint_action

    def cal_local_reward(self, one_episode_joint_action, agent_id, simulator):
        cal_reward = 0.0
        local_sim = simulator.clone()
        isloated_local_sim = simulator.clone()
        for joint_action in one_episode_joint_action:
            
            state, reward, terminal , info = local_sim.step(joint_action)
            local_sim = simulator.clone()
            for action in joint_action:
                if action['source'] == agent_id['source'] and action['target'] == agent_id['target']:
                    action['toll'] = 0.0
                    break
            state, isolated_reward, terminal,  info = isloated_local_sim.step(
                joint_action)
            cal_reward += (reward - isolated_reward)
        return cal_reward

    def concat_action(self, other_joint_seq, own_action_seq):
        join_action_seq = other_joint_seq
        join_action_seq.append(own_action_seq)
        one_episode_joint_action = [[] for _ in range(self.max_time_step) ]
        for action_dict in join_action_seq:
                # action_dict = { source : source , target : target, action_seq : []}
                source = action_dict['source']
                target = action_dict['target']
                action_seq = action_dict['action_seq']
                for i in range(len(action_seq)):
                    one_episode_joint_action[i].append({
                        'source': source,
                        'target': target,
                        'toll': action_seq[i]
                    })
        return one_episode_joint_action


        
        
