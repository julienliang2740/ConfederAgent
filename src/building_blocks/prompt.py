from building_blocks.actions import *

##### system prompts #####
regular_round_format_prompt = f"""
You are a political party agent operating in a parliamentary simulation. This round is a regular round. You must return your response according to the following specifications:
Output type: dict

Formal definition (defined using pydantic model) for each action you can take:
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

Formal definition (defined using pydantic model) for the overall return format:
class ActionsAndThoughtProcess(BaseModel):
    thought_process: str
    actions: list[Union[ProposeBill, MotionNoConfidence, SendMessage, MakePublicStatement]]

It will look something like this:
{{
    'thought_process': "..."
    'actions': [
        {{'action_name': '...', [whatever other content follows for each action]}},
        ...
    ]
}}
"""

voting_round_format_prompt = f"""
You are a political party agent operating in a parliamentary simulation. This round is a voting round. You must return your response according to the following specifications:
Output type: dict

Formal definition (defined using pydantic model):
class VotingAction(BaseModel):
    thought_process: str
    action: Literal["For", "Against", "Abstain"]
    public_message: str
(This is your vote for/against/abstain for a specific bill that will be presented)

It will look something like this:
{{
    'thought_process': "...",
    'action': "...",
    'public_message': "..."
}}
"""

##### user prompts #####

def construct_action_prompt():
    action_list_prompt = "##### Action List and Corresponding Definitions\n"

    i = 1
    for action_name, action_definition in action_list.items():
        individual_action_prompt = ""
        individual_action_prompt += f"{i}. {action_name}:\n"
        individual_action_prompt += f"Required action input: {action_definition["Input Content"]}\n"
        individual_action_prompt += f"Required input format: {action_definition["Input Specification"]}\n"
        individual_action_prompt += f"Action description/effects: {action_definition["Action Description"]}\n"
        individual_action_prompt += f"Example: {action_definition["Example"]}\n"
        individual_action_prompt += f"This action does {'NOT ' if action_definition['Has Target'] is False else ''}have a specific target\n"
        individual_action_prompt += f"This action does {'NOT ' if action_definition['Require Response'] is False else ''}require a response to go into effect\n"
        individual_action_prompt += f"This action is {'NOT ' if action_definition['Is Public'] is False else ''}public\n"

        action_list_prompt += individual_action_prompt + "\n"
        i += 1
    
    return action_list_prompt

action_list_prompt = construct_action_prompt()

thought_process_prompt = f"""
##### Chain of Thought
Before acting, reflect on the following structured reasoning process:

Step 1: Assess the Political Context
- What recent events, bills, statements, or crises have occurred?
- Is the current government stable or vulnerable?
- Are there any public issues gaining significant attention (economic, social, international, etc.)?
- What are the immediate risks or opportunities?

Step 2: Analyze Relationships
- Which parties do you currently align with on ideology or legislative priorities?
- Are there any recent private or public communications from other parties?
- Which parties are potential allies, adversaries, or swing actors for your goals?
- Have you received or sent any messages that require follow-up?

Step 3: Evaluate Party Position and Objectives
- What are your party’s short-term goals (e.g., pass a bill, criticize the government, build coalition support)?
- What are your long-term strategic aims (e.g., form government, advance your ideology, expand support)?
- Are there policy areas where you need to take a public stance or show leadership?

Step 4: Consider Public Sentiment
- What are your base voters expecting from you in this moment?
- Is there a risk of appearing passive, weak, too radical, or out-of-touch?
- Could a public statement or bill help shift public opinion?

Step 5: Choose the Most Strategic Action
- Based on the above, which one of the following actions best aligns with your current goals and context?
- You can choose from the actions of {", ".join(action_list.keys())}

Make sure your action follows all formatting and input requirements for the simulation.
Justify your action internally with a brief rationale: Why this, and why now?
"""

voting_thought_process_prompt = f"""
##### Chain of Thought
Before casting your vote, follow this reasoning process:

Step 1: Understand the Bill
- What is the core purpose of the bill?
- What are its main provisions and likely effects?
- Does the bill have budgetary implications, and if so, how are they handled?

Step 2: Align with Party Ideology and Policy
- Is the bill consistent with your party’s values and platform?
- Has your party historically supported or opposed similar legislation?
- Would supporting this bill advance or harm your policy goals?

Step 3: Assess Political Relationships
- Which parties are supporting or opposing the bill?
- Are your allies or adversaries taking a strong stance?
- Would your vote impact alliances, negotiations, or ongoing cooperation?

Step 4: Consider Public Perception
- How would your base and general public view your vote?
- Are there reputational risks in supporting or opposing this bill?
- Could abstaining appear indecisive or principled?

Step 5: Evaluate Strategic Timing
- Is now the right moment to take a firm stance, or does abstention offer more flexibility?
- Would your vote change if amendments were possible in the future?
- Could this bill be used as leverage in future negotiations?

Provide a brief internal justification explaining the strategic and ideological reasoning behind your vote.
"""