import json
import logging
from utils import safe_llm_execute

logger = logging.getLogger("NGO-Campaign-Copilot.Resources")


def calculate_rules_resources(reach: int, budget: float) -> dict:
    """
    Pure rule-based calculations for volunteer count and flyer estimates.
    No LLM call — deterministic and instant.
    """
    if reach < 200:
        volunteers = 5
    elif reach <= 500:
        volunteers = 10
    else:
        volunteers = 20

    flyers_needed = int(reach * 0.4) if reach > 0 else 0

    return {"calculated_volunteers": volunteers, "suggested_flyers": flyers_needed}


def estimate_resources(
    topic: str, reach: int, budget: float,
    api_key: str | None = None, provider: str = "Gemini (Google)",
) -> dict:
    """
    Combines rule-based estimations with an LLM call to suggest physical/digital
    assets and a percentage-based budget distribution.
    """
    logger.info("Estimating resources — Topic: %s, Reach: %d, Budget: %.0f", topic, reach, budget)

    rules = calculate_rules_resources(reach, budget)
    vol_count = rules["calculated_volunteers"]
    flyers = rules["suggested_flyers"]

    prompt = (
        "You are an expert NGO campaign planner. Recommend resources and a budget allocation.\n\n"
        f"Campaign details:\n"
        f"- Topic: {topic}\n"
        f"- Expected Reach: {reach} participants\n"
        f"- Available Budget: {budget} INR\n"
        f"- Core Volunteer Force: {vol_count} (pre-calculated)\n"
        f"- Recommended flyers: {flyers} units (pre-calculated)\n\n"
        "Recommend:\n"
        "1. Physical materials with quantity and purpose.\n"
        "2. Digital tools/platforms with purposes.\n"
        "3. A percentage-based budget allocation summing to 100%.\n"
        "4. A short operational guideline.\n\n"
        "If budget is 0, focus on 100% free/organic channels.\n\n"
        'Respond ONLY with JSON:\n'
        '{{"physical_materials": [{{"item":"...","purpose":"...","suggested_quantity":"..."}}], '
        '"digital_resources": [{{"item":"...","purpose":"..."}}], '
        '"budget_allocation": [{{"category":"...","percentage":40,"amount_inr":2000}}], '
        '"operational_notes": "..."}}'
    )

    def run_fallback():
        return _build_fallback(vol_count, flyers, budget)

    result = safe_llm_execute(prompt, run_fallback, api_key=api_key, provider=provider, json_output=True)

    # Defensive defaults for every expected key
    result.setdefault("physical_materials", [])
    result.setdefault("digital_resources", [])
    result.setdefault("budget_allocation", [])
    result.setdefault("operational_notes", "")

    # Validate nested structures
    for item in result["physical_materials"]:
        item.setdefault("item", "Unknown Item")
        item.setdefault("purpose", "")
        item.setdefault("suggested_quantity", "N/A")
    for item in result["digital_resources"]:
        item.setdefault("item", "Unknown Tool")
        item.setdefault("purpose", "")
    for item in result["budget_allocation"]:
        item.setdefault("category", "Uncategorized")
        item.setdefault("percentage", 0)
        item.setdefault("amount_inr", 0)

    result["calculated_volunteers"] = vol_count
    return result


def _build_fallback(vol_count: int, flyers: int, budget: float) -> dict:
    """Deterministic fallback when the LLM call fails."""
    if budget > 0:
        alloc = [
            {"category": "Printing & Banners", "percentage": 40, "amount_inr": int(budget * 0.40)},
            {"category": "Volunteer Refreshments", "percentage": 30, "amount_inr": int(budget * 0.30)},
            {"category": "Transport & Logistics", "percentage": 20, "amount_inr": int(budget * 0.20)},
            {"category": "Miscellaneous", "percentage": 10, "amount_inr": int(budget * 0.10)},
        ]
    else:
        alloc = [{"category": "Self-Funded / Free Resources", "percentage": 100, "amount_inr": 0}]

    return {
        "calculated_volunteers": vol_count,
        "physical_materials": [
            {"item": "Handmade banners & posters", "purpose": "Visual display at event", "suggested_quantity": "2 banners"},
            {"item": "Printed flyers", "purpose": "Outreach distribution", "suggested_quantity": f"{flyers} flyers"},
        ],
        "digital_resources": [
            {"item": "WhatsApp Communities", "purpose": "Volunteer coordination"},
            {"item": "Instagram / Facebook", "purpose": "Digital flyer sharing"},
        ],
        "budget_allocation": alloc,
        "operational_notes": "Verify printing costs locally before locking the budget.",
    }
