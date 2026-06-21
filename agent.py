import logging
from security import validate_campaign_inputs, rate_limiter, sanitize_input_text
from modules.objectives import generate_objectives
from modules.timeline import generate_timeline
from modules.resources import estimate_resources
from modules.volunteers import plan_volunteers
from modules.risks import analyze_risks
from modules.metrics import generate_metrics
from modules.compiler import compile_campaign_plan
from models import CampaignPlanState

logger = logging.getLogger("Campaign-Copilot.Agent")


def run_campaign_planner(
    name: str,
    topic: str,
    audience: str,
    budget: float,
    duration: int,
    duration_unit: str,
    reach: int,
    api_key: str | None = None,
    provider: str = "Gemini (Google)",
):
    """
    Orchestration generator that yields step-by-step progress messages
    followed by the final markdown content and download file path.

    Yields: (status_message, markdown_preview, download_file_path)

    ``api_key`` and ``provider`` are threaded through to every LLM call
    so each user session is fully isolated.
    """
    llm_kwargs = {"api_key": api_key, "provider": provider}
    logger.info("Starting campaign planner pipeline (provider=%s)...", provider)

    # --- Rate limiting ---
    if not rate_limiter.allow():
        yield (
            "Rate limit exceeded. Please wait 60 seconds before generating another plan.",
            "",
            None,
        )
        return

    # --- Step 1: Validation & Security ---
    name = sanitize_input_text(name)
    topic = sanitize_input_text(topic)
    audience = sanitize_input_text(audience)

    yield "Running input validation and security checks...", "", None
    is_valid, err_msg = validate_campaign_inputs(
        name, topic, audience, budget, duration, duration_unit, reach
    )
    if not is_valid:
        yield f"Validation Error: {err_msg}", "", None
        return

    state = CampaignPlanState(
        name=name, topic=topic, audience=audience, budget=budget,
        duration=duration, duration_unit=duration_unit, reach=reach,
        api_key=api_key, provider=provider
    )

    # --- Step 2: Objectives ---
    yield f"Step 1/6: Defining SMART campaign objectives ({provider})...", "", None
    state.objectives = generate_objectives(topic, audience, reach, **llm_kwargs)

    # --- Step 3: Timeline ---
    yield "Step 2/6: Structuring execution timeline...", "", None
    state.timeline = generate_timeline(duration, duration_unit, state.objectives, **llm_kwargs)

    # --- Step 4: Resources ---
    yield "Step 3/6: Estimating resources and budget allocation...", "", None
    state.resources = estimate_resources(topic, reach, budget, **llm_kwargs)
    vol_count = state.resources.get("calculated_volunteers", 5)

    # --- Step 5: Volunteers ---
    yield "Step 4/6: Coordinating volunteer role distribution...", "", None
    state.volunteers = plan_volunteers(topic, reach, vol_count, **llm_kwargs)

    # --- Step 6: Risks ---
    yield "Step 5/6: Formulating risk assessment & mitigation...", "", None
    state.risks = analyze_risks(topic, audience, duration, duration_unit, **llm_kwargs)

    # --- Step 7: Metrics ---
    yield "Step 6/6: Designing success indicators & KPIs...", "", None
    state.metrics = generate_metrics(topic, reach, **llm_kwargs)

    # --- Step 8: Compile ---
    yield "Compiling final campaign report...", "", None
    markdown_content, md_file_path, pdf_file_path, docx_file_path = compile_campaign_plan(state)

    yield "Campaign plan compiled successfully! Download it below.", markdown_content, {
        "md": md_file_path,
        "pdf": pdf_file_path,
        "docx": docx_file_path
    }
