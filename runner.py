from env.dynamic_etc import DynamicETC
from agent.default_agent import DefaultAgent 
class Runner():
    def __init__(self):
        super().__init__()
    
    def process_state_to_obs(self, state, i):
        pass

    def run(self):
        env = DynamicETC()
        action_space = env.action_space
        agents = []
        # each road has an agent to adjust toll
        for i in range(action_space) :
            agents.append(DefaultAgent())
        
        state = env.reset()
        while True:
            actions = []
            # get union action
            for i in range(len(agents)):
                obs = self.process_state_to_obs(state, i)
                action = agents[i].act(obs)
                actions.append(action)
            next_state, reward, terminal, info = env.step(actions)
            if terminal:
                break
            state = next_state