import sys
from colorama import init, Fore, Style

sys.path.append('../')

class Agent:
    def __init__(self, identity, profile): # , agents, secretary_agent, model
        self.identity = identity # str: name of the agent for the simulation
        self.profile = profile # str: prompt with the general setting info and agent identity
    
    def __str__(self):
        return f"##### Party Agent Identity: {self.identity} #####"