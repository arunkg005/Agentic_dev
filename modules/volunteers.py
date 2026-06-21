import json
import logging
from utils import safe_llm_execute

logger = logging.getLogger("NGO-Campaign-Copilot.Volunteers")


def plan_volunteers(
    topic: str, reach: int, total_volunteers: int,
    api_key: str | None = None, provider: str = "Gemini (Google)",
) -> dict:
    """
    Suggests volunteer role allocation summing exactly to total_volunteers.
    Includes a post-processing correction if the LLM gets the count wrong.
    """
    logger.info(
        "Planning volunteers — Topic: %s, Reach: %d, Total: %d",
        topic, reach, total_volunteers,
    )

    prompt = (
        "You are an expert NGO coordinator. Design a volunteer role distribution.\n\n"
        f"Campaign details:\n"
        f"- Topic: {topic}\n"
        f"- Expected Reach: {reach} participants\n"
        f"- Total Volunteers: {total_volunteers}\n\n"
        f"Distribute EXACTLY {total_volunteers} volunteers across logical roles.\n"
        "Give each role a name, count, and responsibilities.\n\n"
        'Respond ONLY with JSON:\n'
        '{{"roles": [{{"role_name":"...","count":2,"responsibilities":"..."}}], '
        '"coordination_tips": "..."}}'
    )

    def run_fallback():
        return _build_fallback(total_volunteers)

    result = safe_llm_execute(prompt, run_fallback, api_key=api_key, provider=provider, json_output=True)

    roles = result.get("roles")
    if not isinstance(roles, list) or len(roles) == 0:
        logger.warning("Empty or malformed roles list from LLM; using fallback.")
        return run_fallback()

    # Validate and coerce nested structure
    for role in roles:
        if not isinstance(role, dict):
            continue
        role.setdefault("role_name", "Unnamed Role")
        role.setdefault("responsibilities", "")
        try:
            role["count"] = int(role.get("count", 1))
        except (TypeError, ValueError):
            role["count"] = 1

    # Fix count mismatch
    roles_list = [r for r in roles if isinstance(r, dict)]
    assigned = sum(r.get("count", 0) for r in roles_list)
    if assigned != total_volunteers and roles_list:
        logger.warning(
            "Volunteer count mismatch: expected %d, got %d. Correcting.",
            total_volunteers, assigned,
        )
        _correct_volunteer_counts(roles_list, total_volunteers, assigned)

    result["roles"] = roles_list
    result.setdefault("coordination_tips", "")
    return result


def _correct_volunteer_counts(
    roles: list[dict], target: int, current: int
) -> None:
    """Adjusts the largest adjustable role to match the target total (in-place)."""
    diff = target - current
    # Try to find a field/outreach role first, otherwise use the last one
    adjustable = None
    for r in roles:
        name_lower = r["role_name"].lower()
        if "field" in name_lower or "outreach" in name_lower:
            adjustable = r
            break
    if not adjustable:
        adjustable = roles[-1]

    new_count = adjustable["count"] + diff
    adjustable["count"] = max(1, new_count)


def _build_fallback(total_volunteers: int) -> dict:
    lead = 1
    support = max(1, total_volunteers // 5)
    field = max(1, total_volunteers - lead - support)
    return {
        "roles": [
            {
                "role_name": "Campaign Lead",
                "count": lead,
                "responsibilities": "Coordinates planning, timeline tracking, and is primary POC.",
            },
            {
                "role_name": "Logistics & Material Coordinator",
                "count": support,
                "responsibilities": "Handles procurement, volunteer refreshments, and safety.",
            },
            {
                "role_name": "Field & Outreach Volunteers",
                "count": field,
                "responsibilities": "Community outreach, flyer distribution, and feedback collection.",
            },
        ],
        "coordination_tips": "Conduct a 15-minute briefing before kick-off to align roles and safety.",
    }
