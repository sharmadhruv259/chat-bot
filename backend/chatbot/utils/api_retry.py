
"""Provide retry handling for temporary Groq and OpenAI API failures."""

import logging

import backoff
from groq import (
    APIConnectionError as GroqConnectionError,
    APITimeoutError as GroqTimeoutError,
    InternalServerError as GroqServerError,
    RateLimitError as GroqRateLimitError,
)
from openai import (
    APIConnectionError as OpenAIConnectionError,
    APITimeoutError as OpenAITimeoutError,
    InternalServerError as OpenAIServerError,
    RateLimitError as OpenAIRateLimitError,
)


logger = logging.getLogger(__name__)

RETRYABLE_ERRORS = (
    GroqConnectionError,
    GroqTimeoutError,
    GroqServerError,
    GroqRateLimitError,
    OpenAIConnectionError,
    OpenAITimeoutError,
    OpenAIServerError,
    OpenAIRateLimitError,
)


def log_retry(details: dict) -> None:
    """Log a temporary API failure before another attempt.

    Args:
        details (dict): Backoff event details.

    Returns:
        None: This function only writes a log entry.

    Raises:
        None.
    """
    logger.warning(
        "Retrying API request: function=%s attempt=%s wait=%.2fs",
        details["target"].__name__,
        details["tries"],
        details["wait"],
    )


def log_retry_exhausted(details: dict) -> None:
    """Log when an API operation exhausts its retry attempts.

    Args:
        details (dict): Backoff event details.

    Returns:
        None: This function only writes a log entry.

    Raises:
        None.
    """
    logger.error(
        "API retries exhausted: function=%s attempts=%s",
        details["target"].__name__,
        details["tries"],
    )


def retry_api_call(function):
    """Apply exponential backoff to transient API errors.

    Args:
        function (Callable): API request function to decorate.

    Returns:
        Callable: Wrapped function with retry handling.

    Raises:
        Exception: Original API exception after retries are exhausted.
    """
    decorator = backoff.on_exception(
        backoff.expo,
        RETRYABLE_ERRORS,
        max_tries=3,
        max_time=20,
        jitter=backoff.full_jitter,
        on_backoff=log_retry,
        on_giveup=log_retry_exhausted,
        raise_on_giveup=True,
    )

    return decorator(function)
