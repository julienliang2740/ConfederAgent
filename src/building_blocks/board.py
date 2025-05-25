from building_blocks.actions import *
from building_blocks.agent import *
from building_blocks.secretary import *
from building_blocks.prompt import *

"""
(note: in general feed the game state as a parameter to other functions, dont call it directly)

The game state contains the overall state of the game and all the relevant information that is to be preserved across rounds

Game State items:
1) Trigger event
- format: str
- content: the trigger event

2) History
- format: listof(dict(str:listof(str)))
^ [{"Round 1":[str, str, ...]}, ..., {"Voting Round":[str,...]}]
- content: list of dict of list of past actions (statements made, bills proposed and their results, etc) in strings (each dict has a key for the round name and a )

3) Parties
- format: dictof(str:dictof(str:int, str:bool))
^ {"[party name]": {"seats": INT, "is ruling party":BOOL}}
- content: Parties and their seats, including who is the ruling party(s)

4) Proposed Bills (THIS INCLUDES NO CONFIDENCE VOTES)
- format: listof(dictof(str:str))
^ [{]"[bill name]": "[bill contents]"}, ...]
- content: Bills that have been proposed and are currently up in the air, to be voted upon

5) Passed Bills
- format: listof(dictof(str:str))
^ [{"[bill name]": "[bill contents]"}, ...]
- content: Bills that have already been passed

6) Private Message Record
- format: dictof{str:listof(dictof(str:str))}
^ {"[party name]": [{"[sender]": "content"}, ...], ...}
- content: Private Messages that are specific to each Party Agent

Other things to add (once those features are implemented):
- outgoing coalition requests
- who is in a coalition with who
- election info
"""

game_state = {
    "Trigger Event": "",
    "History": [],
    "Parties": {},
    "Proposed Bills": [],
    "Passed Bills": [],
    "Private Message Record": {}

}



"""
The round state contains everything that has happened in the past round, this information is processed at the end of each round, generally this means that:
- messages are processed into "Private Message Record" in game_state
- bills and non-confidence motions are put into "Proposed Bills" in game_state

Round State items:
1) Private Message Record
- format: dictof(str:listof(dictof(str:str)))
^ {"[party name]": [{"[sender]": "content"}, ...], ...}
- content: Private Messages that are specific to each Party Agent

3) Public Statement Record
- format: dictof(str: listof(str), ...)
^ {"[party name]": ["[statement]", ...], ...}
- content: Public Statements made this round

2) Proposed Bills
- format: listof(dictof(str:str, str:str, str:str))
^ [{"Author": "...", "Bill Name": "...", "Bill Contents": "..."}]
- content: Bills that have been proposed and are currently up in the air, to be voted upon

Other things to add (once those features are implemented):
- outgoing coalition requests
- who is in a coalition with who
- election info
"""
round_state = {""
    "Private Message Record": {},
    "Public Statement Record": {},
    "Proposed Bills": []
}



"""
The board class encapsulates the whole simulation
All the agents each round do their stuff within the board class
"""

