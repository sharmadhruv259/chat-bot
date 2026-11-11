
"""Initialize reusable API clients for chatbot services."""

from functools import lru_cache

from django.conf import settings
from groq import Groq
from openai import OpenAI


@lru_cache(maxsize=1)
def get_groq_client() -> Groq:
    """Initialize and cache the Groq API client.

    Args:
        None.

    Returns:
        Groq: Reusable Groq API client.

    Raises:
        ValueError: If the Groq API key is missing.
    """
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not configured.")

    return Groq(
        api_key=settings.GROQ_API_KEY,
        max_retries=0,    
    )


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    """Initialize and cache the OpenAI API client.

    Args:
        None.

    Returns:
        OpenAI: Reusable OpenAI API client.

    Raises:
        ValueError: If the OpenAI API key is missing.
    """
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not configured.")

    return OpenAI(
        api_key=settings.OPENAI_API_KEY,
        max_retries=0,
    )
