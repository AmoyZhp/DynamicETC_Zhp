import random
class DefaultAgent():

    def __init__(self,road_source, road_target, action_space):
        """
        
        Arguments:
            road_source {int} -- agent 代表的路的起点
            road_target {int} -- agent 代表的路的终点
            action_space {list} -- 一个长度为 2 的 list，第 0 个表示行动的下限，第 1 个表示行动的上限。
        """
        self.road_source = road_source
        self.road_target = road_target
        self.down_bound = action_space[0]
        self.upper_bound = action_space[1]
    

    def act(self, obs):
        base = random.uniform(0,1)
        toll = base * (self.upper_bound - self.down_bound) + self.down_bound
        action = {
            "source" : self.road_source,
            "target" : self.road_target,
            "toll" : toll
        }
        return  action
        