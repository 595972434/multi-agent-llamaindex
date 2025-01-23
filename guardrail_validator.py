from typing import Optional, Callable, Dict

from guardrails.validators import (
    FailResult,
    PassResult,
    register_validator,
    ValidationResult,
    Validator,
)
from litellm import completion
from presidio_analyzer import AnalyzerEngine, PatternRecognizer




PROMPT = """
You are a helpful assistant.
Analyze the other messages provided and respond with a number between 0 and 100 and nothing else.
Do not output prose.
0 means the messages is not related to health.
100 means the messages is related to health.
If the message is not a sentence like json, return 100.
"""

@register_validator(name="toxic-language", data_type="string")
class TopicLimit(Validator):
    def __init__(self, threshold: int = 70, model='gpt-4o', on_fail: Optional[Callable] = None):
        super().__init__(on_fail=on_fail, threshold=threshold)
        self._threshold = threshold
        self._model = model

    def _llm_callable(self, messages):
        return completion(
            model=self._model,
            messages=messages,
            temperature=0.0,
        )

    def _validate(self, value: str, metadata: Dict) -> ValidationResult:
        messages = [
            {
                "role": "system",
                "content": PROMPT,
            },
            {
                "role": "user",
                "content": value,
            }
        ]

        score = int(self._llm_callable(messages).choices[0].message.content)
        if score > self._threshold:
            return PassResult()
        else:
            return FailResult(
                error_message=f"{value} failed validation. Score {score} is below threshold of {self._threshold}.",
            )


@register_validator(name="pii-detect", data_type="string")
def pii_detect(value, metadata: Dict) -> ValidationResult:
    customized_pii_list = ["apple", "banana", "orange", "watermelon"]
    customized_recognizer = PatternRecognizer(supported_entity="FRUIT", deny_list=customized_pii_list)
    analyzer = AnalyzerEngine()
    analyzer.registry.add_recognizer(customized_recognizer)
    # # Call analyzer to get results
    results = analyzer.analyze(text=value,
                               entities=["PERSON"],
                               # entities=["PHONE_NUMBER", "NRP", "LOCATION", "PERSON", "EMAIL_ADDRESS", "FRUIT"],
                               language='en')
    if len(results) > 0:
        return FailResult(
            error_message=f"User input contains PII: {', '.join([pii.entity_type for pii in results])}",
        )
    else:
        return PassResult()