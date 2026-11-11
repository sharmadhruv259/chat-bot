
"""Define schemas for chatbot requests, responses, and guardrails."""

from typing import Literal

from pydantic import BaseModel, Field

from .constants import MAX_HISTORY_MESSAGES, MAX_INPUT_LENGTH


GuardrailName = Literal["code", "llm", "moderation"]
GuardrailStage = Literal["input", "output"]


class ChatMessage(BaseModel):
    """Represent one conversation message.

    Attributes:
        role (Literal["user", "assistant"]): Message author.
        content (str): Message content.

    Functions:
        None.
    """

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=MAX_INPUT_LENGTH)


class ChatRequest(BaseModel):
    """Represent an incoming chatbot request.

    Attributes:
        message (str): Current user message.
        history (list[ChatMessage]): Previous conversation messages.
        enabled_guardrails (list[GuardrailName]): Selected guardrails.

    Functions:
        None.
    """

    message: str = Field(min_length=1, max_length=MAX_INPUT_LENGTH)
    history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=MAX_HISTORY_MESSAGES,
    )
    enabled_guardrails: list[GuardrailName] = Field(
        default_factory=list,
    )


class GuardrailResult(BaseModel):
    """Represent the result of a safety evaluation.

    Attributes:
        allowed (bool): Whether the content passed the check.
        guardrail (str): Name of the guardrail.
        stage (GuardrailStage): Input or output stage.
        category (str | None): Detected issue category.
        message (str | None): Safe user-facing message.

    Functions:
        None.
    """

    allowed: bool
    guardrail: str
    stage: GuardrailStage
    category: str | None = None
    message: str | None = None


class ChatResponse(BaseModel):
    """Represent the chatbot API response.

    Attributes:
        answer (str | None): Allowed assistant answer.
        model (str): Main Groq model identifier.
        blocked (bool): Whether a guardrail blocked content.
        guardrail_result (GuardrailResult | None): Blocking check result.
        error (str | None): Technical error description.

    Functions:
        None.
    """

    answer: str | None = None
    model: str
    blocked: bool = False
    guardrail_result: GuardrailResult | None = None
    error: str | None = None