class Board:
    def __init__(self, scenario_data, logger):
        # Game and Round State (these change as the simulation goes on)
        self.game_state = game_state
        self.round_state = round_state

        # Action info (these are static)
        self.action_list = action_list
        self.action_format = ActionsAndThoughtProcess
        self.voting_action_format = VotingAction

        # Scenario data (extracted from json, with all the parties and their info)
        self.scenario_data = scenario_data
        self.num_parties = len(scenario_data["agents_list"])
        self.total_seats = sum(scenario_data["party_seats_map"].values())

        # Party agents, these are initialized in initialize_party_agents() fills the line below
        self.party_agents = []

        # Secrtary agent (this is static)
        self.secretary_agent = SecertaryAgent()

    # int - total_rounds: total number of rounds to run
    # int - voting_round_interval: number of rounds to run before doing a voting round
    def run(self, total_rounds, voting_round_interval):
        round_number = 1
        regular_rounds_since_vote = 0

        while round_number <= total_rounds:
            print(f"MONKE BRUGA ROUND {round_number}")
            self.run_round(round_number)
            round_number += 1
            regular_rounds_since_vote += 1

            if regular_rounds_since_vote == voting_round_interval:
                print("MONKE BRUGA VOTING ROUND")
                self.run_voting_round(self.game_state["Proposed Bills"])
                regular_rounds_since_vote = 0

    def run_round(self, round_number):
        pass

    def run_voting_round(self, bills):
        pass

    def update_game_state(self, current_round_state):
        pass

    def update_round_state(self, agent_actions_list):
        for action in agent_actions_list:
            pass

    # Create the Party Agents and the prompts for them (simulation setting, scenario info, which party they are, etc)
    def initialize_party_agents(self):
        # 1) create common prompt
        # 2) initialize each agent with its own agent-specific data/prompts
        scenario_agents_list = self.scenario_data["agents_list"]

        # 1) create common prompt
        # Parts to the common prompt: simulation setting, country info, parties info
        string_list_parties = ""
        for party in scenario_agents_list:
            string_list_parties += f"\n{party}"
        simulation_setting_prompt = f"""
You are an AI agent for a political party in a parliament simulation. There are {self.num_parties} parties in the simulation. The names of these parties are: {string_list_parties}
You are playing as the role of one of these parties. You are provided with the information of each of these parties, as well as information about the country your party is in. You can use many tools and actions to react to the current situation to forward the interests and goals of your country given the situation at large and for your specific party.
The simulation begins on Round 1 with an initial situation and the situation will change by rounds. There will be regular rounds as well as voting rounds where you vote on proposed bills. You should react to the latest situation by choosing the appropriate actions.
"""

        country_info_prompt = self.scenario_data["country_info"]

        parties_info_prompt = ""
        for party in scenario_agents_list:
            party_info = self.scenario_data[party]
            party_info_prompt = f"""
## {party} Information:
Leadership: {party_info["leadership"]}
Ideology and Beliefs: {party_info["ideology"]}
Parliamentary Metrics: {party_info["metrics"]}
Party History: {party_info["history"]}
Public Support: {party_info["public_support"]}
Tactics and Strategy: {party_info["tactics_and_strategy"]}
Demographic and Regional Bases: {party_info["demographic_and_regional_bases"]}
"""
            parties_info_prompt += party_info_prompt

        seat_distribution_prompt = ""
        for party in scenario_agents_list:
            party_seats = f"{party}: {self.scenario_data["party_seats_map"][party]}\n"
            seat_distribution_prompt += party_seats



        common_information_prompt = f"""
##### Simulation Overall Setting
{simulation_setting_prompt}

##### Country Information
{country_info_prompt}

##### Parties Information
{parties_info_prompt}

##### Seat Distribution
{seat_distribution_prompt}
The ruling party is {self.scenario_data["ruling_party"]}.
"""
        print(common_information_prompt)

        # 2) initialize each agent with its own agent-specific data/prompts
        for party in scenario_agents_list:
            party_assignment_prompt = f"""
##### Party Role Assignment
You are playing the role of {party}.
Your leadership has the features of {party}. You must act, message, and respond like {party}.
The party has the Ideology and Beliefs, Parliamentary Metrics, Party History, Public Support, Tactis and Strategy, as well as Demographic and Regional Bases as outlined in the information above for {party}. You must be aware of what your part is like, what it wants to achieve, and what it is capable of doing.
You must act to maximize your party's interests and the likelihood of forwarding your party's agenda and winning, following the key policies and interests of your party.
Play according to your own settings for {party}.
"""
            full_profile_prompt = common_information_prompt + party_assignment_prompt
            Party_Agent = Agent(
                identity=party,
                profile=full_profile_prompt
            )
            self.party_agents.append(Party_Agent)
