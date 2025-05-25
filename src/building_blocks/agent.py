from building_blocks.prompt import *
from building_blocks.model import *

import sys
from colorama import init, Fore, Style

sys.path.append('../')

class Agent:
    def __init__(self, identity, profile, model):
        self.identity = identity # str: name of the agent for the simulation
        self.profile = profile # str: prompt with the general setting info and agent identity
        self.model = model
    
    def __str__(self):
        return f"##### Party Agent Identity: {self.identity} #####"


    def generate_actions(self, game_state, round_number, trigger_event):
        situation_prompt = "\n##### Situation \n" + f"Day 0: {trigger_event}\n" + self.generate_action_history(game_state) + "\n" + self.generate_chat_history(game_state)

        full_prompt = self.profile + situation_prompt + action_list_prompt + thought_process_prompt

        actions_list = generate_action(full_prompt, self.model, "regular")

        return actions_list
    
    def generate_vote_actions(self, game_state, trigger_event):
        return ""

    def generate_chat_history(self, chat_log):
        return ""

    def generate_action_history(self, game_state):
        return ""
        