from building_blocks.actions import *
from building_blocks.agent import *
from building_blocks.secretary import *
from building_blocks.prompt import *

"""
(note: this is a little outdated :skull:, sample of newer version in a diff file)

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

"""
current game_state format
key -> str, val -> list

game_state["History"] -> {ROUND_NUMBER: {PARTY_NAME: [action1, action2, ...], ...}, ...}
game_state["Proposed Bills"] -> [{"proposer": PARTY_NAME, "title": "...", "content": "..."}, ...]
game_state["Passed Bills"] -> [{"proposer": PARTY_NAME, "title": "...", "content": "..."}, ...]
game_state["No Confidence in Motion"] -> bool for whether no confidence has been brought up

VERY IMPORTANT THAT ROUND NUMBER IS STORED AS FLOAT -> ROUND.5 IS FOR VOTING ROUND (ex. 3 and 3.5)
^GAME HISTORY FOR VOTING ROUNDS WILL HAVE DIFF FORMAT
"""

game_state = {
    "History": {},
    "Proposed Bills": [],
    "Passed Bills": [],
    "No Confidence in Motion": False
}

"""
chat_history contains all the private messages
self_is_sender -> is the party that is the big key the one sending it

format example:
{
    "Party A": {
        "Party B": [{"round_number": ROUND_NUMBER_FLOAT, "self_is_sender": BOOL, "content", "..."}, ...],
        "Party C": [^same as above]
    },
    ^repeat for Party B and Party C
}

"""
chat_history = {}


"""
The board class encapsulates the whole simulation
All the agents each round do their stuff within the board class
"""

class Board:
    def __init__(self, scenario_data, logger, model, present_thought_process):
        agents_list = scenario_data["agents_list"]

        # Game and Round State (these change as the simulation goes on)
        self.game_state = game_state
        self.chat_history = {}
        for agent_name in agents_list:
            self.chat_history[agent_name] = {}
            for other_agent_name in agents_list:
                if other_agent_name != agent_name:
                    self.chat_history[agent_name][other_agent_name] = []

        # Action info (these are static)
        self.action_list = action_list
        self.action_format = ActionsAndThoughtProcess
        self.voting_action_format = VotingAction

        # Scenario data (extracted from json, with all the parties and their info)
        self.scenario_data = scenario_data
        self.num_parties = len(agents_list)
        self.total_seats = sum(scenario_data["party_seats_map"].values())

        # Party agents, these are initialized in initialize_party_agents() fills the line below
        self.party_agents = []

        # Other things
        self.secretary_agent = SecertaryAgent()
        self.logger = logger
        self.model = model
        self.present_thought_process = present_thought_process

    # int - total_rounds: total number of rounds to run
    # int - voting_round_interval: number of rounds to run before doing a voting round
    def run(self, total_rounds, voting_round_interval):
        round_number = 1
        regular_rounds_since_vote = 0

        while round_number <= total_rounds:
            turn_record, though_process_record = self.run_round(round_number)
            self.update_chat_history(turn_record, round_number)
            self.update_game_state(turn_record, round_number)
            print("="*100)
            print(self.chat_history)
            print("="*100)
            print(self.game_state)
            print("="*100)
            exit()
            
            round_number += 1
            regular_rounds_since_vote += 1

            if regular_rounds_since_vote == voting_round_interval:
                self.run_voting_round(self.game_state["Proposed Bills"])
                regular_rounds_since_vote = 0

    def run_round(self, round_number):
        print(f"MONKE BRUGA ROUND {round_number}")

        # dictof(str:listof(actions), ...) - turn_record: each key is a party name, the corresponding value is their list of actions
        turn_record = {}
        # dictof(str:str, ...) - thought_process_record: each key is a party name, the value is a str with the thought process
        thought_process_record = {}
        
        for party_agent in self.party_agents:
            party_agent_actions = party_agent.generate_actions(self.game_state, round_number, self.scenario_data["trigger"])
            turn_record[party_agent.identity] = party_agent_actions['actions']
            thought_process_record[party_agent.identity] = party_agent_actions['thought_process']

        print("======================================\n" * 5)
        print(turn_record)
        print(thought_process_record)
        return turn_record, thought_process_record

    def run_voting_round(self, bills):
        print("MONKE BRUGA VOTING ROUND")
        self.game_state["No Confidence in Motion"] = False

    def update_chat_history(self, turn_record, round_number):
        for agent_name in turn_record.keys():
            for action in turn_record[agent_name]:
                if action['action_name'] != "Send Message":
                    continue
                target_agent_name = action["target"]
                message_content = action["message_content"]
                self.chat_history[agent_name][target_agent_name].append({"round_number": round_number, "self_is_sender": True, "content": message_content})
                self.chat_history[target_agent_name][agent_name].append({"round_number": round_number, "self_is_sender": False, "content": message_content})

    # note: the current design makes it so that the first party to ever raise no confidence is the only one who gets their bill put up to vote, may change later
    def update_game_state(self, turn_record, round_number):
        # actual processing
        self.game_state["History"][round_number] = {}
        for agent_name in turn_record.keys():
            # initialize empty list
            self.game_state["History"][round_number][agent_name] = []
            # go through actions
            for action in turn_record[agent_name]:
                action_name = action['action_name']
                # skip "Send Message" actions -> these are dealt with in update_chat_history
                if action_name == "Send Message":
                    continue

                # processing for other actions
                self.game_state["History"][round_number][agent_name].append(action)
                if action_name == "Propose Bill":
                    self.game_state["Proposed Bills"].append({"proposer": agent_name, "title": action["bill_name"], "content": action["bill_content"]})
                elif action_name == "Motion of No Confidence":
                    if self.game_state["No Confidence in Motion"] == True: # if a no confidence call is already in motion then skip this one, considered as repeat
                        continue
                    self.game_state["Proposed Bills"].append({"proposer": agent_name, "title": "Motion of No Confidence", "content": action["bill_content"]})
                    self.game_state["No Confidence in Motion"] = True

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
                profile=full_profile_prompt,
                model=self.model
            )
            self.party_agents.append(Party_Agent)
