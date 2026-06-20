import json
import logging
from config import call_llm

logger = logging.getLogger("NGO-Campaign-Copilot.Risks")


def analyze_risks(
    topic: str, audience: str, duration: int, duration_unit: str,
    api_key: str | None = None, provider: str = "Gemini (Google)",
) -> list[dict]:
    """
    Identifies 3–5 operational risks and suggests practical mitigations.
    """
    duration_str = f"{duration} {duration_unit}"
    logger.info("Analyzing risks — Topic: %s, Audience: %s, Duration: %s", topic, audience, duration_str)

    prompt = (
        "You are an expert NGO risk manager. Identify 3 to 5 key operational risks.\n\n"
        f"Campaign details:\n"
        f"- Topic: {topic}\n"
        f"- Target Audience: {audience}\n"
        f"- Duration: {duration_str}\n\n"
        "For each risk, provide a practical, budget-friendly mitigation strategy.\n"
        "Focus on realistic risks: weather, low turnout, communication breakdowns, "
        "volunteer conflicts, material delays.\n\n"
        'Respond ONLY with JSON:\n'
        '{{"risks": [{{"risk":"...","mitigation":"..."}}]}}'
    )

    try:
        raw = call_llm(prompt, api_key=api_key, json_output=True, provider=provider)
        result = json.loads(raw)
        risks = result.get("risks")
        if not isinstance(risks, list) or len(risks) == 0:
            raise ValueError("Empty or malformed risks list from LLM.")
        # Defensive validation
        for r in risks:
            r.setdefault("risk", "Unknown Risk")
            r.setdefault("mitigation", "No mitigation specified.")
        return risks
    except Exception as e:
        logger.error("Error analyzing risks: %s", e)
        return [
            {
                "risk": "Low Turnout / Participant Attendance",
                "mitigation": "Promote across multiple channels (WhatsApp, flyers, posters) at least 5 days prior.",
            },
            {
                "risk": "Volunteer Dropouts",
                "mitigation": "Recruit 20% more volunteers than required as a standby pool.",
            },
            {
                "risk": "Material Availability",
                "mitigation": "Procure and verify all materials at least 2 days before execution.",
            },
        ]
