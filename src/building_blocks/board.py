"""
(note: in general feed the game state as a parameter to other functions, dont call it directly)

The game state contains the overall state of the game and all the relevant information that is to be preserved across rounds

Game State items:
1) Trigger event
- format: str
- content: the trigger event

2) History
- format: listof(str)
- content: list of past actions (statements made, bills proposed and their results, etc) in strings

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
^ [{]"[bill name]": "[bill contents]"}, ...]
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