# Python Based Guardrails for Chatbot Responses


"""Provide deterministic input and output guardrail checks."""

import unicodedata

from ..constants import (
    BLOCKED_INPUT_MESSAGE,
    BLOCKED_OUTPUT_MESSAGE,
    MAX_INPUT_LENGTH,
    MAX_OUTPUT_LENGTH,
)
from ..schemas import GuardrailResult


def contains_disallowed_characters(text: str) -> bool:
    """Check whether text contains disallowed control characters.

    Args:
        text (str): Text to inspect.

    Returns:
        bool: True if a disallowed control character is found.

    Raises:
        None.
    """
    return any(
        unicodedata.category(character) == "Cc"
        and character not in "\n\r\t"
        for character in text
    )


def check_input(message: str) -> GuardrailResult:
    """Validate a user message using deterministic rules.

    Args:
        message (str): User message to validate.

    Returns:
        GuardrailResult: Input guardrail evaluation result.

    Raises:
        None.
    """
    if not message.strip():
        return GuardrailResult(
            allowed=False,
            guardrail="code",
            stage="input",
            category="empty_input",
            message=BLOCKED_INPUT_MESSAGE,
        )

    if len(message) > MAX_INPUT_LENGTH:
        return GuardrailResult(
            allowed=False,
            guardrail="code",
            stage="input",
            category="input_too_long",
            message=BLOCKED_INPUT_MESSAGE,
        )

    if contains_disallowed_characters(message):
        return GuardrailResult(
            allowed=False,
            guardrail="code",
            stage="input",
            category="invalid_characters",
            message=BLOCKED_INPUT_MESSAGE,
        )

    return GuardrailResult(
        allowed=True,
        guardrail="code",
        stage="input",
    )


def check_output(answer: str) -> GuardrailResult:
    """Validate a generated answer using deterministic rules.

    Args:
        answer (str): Generated chatbot response to validate.

    Returns:
        GuardrailResult: Output guardrail evaluation result.

    Raises:
        None.
    """
    if not answer.strip():
        return GuardrailResult(
            allowed=False,
            guardrail="code",
            stage="output",
            category="empty_output",
            message=BLOCKED_OUTPUT_MESSAGE,
        )

    if len(answer) > MAX_OUTPUT_LENGTH:
        return GuardrailResult(
            allowed=False,
            guardrail="code",
            stage="output",
            category="output_too_long",
            message=BLOCKED_OUTPUT_MESSAGE,
        )

    if contains_disallowed_characters(answer):
        return GuardrailResult(
            allowed=False,
            guardrail="code",
            stage="output",
            category="invalid_characters",
            message=BLOCKED_OUTPUT_MESSAGE,
        )

    return GuardrailResult(
        allowed=True,
        guardrail="code",
        stage="output",
    )
