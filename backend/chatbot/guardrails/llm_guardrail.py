
"""Evaluate chatbot inputs and outputs using a Groq safety model."""

import json

from django.conf import settings

from ..clients import get_groq_client
from ..prompts.safety_policy import SAFETY_POLICY
from ..schemas import GuardrailResult
from ..utils.api_retry import retry_api_call


@retry_api_call
def request_safety_completion(messages: list[dict[str, str]]):
    """Request a safety classification from Groq.

    Args:
        messages (list[dict[str, str]]): Safety policy and content.

    Returns:
        ChatCompletion: Groq safety-model response.

    Raises:
        Exception: If the API fails or retries are exhausted.
    """
    return get_groq_client().chat.completions.create(
        model=settings.GROQ_GUARDRAIL_MODEL,
        messages=messages,
        temperature=0,
        max_completion_tokens=256,
    )


def evaluate_content(content: str, stage: str) -> GuardrailResult:
    """Evaluate text against the chatbot safety policy.

    Args:
        content (str): User input or generated assistant response.
        stage (str): Input or output evaluation stage.

    Returns:
        GuardrailResult: Safety evaluation result.

    Raises:
        ValueError: If the safety model returns an invalid result.
        Exception: If the Groq API request fails.
    """
    response = request_safety_completion(
        [
            {"role": "system", "content": SAFETY_POLICY},
            {
                "role": "user",
                "content": json.dumps(
                    {"stage": stage, "text": content}
                ),
            },
        ]
    )

    response_text = response.choices[0].message.content

    if not response_text:
        raise ValueError("The safety model returned an empty response.")

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError as error:
        raise ValueError(
            "The safety model returned invalid JSON."
        ) from error

    if not isinstance(result, dict):
        raise ValueError(
            "The safety model returned an invalid result."
        )

    if type(result.get("allowed")) is not bool:
        raise ValueError(
            "The safety model returned an invalid decision."
        )

    category = result.get("category")

    if category is not None and not isinstance(category, str):
        raise ValueError(
            "The safety model returned an invalid category."
        )

    allowed = result["allowed"]

    return GuardrailResult(
        allowed=allowed,
        guardrail="llm",
        stage=stage,
        category=category,
        message=(
            None
            if allowed
            else "This content was blocked by the LLM safety guardrail."
        ),
    )


def check_input(message: str) -> GuardrailResult:
    """Evaluate a user message using the LLM safety guardrail.

    Args:
        message (str): User message to evaluate.

    Returns:
        GuardrailResult: Input safety evaluation result.

    Raises:
        ValueError: If the model response is invalid.
        Exception: If the Groq API request fails.
    """
    return evaluate_content(message, "input")


def check_output(answer: str) -> GuardrailResult:
    """Evaluate a generated answer using the LLM safety guardrail.

    Args:
        answer (str): Generated assistant response to evaluate.

    Returns:
        GuardrailResult: Output safety evaluation result.

    Raises:
        ValueError: If the model response is invalid.
        Exception: If the Groq API request fails.
    """
    return evaluate_content(answer, "output")
