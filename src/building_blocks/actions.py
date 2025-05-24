from pydantic import BaseModel
from typing import Literal, Union, Tuple

"""
Each action is a key, value pair in the actions_list dict:
    "[Action Name]": {
        "Input Content": "[Natural text description of what the input for the action is, ex. contents of a bill, a message to send to another party]",
        "Input Specification": "[The specific format specification of how the input should be, ex. dictionary with key and value both as str, list of strings]",
        "Action Description": "[Description of the action and what it does]",
        "Example": "[Full written out example usage]"
        "Has Target": "[Whether the action has a target]"
        "Require Response": [Whether a response is required],
        "Is Public": "[Whether the action is public]",
        "Descriptor": "[For linguistically fluent logging purposes]"
    },

NOTE: VOTING FOR/AGAINST IS NOT COUNTED IN ACTIONS (since it is a binary, and it's dealt with elsewhere)
"""

action_list = {
    "Propose Bill": {
        "Input Content": (
            "Provide the title of your new bill, followed by a detailed description: "
            "explain its purpose, key provisions, funding clauses (if any), and any implementation steps."
        ),
        "Input Specification": "A string for the title of the bill, and a string for the contents of the bill",
        "Action Description": "Drafts and formally introduces a new legislative proposal for debate and vote in parliament.",
        "Example": "",
        "Has Target": False,
        "Require Response": False,
        "Is Public": True,
        "Descriptor": ""
    },
    "Motion of No Confidence": {
        "Input Content": (
            "Summarize your motion: state the government or leader you have no confidence in, "
            "list the main reasons, and outline the intended consequence if it passes."
        ),
        "Input Specification": "A string for the contents of the motion of no confidence",
        "Action Description": "Tables a formal no-confidence motion against the sitting government, triggering debate and a potential confidence vote.",
        "Example": "",
        "Has Target": False,
        "Require Response": False,
        "Is Public": True,
        "Descriptor": ""
    },
    "Send Message": {
        "Input Content": (
            "Specify the recipient (party or member) and then the body of your private message: "
            "state your intent, arguments, or requests clearly."
        ),
        "Input Specification": "A string for the target recipient, and a string for the message contents. For the target recipient, enter the name EXACTLY THE SAME AS IT IS SPECIFIED (do not add any descriptors or change the spelling in any way)",
        "Action Description": "Sends a confidential communication to another party or member to negotiate or share information.",
        "Example": "",
        "Has Target": True,
        "Require Response": False,
        "Is Public": False,
        "Descriptor": ""
    },
    "Make Public Statement": {
        "Input Content": (
            "Write your public address: include key talking points, the intended audience, "
            "and any calls to action or policy positions you wish to broadcast."
        ),
        "Input Specification": "A string containing the full statement text",
        "Action Description": "Issues an official public statement announcing party positions or responding to current events.",
        "Example": "",
        "Has Target": False,
        "Require Response": False,
        "Is Public": True,
        "Descriptor": ""
    },
    # "Propose Coalition": {
    #     "Input Content": "",
    #     "Input Specification": "",
    #     "Action Description": "",
    #     "Has Target": True,
    #     "Require Response": True,
    #     "Is Public": "",
    #     "Descriptor": ""
    # },
    # "Accept Coalition": {
    #     "Input Content": "",
    #     "Input Specification": "",
    #     "Action Description": "",
    #     "Has Target": True,
    #     "Require Response": False,
    #     "Is Public": "",
    #     "Descriptor": ""
    # },
    # "Reject Coalition": {
    #     "Input Content": "",
    #     "Input Specification": "",
    #     "Action Description": "",
    #     "Has Target": True,
    #     "Require Response": False,
    #     "Is Public": "",
    #     "Descriptor": ""
    # },
    # "Leave Coalition": {
    #     "Input Content": "",
    #     "Input Specification": "",
    #     "Action Description": "",
    #     "Has Target": False,
    #     "Require Response": False,
    #     "Is Public": "",
    #     "Descriptor": ""
    # },
    # "": {
    #     "Input Content": "",
    #     "Input Specification": "",
    #     "Action Description": "",
    #     "Has Target": False,
    #     "Require Response": False,
    #     "Is Public": "",
    #     "Descriptor": ""
    # },
}

##### Pydantic formatting code (for the llm) #####
# Formatting class for each individual action
class ProposeBill(BaseModel):
    action_name: Literal["Propose Bill"]
    bill_name: str
    bill_content: str

class MotionNoConfidence(BaseModel):
    action_name: Literal["Motion of No Confidence"]
    bill_content: str

class SendMessage(BaseModel):
    action_name: Literal["Send Message"]
    target: str
    message_content: str

class MakePublicStatement(BaseModel):
    action_name: Literal["Make Public Statement"]
    statement_content: str

# What the LLM sees:
class ActionsAndThoughtProcess(BaseModel):
    thought_process: str
    actions: list[Union[ProposeBill, MotionNoConfidence, SendMessage, MakePublicStatement]]

class VotingAction(BaseModel):
    thought_process: str
    action: Literal["For", "Against", "Abstain"]
    public_message: str