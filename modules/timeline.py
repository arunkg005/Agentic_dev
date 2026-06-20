import json
import logging
from config import call_llm

logger = logging.getLogger("NGO-Campaign-Copilot.Timeline")


def generate_timeline(
    duration: int, duration_unit: str, objectives: list[str],
    api_key: str | None = None, provider: str = "Gemini (Google)",
) -> list[dict]:
    """
    Generates a phased campaign timeline aligned with the objectives.
    Falls back to a sensible default on API/parsing errors.
    """
    duration_str = f"{duration} {duration_unit}"
    logger.info("Generating timeline — Duration: %s", duration_str)

    objectives_str = "\n".join(f"- {obj}" for obj in objectives)

    prompt = (
        f"You are an expert NGO campaign planner. Create a detailed activity timeline "
        f"for a campaign lasting {duration_str}.\n\n"
        f"Campaign objectives:\n{objectives_str}\n\n"
        f"Divide the timeline into logical phases for {duration_str} "
        "(e.g. days→stages, weeks→week-by-week, months→month-by-month).\n"
        "For each phase include a title, timeframe, and key activities.\n\n"
        'Respond ONLY with JSON:\n'
        '{{"timeline": [{{"phase": "...", "timeframe": "...", "activities": ["..."]}}]}}'
    )

    try:
        raw = call_llm(prompt, api_key=api_key, json_output=True, provider=provider)
        result = json.loads(raw)
        timeline = result.get("timeline")
        if not isinstance(timeline, list) or len(timeline) == 0:
            raise ValueError("Empty or malformed timeline list from LLM.")
        # Validate structure of each phase
        for phase in timeline:
            phase.setdefault("phase", "Unnamed Phase")
            phase.setdefault("timeframe", "")
            if not isinstance(phase.get("activities"), list):
                phase["activities"] = []
        return timeline
    except Exception as e:
        logger.error("Error generating timeline: %s", e)
        return _build_fallback(duration, duration_unit)


def _build_fallback(duration: int, duration_unit: str) -> list[dict]:
    """Produces a reasonable generic fallback timeline."""
    if duration_unit == "Weeks":
        return [
            {
                "phase": "Week 1: Preparation & Publicity",
                "timeframe": "Week 1",
                "activities": [
                    "Onboard and train core volunteer team.",
                    "Publish digital posters and kickstart online outreach.",
                    "Procure physical campaign collateral (posters, banners).",
                ],
            },
            {
                "phase": "Week 2: Execution & Closure",
                "timeframe": "Week 2",
                "activities": [
                    "Conduct target outreach events/workshops.",
                    "Perform street-level campaigns or community drives.",
                    "Collect participant feedback and compile final impact reports.",
                ],
            },
        ]
    elif duration_unit == "Months":
        phases = [
            {
                "phase": "Month 1: Mobilization & Planning",
                "timeframe": "Month 1",
                "activities": [
                    "Form partnerships and onboard volunteer cohorts.",
                    "Design outreach strategy and create event schedules.",
                ],
            },
            {
                "phase": "Month 2: Execution",
                "timeframe": "Month 2",
                "activities": ["Conduct core workshops, events, and awareness sessions."],
            },
            {
                "phase": "Month 3: Review & Handover",
                "timeframe": "Month 3",
                "activities": [
                    "Evaluate metrics and gather feedback.",
                    "Host volunteer appreciation meetups.",
                ],
            },
        ]
        return phases[: max(1, duration)]
    else:  # Days
        half = max(1, duration // 2)
        return [
            {
                "phase": "Phase 1: Setup & Warmup",
                "timeframe": f"Days 1–{half}",
                "activities": [
                    "Coordinate permissions and set up campaign booth/materials.",
                    "Inform the local community and distribute preliminary flyers.",
                ],
            },
            {
                "phase": "Phase 2: Main Event & Cleanup",
                "timeframe": f"Days {half + 1}–{duration}",
                "activities": [
                    "Conduct primary campaign activities.",
                    "Conclude the drive and run feedback surveys.",
                ],
            },
        ]
