
"""Execute enabled guardrails at their appropriate stages."""

from collections.abc import Callable

from ..schemas import GuardrailName, GuardrailResult, GuardrailStage
from . import code_guardrail, llm_guardrail, moderation_guardrail


GuardrailCheck = Callable[[str], GuardrailResult]

INPUT_CHECKS: dict[str, GuardrailCheck] = {
    "code": code_guardrail.check_input,
    "moderation": moderation_guardrail.check_input,
    "llm": llm_guardrail.check_input,
}

OUTPUT_CHECKS: dict[str, GuardrailCheck] = {
    "code": code_guardrail.check_output,
    "moderation": moderation_guardrail.check_output,
    "llm": llm_guardrail.check_output,
}

GUARDRAIL_ORDER = ("code", "moderation", "llm")


def run_guardrails(
    content: str,
    stage: GuardrailStage,
    enabled_guardrails: list[GuardrailName],
) -> GuardrailResult | None:
    """Run enabled guardrails and return the first blocking result.

    Args:
        content (str): Text to evaluate.
        stage (GuardrailStage): Input or output evaluation stage.
        enabled_guardrails (list[GuardrailName]): Enabled checks.

    Returns:
        GuardrailResult | None: Blocking result or None when all pass.

    Raises:
        ValueError: If the stage is unsupported.
        Exception: If an enabled guardrail evaluation fails.
    """
    if stage == "input":
        checks = INPUT_CHECKS
    elif stage == "output":
        checks = OUTPUT_CHECKS
    else:
        raise ValueError("Unsupported guardrail stage.")

    selected = set(enabled_guardrails)

    for name in GUARDRAIL_ORDER:
        if name not in selected:
            continue

        result = checks[name](content)

        if not result.allowed:
            return result

    return None
