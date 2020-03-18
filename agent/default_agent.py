import random
class DefaultAgent():

    def __init__(self):
        super().__init__()

    def act(self, obs):
        return random.random() * 6
        