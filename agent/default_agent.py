import random
class DefaultAgent():

    def __init__(self,road_id, road_source, road_target):
        self.road_id = road_id
        self.road_source = road_source
        self.road_target = road_target

    def act(self, obs):
        toll = round(random.random() * 6, 3)
        action = {
            "source" : self.road_source,
            "target" : self.road_target,
            "toll" : toll
        }
        return  action
        