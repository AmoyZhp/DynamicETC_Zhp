from env.dynamic_etc import DynamicETC
from agent.default_agent import DefaultAgent 
class Runner():
    def __init__(self):
        super().__init__()
    
    def process_state_to_obs(self, state, i):
        return []

    def run(self):
        dyenv = DynamicETC()
        action_space = dyenv.action_space
        agents = {}
        # each road has an agent to adjust toll
        for i in range(action_space[2]) :
            agents[i] = DefaultAgent()

        state = dyenv.reset()
        cnt = 0
        while True:
            actions = {}
            # get union action
            for key, agent in agents.items():
                obs = self.process_state_to_obs(state, i)
                act = agent.act(obs)
                actions[key] = act
            next_state, reward, terminal, info = dyenv.step(actions)
            if terminal:
                break
            print(cnt)
            cnt += 1
            state = next_state