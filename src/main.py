from utils.logging import *
from building_blocks.board import Board, game_state, chat_history
from building_blocks.agent import *

import argparse
import json
import sys
import os
import datetime

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trigger', type=str, default="", help='triggering event')
    parser.add_argument('--rounds', type=int, default=10, help='number of rounds')
    parser.add_argument('--model', type=str, default='gpt-4o-mini', help='choose the model name')
    parser.add_argument('--scenario', type=str, default='example', help='file name of the scenario file to run')
    parser.add_argument('--type_speed', type=int, default=500, help='typing speed for thought process')
    parser.add_argument('--present_thought_process', action='store_true', help='whether to print thought process')
    return parser

def creating_log(scenario, model):
    scenario_name = scenario.replace(" ", "")
    model_name = model.replace("/", "")
    now = datetime.datetime.now()
    time_string = now.strftime("%Y-%m-%d_%H:%M:%S")
    logging_dir = "log/{}_{}_{}.log".format(scenario_name, model_name, time_string)
    logger = Logger(logging_dir, True)
    return logger 

if __name__ == '__main__':
    # Setup:
    # 1. Parse arguments
    # 2. Open scenario file
    # 3. Set up logger and log file

    # Setup 1: Parse arguments
    parser = create_parser()
    args = parser.parse_args()

    # Setup 2: Open scenario file
    scenario_file = os.path.join('./scenario_files', args.scenario + '.json')
    with open(scenario_file, 'r') as file:
        scenario_data = json.load(file)
    
    # Setup 3: Set up logger and log file
    # basic setting to log
    trigger = args.trigger
    if args.trigger == "":
        trigger = scenario_data["trigger"]
    logger = creating_log(args.scenario, args.model)

    # log trigger event
    logger.log('Trigger: {}\n\n'.format(trigger))

    ##### Initialize Board and Agents #####
    Simulation = Board(scenario_data, logger, args.model, args.present_thought_process)
    Simulation.initialize_party_agents()

    ##### Start Running the Simulation #####
    Simulation.run(10,3)