import gym
import math
import random
import json
from env.traffic_graph import TrafficGraph
from env.dyetc_state import DyETCState
import logging
                    
class DynamicETC(gym.Env):
    """DyETC 的环境容器，主要的属性有
        state: 是 DyETCState 类别。用来表示当前环境的状态
        timestep: 当前环境经历的时间步
        max_timestep: 环境最多经历的时间步
        memory: 存放 timestep 及之前的状态
    """

    def __init__(self, graph_data, max_timestep, state_data=None):
        self.state = DyETCState(graph_data, state_data)
        self.memory = [self.state.copy()]
        self.timestep = 0
        self.max_timestep = max_timestep
        self.graph_data = graph_data
        self.state_data = state_data

    def step(self, actions):
        self.timestep += 1
        tolls = []
        for action in actions:
            tolls.append({
                "source": action['source'],
                "target": action['target'],
                "toll": action['toll']
            })
        # reward 的计算应该在 update 之前
        reward = self.state.value()
        self.state.update(tolls)
        
        self.memory.append(self.state.copy())
        
        terminal = False
        if self.timestep == self.max_timestep:
            terminal = True
        info = {}
        return self.state, reward, terminal, info

    def reset(self):
        self.state = self.memory[0].copy()
        self.timestep = 0
        self.memory = [self.state.copy()]
        return self.state

    def get_state(self):
        return self.state.copy()
    
    def clone(self):
        return DynamicETC(self.state.graph_data, self.state.state_data)

    def render(self, mode=""):
        pass

    def close(self):
        pass
    
    def data(self):
        trajectory = []
        for state in self.memory:
            state_data = state.data()
            trajectory.append(state_data)
        return {
            'trajectory': trajectory
        }


