from building_blocks.prompt import *
from building_blocks.model import *
from building_blocks.message_creator import *

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


    def generate_actions(self, game_state, chat_history, round_number, trigger_event):
        situation_prompt = ""
        if round_number == 1:
            situation_prompt = "\n##### Situation \n" + f"Day 0: {trigger_event}\n"
        else:
            situation_prompt = "\n##### Situation \n" + f"Day 0: {trigger_event}\n" + self.generate_action_history(game_state) + "\n" + self.generate_chat_history(chat_history)

        full_prompt = self.profile + situation_prompt + action_list_prompt + thought_process_prompt

        if round_number > 1:
            print("MONKE BRUGA")
            print("#"*500)
            print(game_state)
            print("#"*500)
            print(chat_history)
            print("#"*500)
            print(full_prompt)
            print("#"*500)
            exit()


        actions_list = generate_action(full_prompt, self.model, "regular")

        return actions_list

    def generate_vote_actions(self, game_state, trigger_event):
        return ""

    def generate_chat_history(self, chat_history):
        to_return = "\n##### These are the messages your party has had with other parties:\n"

        my_chat_history = chat_history[self.identity]
        for party, messages in my_chat_history.items():
            party_dms = f"Messages with {party}:\n"
            for message in messages:
                party_dms = party_dms + f"Round {message['round_number']} - {'to' if message['self_is_sender'] else 'from'} {party}: {message['content']}\n"
            to_return = to_return + party_dms

        return to_return

    def generate_action_history(self, game_state):
        # we generate the action history largely using the history section of the game_state
        # recall that the keys for history are floats (whole numbers for normal rounds, x.5 for voting rounds)
        # so if theres a vote every 3 rounds itll looks smtg like: {1:..., 2:..., 3:..., 3.5:..., 4:..., 5:..., 6:..., 6.5:..., 7:..., and so on}
        to_return = "\n##### This is the history of actions up to this point:\n"

        history = game_state['History']
        round_numbers = list(history.keys())
        round_numbers.sort()

        for round_number in round_numbers:
            round_history = ""
            if round_number.is_integer():
                round_history = f"## Round {int(round_number)}:\n"
            else:
                round_history = f"## VOTING ROUND:\n"

            round_info = history[round_number]
            for party, actions in round_info.items():
                round_history = round_history + f"{party}:\n"
                for action in actions:
                    action_text = create_action_text(party, action, False)
                    round_history = round_history + action_text
            
            to_return += round_history
        
        return to_return
