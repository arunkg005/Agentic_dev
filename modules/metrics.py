import json
import logging
from utils import safe_llm_execute

logger = logging.getLogger("NGO-Campaign-Copilot.Metrics")


def generate_metrics(
    topic: str, reach: int,
    api_key: str | None = None, provider: str = "Gemini (Google)",
) -> list[dict]:
    """
    Generates 4–6 measurable success metrics (KPIs) for the campaign.
    """
    logger.info("Generating metrics — Topic: %s, Reach: %d", topic, reach)

    prompt = (
        "You are an expert NGO impact assessor. Recommend 4 to 6 specific, measurable "
        "success metrics for a campaign.\n\n"
        f"Campaign details:\n"
        f"- Topic: {topic}\n"
        f"- Expected Reach: {reach} participants\n\n"
        "Include both output metrics (attendees, materials distributed) and outcome metrics "
        "(awareness change, survey scores).\n"
        "For each metric, provide a realistic target and a simple measurement method.\n\n"
        'Respond ONLY with JSON:\n'
        '{{"metrics": [{{"name":"...","target":"...","method":"..."}}]}}'
    )

    def run_fallback():
        return {"metrics": [
            {
                "name": "Direct Reach (Participants)",
                "target": f"Engage at least {int(reach * 0.8)} individuals directly.",
                "method": "Count sign-ins, attendance sheets, or registration logs.",
            },
            {
                "name": "Materials Distributed",
                "target": f"Distribute resources to {reach} people.",
                "method": "Track quantity printed vs. leftover post-campaign.",
            },
            {
                "name": "Community Feedback Rate",
                "target": "Collect feedback from at least 30 participants.",
                "method": "3-question WhatsApp or paper survey after events.",
            },
        ]}

    result = safe_llm_execute(prompt, run_fallback, api_key=api_key, provider=provider, json_output=True)

    metrics = result.get("metrics")
    if not isinstance(metrics, list) or len(metrics) == 0:
        logger.warning("Empty or malformed metrics list from LLM; using fallback.")
        return run_fallback()
        
    for m in metrics:
        if not isinstance(m, dict):
            continue
        m.setdefault("name", "Unnamed Metric")
        m.setdefault("target", "N/A")
        m.setdefault("method", "N/A")
    return [m for m in metrics if isinstance(m, dict)]
