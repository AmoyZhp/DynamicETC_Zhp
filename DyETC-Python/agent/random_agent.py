import random
from agent.de_mcts_agent import ActionSeqWrapper


class RandomAgent():

    def __init__(self, road_source, road_target, action_range, max_time_step):
        self.agent_id = {'source': road_source, 'target': road_target}
        self.action_range = action_range
        self.max_time_step = max_time_step
        self.actions = []
        for action in self.action_range:
            self.actions.append([action for _ in range(max_time_step)])
    def act(self):
        index = random.randint(0,len(self.actions)-1)
        return ActionSeqWrapper(self.agent_id, self.actions[index],1)
    
    def get_id(self):
        return self.agent_id