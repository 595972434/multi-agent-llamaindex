import os

import dotenv
from guardrails import Guard
from openai import OpenAI

from guardrail_validator import TopicLimit, pii_detect

dotenv.load_dotenv()

def function_call_with_openai():
    os.environ["OPENAI_API_KEY"] = os.getenv("API_KEY")
    os.environ["OPENAI_BASE_URL"] = os.getenv("BASE_URL")
    client = OpenAI()

    tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current temperature for a given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and country e.g. Bogotá, Colombia"
                    }
                },
                "required": [
                    "location"
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    },
            {
                "type": "function",
                "function": {
                    "name": "sum_numbers",
                    "description": "Sum the two given nums a given location.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "x": {
                                "type": "string",
                                "description": "number 1 to be added"
                            },
                            "y": {
                                "type": "string",
                                "description": "number 2 to be added"
                            },
                        },
                        "required": [
                            "x", 'y'
                        ],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }]

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "calculate 3+2"}],
        tools=tools
    )

    print(completion)

def function_call_with_guardrails():

    os.environ["OPENAI_API_KEY"] = os.getenv("API_KEY")
    os.environ["OPENAI_API_BASE"] = os.getenv("API_BASE")
    guard = Guard().use(
        TopicLimit(threshold=50)
    ).use(pii_detect, on_fail="noop")
    result = guard(
        messages=[{"role": "user", "content": "calculate 3+2"}],
        model="gpt-4o",
        tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current temperature for a given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and country e.g. Bogotá, Colombia"
                    }
                },
                "required": [
                    "location"
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    },
            {
                "type": "function",
                "function": {
                    "name": "sum_numbers",
                    "description": "Sum the two given nums a given location.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "x": {
                                "type": "string",
                                "description": "number 1 to be added"
                            },
                            "y": {
                                "type": "string",
                                "description": "number 2 to be added"
                            },
                        },
                        "required": [
                            "x", 'y'
                        ],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }],
        tool_choice="required"
    )
    print(result)

if __name__ == "__main__":
    # function_call_with_guardrails()
    function_call_with_openai()