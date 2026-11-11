
"""Generate Groq chatbot responses with optional safety checks."""

# import httpx
# from groq import InternalServerError

from django.conf import settings

from ..clients import get_groq_client
from ..constants import MAX_OUTPUT_TOKENS, SYSTEM_PROMPT, TEMPERATURE
from ..guardrails.orchestrator import run_guardrails
from ..schemas import ChatRequest, ChatResponse, GuardrailResult
from ..utils.helpers import build_message_history
from ..utils.api_retry import retry_api_call

def build_blocked_response(result: GuardrailResult) -> ChatResponse:
    """Build a response for content blocked by a guardrail.

    Args:
        result (GuardrailResult): Blocking guardrail result.

    Returns:
        ChatResponse: Response containing the blocking information.

    Raises:
        None.
    """
    return ChatResponse(
        answer=None,
        model=settings.GROQ_MODEL,
        blocked=True,
        guardrail_result=result,
    )


def generate_chat_response(request: ChatRequest) -> ChatResponse:
    """Generate a chatbot answer with input and output checks.

    Args:
        request (ChatRequest): Validated chatbot request.

    Returns:
        ChatResponse: Permitted answer or blocking information.

    Raises:
        ValueError: If the chatbot returns an empty answer.
        Exception: If an external API request fails.
    """
    input_result = run_guardrails(
        content=request.message,
        stage="input",
        enabled_guardrails=request.enabled_guardrails,
    )

    if input_result is not None:
        return build_blocked_response(input_result)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *build_message_history(request.history),
        {"role": "user", "content": request.message},
    ]

    response = request_chat_completion(messages)

    answer = response.choices[0].message.content

    if not answer:
        raise ValueError("Groq returned an empty response.")

    output_result = run_guardrails(
        content=answer,
        stage="output",
        enabled_guardrails=request.enabled_guardrails,
    )

    if output_result is not None:
        return build_blocked_response(output_result)

    return ChatResponse(
        answer=answer,
        model=settings.GROQ_MODEL,
    )


@retry_api_call
def request_chat_completion(messages: list[dict[str, str]]):
    """Send conversation messages to the Groq chatbot.

    Args:
        messages (list[dict[str, str]]): Conversation messages.

    Returns:
        ChatCompletion: Groq model response.

    Raises:
        Exception: If the API fails or retries are exhausted.
    """
    return get_groq_client().chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        max_completion_tokens=MAX_OUTPUT_TOKENS,
    )



# TESTING

# @retry_api_call
# def request_chat_completion(messages: list[dict[str, str]]):
#     """Simulate a Groq server failure to test backoff.

#     Args:
#         messages (list[dict[str, str]]): Conversation messages.

#     Returns:
#         ChatCompletion: Groq completion response if simulation is removed.

#     Raises:
#         InternalServerError: Simulated HTTP 500 failure.
#     """
#     request = httpx.Request(
#         "POST",
#         "https://api.groq.com/openai/v1/chat/completions",
#     )

#     response = httpx.Response(
#         status_code=500,
#         request=request,
#     )

#     raise InternalServerError(
#         "Simulated Groq server error",
#         response=response,
#         body=None,
#     )
