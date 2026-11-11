"""Provide reusable chatbot helper functions."""

from ..schemas import ChatMessage


def build_message_history(
    history: list[ChatMessage],
) -> list[dict[str, str]]:
    """Convert conversation history to Groq message format.

    Args:
        history (list[ChatMessage]): Previous messages.

    Returns:
        list[dict[str, str]]: Groq-compatible message dictionaries.

    Raises:
        None.
    """
    return [
        {"role": item.role, "content": item.content}
        for item in history
    ]