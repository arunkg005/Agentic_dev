import json
import logging
from config import call_llm

logger = logging.getLogger("NGO-Campaign-Copilot.Objectives")

_FALLBACK = None  # lazily built per-call


def generate_objectives(
    topic: str, audience: str, reach: int,
    api_key: str | None = None, provider: str = "Gemini (Google)",
) -> list[str]:
    """
    Generates 3–5 SMART objectives for the campaign.
    Falls back to sensible defaults on any API/parsing error.
    """
    logger.info("Generating objectives — Topic: %s, Audience: %s, Reach: %d", topic, audience, reach)

    prompt = (
        "You are an expert NGO campaign planner. Generate 3 to 5 SMART "
        "(Specific, Measurable, Achievable, Relevant, Time-bound) objectives.\n\n"
        f"Campaign details:\n"
        f"- Topic: {topic}\n"
        f"- Target Audience: {audience}\n"
        f"- Expected Reach: {reach} participants\n\n"
        "Objectives must be actionable and reflect the expected reach.\n\n"
        'Respond ONLY with JSON: {{"objectives": ["...", "..."]}}'
    )

    fallback = [
        f"Increase awareness of {topic} among {audience}.",
        f"Reach out to {reach} people via offline/online communication channels.",
        "Engage the target community to drive participation in campaign activities.",
    ]

    try:
        raw = call_llm(prompt, api_key=api_key, json_output=True, provider=provider)
        result = json.loads(raw)
        objectives = result.get("objectives")
        if not isinstance(objectives, list) or len(objectives) == 0:
            logger.warning("LLM returned empty or malformed objectives list; using fallback.")
            return fallback
        # Ensure every item is a string
        return [str(o) for o in objectives]
    except Exception as e:
        logger.error("Error generating objectives: %s", e)
        return fallback
