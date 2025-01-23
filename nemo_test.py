import os

from nemoguardrails import LLMRails, RailsConfig
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()
# Load a guardrails configuration from the specified path.
    os.environ["OPENAI_API_KEY"] = os.getenv("API_KEY")
    os.environ["OPENAI_API_BASE"] = os.getenv("API_BASE")
    config = RailsConfig.from_path("./guardrail_config")
    rails = LLMRails(config)
    tools = [{
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
    completion = rails.generate(
        messages=[{"role": "user", "content": "calculate 1+2?"}],
        # tools=tools
    )
    print(completion)