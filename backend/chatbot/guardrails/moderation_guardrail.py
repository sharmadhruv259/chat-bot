#Moderation for Chatbot Responses


"""Moderate chatbot inputs and outputs using the OpenAI API."""

from typing import Literal

from django.conf import settings

from ..clients import get_openai_client
from ..schemas import GuardrailResult
from ..utils.api_retry import retry_api_call


def evaluate_content(
    content: str,
    stage: Literal["input", "output"],
) -> GuardrailResult:
    """Evaluate text using OpenAI Moderation.

    Args:
        content (str): Text to evaluate.
        stage (Literal["input", "output"]): Evaluation stage.

    Returns:
        GuardrailResult: Moderation evaluation result.

    Raises:
        ValueError: If the content or API result is invalid.
        openai.OpenAIError: If the moderation API request fails.
    """
    if not content.strip():
        raise ValueError("Cannot moderate empty content.")

    client = get_openai_client()

    response = client.moderations.create(
        model=settings.OPENAI_MODERATION_MODEL,
        input=content,
    )

    if not response.results:
        raise ValueError("OpenAI returned no moderation results.")

    result = response.results[0]

    if not isinstance(result.flagged, bool):
        raise ValueError("OpenAI returned an invalid moderation decision.")

    if not result.flagged:
        return GuardrailResult(
            allowed=True,
            guardrail="moderation",
            stage=stage,
        )

    categories = result.categories.model_dump(by_alias=True)

    flagged_categories = [
        category
        for category, flagged in categories.items()
        if flagged is True
    ]

    category = (
        ", ".join(flagged_categories)
        if flagged_categories
        else "flagged_content"
    )

    return GuardrailResult(
        allowed=False,
        guardrail="moderation",
        stage=stage,
        category=category,
        message=(
            "This content was flagged by OpenAI Moderation."
        ),
    )


def check_input(message: str) -> GuardrailResult:
    """Moderate a user message before response generation.

    Args:
        message (str): User message to moderate.

    Returns:
        GuardrailResult: Input moderation result.

    Raises:
        ValueError: If the content or API result is invalid.
        openai.OpenAIError: If the moderation request fails.
    """
    return evaluate_content(message, "input")


def check_output(answer: str) -> GuardrailResult:
    """Moderate an assistant response before displaying it.

    Args:
        answer (str): Generated assistant response.

    Returns:
        GuardrailResult: Output moderation result.

    Raises:
        ValueError: If the content or API result is invalid.
        openai.OpenAIError: If the moderation request fails.
    """
    return evaluate_content(answer, "output")

@retry_api_call
def request_moderation(content: str):
    """Request an OpenAI Moderation classification.

    Args:
        content (str): Content to moderate.

    Returns:
        ModerationCreateResponse: OpenAI moderation result.

    Raises:
        Exception: If the API fails or retries are exhausted.
    """
    return get_openai_client().moderations.create(
        model=settings.OPENAI_MODERATION_MODEL,
        input=content,
    )
