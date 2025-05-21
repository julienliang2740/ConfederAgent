"""
Copyright 2023 Wenyue Hua

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""

__author__ = "Wenyue Hua"
__copyright__ = "Copyright 2023, WarAgent"
__date__ = "2023/11/28"
__license__ = "Apache 2.0"
__version__ = "0.0.1"

from history_setting.action_definition import *
from procoder.prompt import *
from history_setting.action_definition import action_property_definition
from prompt import *
from building_blocks.secretary import Secretary
from building_blocks.agent import *
from utils import * 
import datetime
import argparse

import json
import sys
import os

# for testing convenience
testingbar = "==================================================TESTING==================================================\n==================================================TESTING==================================================\n==================================================TESTING=================================================="


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trigger', type=str, default="", help='triggering event')
    parser.add_argument('--rounds', type=int, default=10, help='number of rounds')
    parser.add_argument('--model', type=str, default='gpt-4o-mini', help='choose the model name')
    parser.add_argument('--experiment_type', type=str, default='trigger', help='experiment name: accuracy, trigger, or country_profile')
    parser.add_argument('--experiment_name', type=str, default='test', help='special name for experiment in logging file name')
    parser.add_argument('--scenario', type=str, default='WWI', help='WWI, WWII, Warring_States_Period')
    parser.add_argument('--type_speed', type=int, default=500, help='typing speed for thought process')
    parser.add_argument('--present_thought_process', action='store_true', help='whether to print thought process')
    return parser

## counterfactual triggering event
# trigger = "Today is sunny and nothing special happened."

# trigger = """
# Country P and Country B were involved in a grave naval incident. 
# A Country B ship was sunk, resulting in 10 fatalities. 
# Country B, asserting that the sunken vessel was a civilian business ship, demanded an apology from Country P. 
# Country P fiercely countered, claiming the Country B ship was a military vessel that had no right to intrude in Country P's maritime territory, and declared that the tragedy was Country B's own doing.
# """

# trigger = """
# Country A and Country R clashed in a military conflict over the strategic Allison Strait, a vital hub for port and export activities. 
# Country R is determined to dominate the area for ports to boost its export prospects, clashed fiercely with armies from Country A. 
# Country A resisted relinquishing control and will not acknowledge Country R's dominance in the area, which a direct threat to Country A's own export capabilities.
# Country R's army has killed over hundreds soldiers from Country A in the conflict, feuling Country A's anger.
# """

def creating_log(experiment_type, experiment_name, scenario, model):
    scenario_name = scenario.replace(" ", "")
    model_name = model.replace("/", "")
    now = datetime.datetime.now()
    time_string = now.strftime("%Y-%m-%d_%H:%M:%S")
    logging_dir = "log/{}/{}_{}_{}_{}.log".format(experiment_type, experiment_name, scenario_name, model_name, time_string)
    logger = Logger(logging_dir, True)
    return logger 

if __name__ == "__main__":
    ## parse arguments
    parser = create_parser()
    args = parser.parse_args()

    ## open the json file
    scenario_file = os.path.join('./history_setting', args.scenario + '.json')
    with open(scenario_file, 'r') as file:
        scenario_data = json.load(file)

    ## basic setting to log for experiment
    trigger = args.trigger
    if trigger == "":
        trigger = scenario_data["trigger"]
    experiment_type = args.experiment_type
    experiment_name = args.experiment_name
    logger = creating_log(experiment_type, experiment_name, args.scenario, args.model)

    ## log the triggering event
    logger.log('Trigger: {}\n\n'.format(trigger))

    init(autoreset=True)
    inputs = {"situation": "[Situation]"}

    ### define all agents
    scenario_agents = scenario_data["agents_list"]

    secretary_agent = Secretary(action_property_definition)

    formatting_agent = FormattingAgent(FORMATTING_AGENT_PROMPT, action_list)

    all_agents = intialize_scenario_agents(scenario_agents, secretary_agent, formatting_agent, MODEL=args.model, scenario_data=scenario_data)
      
    agent_number = len(all_agents)

    ### simulation start
    respective_situation_for_agents = [trigger] * agent_number
    respective_requests_for_agents = [[]] * agent_number
    for round in range(args.rounds):
        print_day(round, logger)
        # all agent plan simultaneously, collect the messages and create situation
        agent_responses = []
        for agent_index, agent in enumerate(all_agents):
            source_country, agent_messages, thought_process = agent.plan(
                trigger, respective_situation_for_agents[agent_index], respective_requests_for_agents[agent_index], round, scenario_agents
            )
            print_country(scenario_data, source_country, logger)
            if args.present_thought_process:
                slow_type(scenario_data, args.type_speed, thought_process)
            print_message(scenario_data, agent_messages, logger)
            agent_responses += agent_messages

        # agent update information after observation
        for agent_index, agent in enumerate(all_agents):
            public_messages, private_messages, requests = agent.observe(agent_responses)
            situation = public_messages + private_messages
            respective_situation_for_agents[agent_index] = situation
            respective_requests_for_agents[agent_index] = requests
            # update boad and stick
            print(f'For {agent.identity}:')
            agent.board = agent.secretary_agent.update_board(situation, agent.board)
            agent.board = agent.secretary_agent.update_board(requests, agent.board)
            agent.stick = agent.secretary_agent.update_stick(situation, agent.stick)
            agent.stick = agent.secretary_agent.update_stick(requests, agent.stick)
            # print board and stick
            board_display = agent.board.display_board()
            stick_text = agent.stick.translate_to_text()
            print(stick_text)
            logger.log_board_and_stick(board_display, stick_text, agent.identity)
