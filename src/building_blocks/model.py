# from building_blocks.actions import *
from actions import *

from openai import OpenAI

from dotenv import load_dotenv
import os
import getpass

# rn we only doing openai models since they support the codebase (formatted outputs etc)
openai_models = ["gpt-4o-mini", "gpt-4o", "o1", "o3-mini"]

# load api key
load_dotenv()
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")


"""
Regular round output type: dict
Output format:
{
    'thought_process': "...",
    'actions': [
        {'action_name': '...', [other key/value pairs]},
        ...
    ]
}
"""

"""
Voting round output type: dict
(note: voting api is called per bill per party)
Output format:
{
    'thought_process': "...",
    action: Literal["For", "Against", "Abstain"]
    public_message: "..."
}
"""

def generate_action(prompt, model, round_type):
    actions = {}
    if round_type == "voting":
        actions = run_gpt("", prompt, VotingAction, 0, model)
    else:
        actions = run_gpt("", user_prompt, ActionsAndThoughtProcess, 0, model)
    return actions


def run_gpt(system_prompt, user_prompt, response_format, temperature: float = 0, model="gpt-4o-mini"):
    open_ai_key = os.environ["OPENAI_API_KEY"]
    client = OpenAI(api_key=open_ai_key)

    response = client.beta.chat.completions.parse(
      model=model,
      messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
      ],
      temperature=temperature,
      response_format=response_format
    )

    resp = response.choices[0].message.parsed
    resp_formatted = resp.model_dump() # resp_formatted should be a dict

    return resp_formatted

if __name__ == '__main__':
    system_prompt = "You are a political party agent in a parliament simulation game. Do actions and give your thought process"
    user_prompt = "You are a conservative political party agent in a parliament simulation. There is also the Liberal Party that is in charge, and the Trees and Flowers Party that is a relatively small but loud party. You are the official opposition. You are trying to forward your agenda of doing more fracking and drilling. Do every action possible to forward your agenda"
    user_prompt_voting = "Currently there is a bill to increase fossil fuel taxes by ten times. Do you vote for or against it? Give your thought process"

    # result = run_gpt(system_prompt, user_prompt, ActionsAndThoughtProcess)
    result = run_gpt(system_prompt, user_prompt_voting, VotingAction)

    print(result)


    # These are just here to look at
    output1 = {
        'thought_process': "As the official opposition, my primary goal is to promote our party's agenda of increasing fracking and drilling. To do this effectively, I need to engage in a multi-faceted approach that includes public statements to rally support, proposing a bill that outlines our plans, and possibly sending messages to key stakeholders to gain their backing. Additionally, I should consider the political landscape and the potential for a motion of no confidence against the Liberal Party if they continue to oppose our energy initiatives.", 
        'actions': [
            {'action_name': 'Make Public Statement', 'statement_content': 'The Conservative Party believes in the importance of energy independence and economic growth through responsible fracking and drilling. We urge the government to reconsider their stance and support our initiatives for a sustainable energy future.'}, 
            {'action_name': 'Propose Bill', 'bill_name': 'Energy Independence and Growth Act', 'bill_content': 'This bill aims to increase the opportunities for fracking and drilling in our country, ensuring that we utilize our natural resources responsibly while creating jobs and boosting the economy.'}, 
            {'action_name': 'Send Message', 'target': 'Liberal Party Leadership', 'message_content': 'We request a meeting to discuss the potential benefits of increasing fracking and drilling in our country. We believe that a collaborative approach can lead to a sustainable energy policy that benefits all.'}, 
            {'action_name': 'Make Public Statement', 'statement_content': "The Trees and Flowers Party's opposition to fracking is misguided. We must prioritize energy security and economic development over environmental concerns that can be managed responsibly."}
        ]
    }

    output2 = {
        'thought_process': "Increasing fossil fuel taxes by ten times could have significant implications for both the environment and the economy. On one hand, it could incentivize a shift towards renewable energy sources and reduce carbon emissions, aligning with our party's commitment to combat climate change. On the other hand, such a drastic increase could burden low-income families and small businesses that rely on fossil fuels, potentially leading to economic hardship and backlash from constituents. I need to weigh the long-term environmental benefits against the immediate economic impact on our voters. Additionally, I should consider the potential for public support or opposition to this bill and how it aligns with our party's platform. After careful consideration, I believe that while the intention behind the bill is commendable, the scale of the tax increase is too extreme and could lead to unintended consequences. Therefore, I will vote against it, advocating instead for a more gradual increase that allows for a smoother transition to renewable energy.", 
        'action': 'Against', 
        'public_message': 'While I support efforts to combat climate change, I believe that a tenfold increase in fossil fuel taxes is too extreme and could harm our economy and constituents. I advocate for a more balanced approach that encourages renewable energy without placing undue burden on families and businesses.'
    }