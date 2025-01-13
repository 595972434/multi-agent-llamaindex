# Multi-agent system
This repo refers to [multi-agent-concierge](https://github.com/run-llama/multi-agent-concierge) to implement a multi-agent system with information agent and health coaching agent. The simplified flow chat is shown below:

![flow-chat](./flow-chart.png)

## Setup
- specify python3.12
- install dependencies
- rename .demo_env to .env and update api base url and api key
- start service

```bash
poetry env use python3.12
poetry install
poetry run python main.py
```

## What we built

We built a system of agents to complete the above flow chat. There are two basic "task" agents:
* A health information agent (which takes care of questions like "How to learn genai")
* A health coaching agent (which takes care of questions like "I want to start health coaching")

Currently, the health coaching flow is a bit fixed, we just use some mock function to demo the workflow.

## Repo Structure

- `main.py` - the main entry point for the application. Sets up the global state and the agent pool, and starts the workflow. See this for a detailed quickstart example of how to use the system.
- `workflow.py` - the workflow definition, including all the agents and tools. This handles orchestration, routing, and human approval.
- `utils.py` - additional utility functions for the workflow, mainly to provide the `FunctionToolWithContext` class.

## The system in action

![workflow](./workflow.png)
To get a sense of how this works in practice, here's sample output during an interaction with the system.

At the beginning of the conversation, no active speaker is set, so you get routed to the concierge orchestration agent:

<blockquote>
<span style="color:blue">AGENT >>  Hello! How can I assist you today?</span>
<span style="color:white">USER >> I want to start health coaching</span>
<span style="color:green">SYSTEM >> Transferring to agent Health Coach Agent</span>
<span style="color:green">SYSTEM >> I need approval for the following tool call: get_user_information {} </span>
<span style="color:white">Do you approve? (y/n): y</span>
<span style="color:green">SYSTEM >> Retrieving user information</span>
<span style="color:green">SYSTEM >> Tool get_user_information called with {} returned The user information is {'age': 25, 'weight': 70, 'height': 180} and the user tasks are ['Walk 1000 steps everyday', 'Eat more green vegetables']. </span>
<span style="color:blue">AGENT >>  Great! To tailor our health coaching to your needs, could you please share your specific health goal with me? </span>
<span style="color:white">USER >> gain muscle </span>
<span style="color:blue">AGENT >> Final response in json format </span>
<span style="color:white">bye</span>
</blockquote>


Here, we see the orchestration agent routing to the health coaching agent, and then asking for an approval of getting user information.

<blockquote>
<span style="color:blue">AGENT >>  Hello! How can I assist you today?</span>
<span style="color:white">USER >> Is eating a lot of apples considered healthy?</span>
<span style="color:green">SYSTEM >> Transferring to agent Information Agent</span>
<span style="color:blue">AGENT >> Eating apples can be a healthy part of a balanced diet, xxxxxxx </span>
<span style="color:white">bye</span>
</blockquote>

Here, we see the orchestration agent routing to the information agent since we send a general question of genai.

## What's next
- Add real tool calls to get user information via api