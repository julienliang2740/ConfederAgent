# ConfederAgent

## Setup and Installation
```
git clone https://github.com/julienliang2740/ConfederAgent.git
cd ConfederAgent
cd src
pip install -r requirements.txt
```

## Simulation Arguments
```
trigger: str -> trigger event to start off scenario, can also be specified in scenario file
rounds: int -> number of rounds to run
model: str -> which llm model to run (currently only supoorts openai)
scenario: str -> file name of the scenario file to run
type_speed: int -> typing speed for thought process (you can safely ignore this for every run)
present_thought_process: bool -> whether to print thought process
```

## Example Run (from src/ folder)
```
python main.py --scenario Canada2025
```
