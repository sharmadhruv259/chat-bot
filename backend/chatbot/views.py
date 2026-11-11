
"""Handle chatbot API requests and external API errors."""

import json
import logging

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST
from groq import (
    APIConnectionError as GroqConnectionError,
    APITimeoutError as GroqTimeoutError,
    AuthenticationError as GroqAuthenticationError,
    BadRequestError as GroqBadRequestError,
    InternalServerError as GroqServerError,
    RateLimitError as GroqRateLimitError,
)
from openai import (
    APIConnectionError as OpenAIConnectionError,
    APITimeoutError as OpenAITimeoutError,
    AuthenticationError as OpenAIAuthenticationError,
    BadRequestError as OpenAIBadRequestError,
    InternalServerError as OpenAIServerError,
    RateLimitError as OpenAIRateLimitError,
)
from pydantic import ValidationError

from .schemas import ChatRequest
from .services.chat_service import generate_chat_response


logger = logging.getLogger(__name__)



@require_POST
def chat_view(request: HttpRequest) -> JsonResponse:
    """Validate a chatbot request and handle API errors.

    Args:
        request (HttpRequest): Incoming Django HTTP request.

    Returns:
        JsonResponse: Chat answer, guardrail result, or error response.

    Raises:
        None: Exceptions are handled and returned as JSON responses.
    """
    try:
        payload = json.loads(request.body)
        chat_request = ChatRequest.model_validate(payload)

    except (ValueError, ValidationError):
        return JsonResponse(
            {
                "answer": None,
                "blocked": False,
                "error": "Invalid request payload.",
            },
            status=400,
        )

    try:
        result = generate_chat_response(chat_request)

    except (GroqRateLimitError, OpenAIRateLimitError):
        logger.exception("API rate limit exceeded after retries.")

        return JsonResponse(
            {
                "answer": None,
                "model": settings.GROQ_MODEL,
                "blocked": False,
                "error": (
                    "The AI service is currently rate-limited. "
                    "Please try again later."
                ),
            },
            status=429,
        )

    except (GroqAuthenticationError, OpenAIAuthenticationError):
        logger.exception("External API authentication failed.")

        return JsonResponse(
            {
                "answer": None,
                "model": settings.GROQ_MODEL,
                "blocked": False,
                "error": (
                    "The AI service authentication failed. "
                    "Please contact the administrator."
                ),
            },
            status=503,
        )

    except (GroqBadRequestError, OpenAIBadRequestError):
        logger.exception("External API rejected the request.")

        return JsonResponse(
            {
                "answer": None,
                "model": settings.GROQ_MODEL,
                "blocked": False,
                "error": (
                    "The AI service could not process this request."
                ),
            },
            status=502,
        )

    except (
        GroqConnectionError,
        GroqTimeoutError,
        GroqServerError,
        OpenAIConnectionError,
        OpenAITimeoutError,
        OpenAIServerError,
    ):
        logger.exception(
            "External API unavailable after retry attempts."
        )

        return JsonResponse(
            {
                "answer": None,
                "model": settings.GROQ_MODEL,
                "blocked": False,
                "error": (
                    "The AI service is temporarily unavailable. "
                    "Please try again."
                ),
            },
            status=503,
        )

    except Exception:
        logger.exception("Unexpected chatbot or guardrail failure.")

        return JsonResponse(
            {
                "answer": None,
                "model": settings.GROQ_MODEL,
                "blocked": False,
                "error": (
                    "The chatbot or safety check could not complete. "
                    "Please try again."
                ),
            },
            status=503,
        )

    return JsonResponse(result.model_dump())
