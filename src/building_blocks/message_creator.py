# construct output text for outputting/prompting for action history (from the game state) -> for agent prompts and logging/terminal output
# doer -> str: name of party
# action -> dict: dict containing action info (should be the same as the Pydantic formattings)
# verbose -> bool: whether to be wordy and output the entire content of bills and no confidence motions
# note: voting is also not addressed here -> they arent in the regular round action space, grouped with voting, separate function
def create_action_text(doer, action, verbose):
    to_return = ""

    if action['action_name'] == "Propose Bill":
        to_return = f"    - {doer} proposes the following Bill for voting: {action['bill_name']}\n"
        if verbose:
            to_return = to_return + f"The content of the Bill are as follows: {action['bill_content']}\n"
    elif action['action_name'] == "Motion of No Confidence":
        to_return = f"    - {doer} moved a vote of no confidence against the sitting government.\n"
        if verbose:
            to_return = to_return + f"The motion reads as follows: {action['bill_content']}\n"
    elif action['action_name'] == "Send Message":
        to_return = f"    - {doer} sends a message to {action['target']}: {action['message_content']}\n"
    elif action['action_name'] == "Make Public Statement":
        to_return = f"    - {doer} makes the following public statement: {action['statement_content']}\n"

    return to_return

def create_voting_text(doer, bill, action):
    pass