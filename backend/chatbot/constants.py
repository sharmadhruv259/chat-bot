"""Define shared chatbot configuration constants."""

SYSTEM_PROMPT = (
    "You are a helpful, friendly, and knowledgeable AI assistant. "
    "Provide clear and accurate answers to user questions. "
    "Maintain conversation context when responding to follow-up questions."
)

MAX_INPUT_LENGTH = 200
MAX_OUTPUT_LENGTH = 8000
MAX_HISTORY_MESSAGES = 50
MAX_OUTPUT_TOKENS = 512

TEMPERATURE = 0.7

BLOCKED_INPUT_MESSAGE = (
    "Your message was blocked by the configured guardrail."
)

BLOCKED_OUTPUT_MESSAGE = (
    "The generated response was blocked by the configured guardrail."
)
