import os
import logging
import markdown
from utils import safe_llm_execute
from models import CampaignPlanState
from exporters.pdf_exporter import compile_campaign_plan_pdf
from exporters.docx_exporter import compile_markdown_to_docx

logger = logging.getLogger("NGO-Campaign-Copilot.Compiler")


def generate_strategic_recommendations(
    campaign_summary: str,
    api_key: str | None = None, provider: str = "Gemini (Google)",
) -> str:
    """
    Calls the LLM to produce 3–4 high-level strategic recommendations
    tailored to the campaign context.
    """
    logger.info("Generating strategic recommendations...")
    prompt = (
        "You are a senior advisor for a large international NGO. "
        "Review this campaign plan summary:\n\n"
        f"{campaign_summary}\n\n"
        "Provide 3 to 4 high-value, practical strategic recommendations "
        "to ensure the campaign's success. Do not repeat details already in the summary. "
        "Write them as a simple markdown bullet list."
    )
    def run_fallback():
        return {"recommendations": [
            "**Focus on Local Engagement**: Build relationships with local schools or community centres early.",
            "**Optimise Communication**: Maintain a shared WhatsApp group for real-time volunteer coordination.",
            "**Document for Future**: Take photos/videos to demonstrate impact for future donor proposals."
        ]}

    # Note: we ask for JSON so we don't have to parse markdown heuristics
    prompt += "\nRespond ONLY with JSON: {\"recommendations\": [\"...\"]}"

    result = safe_llm_execute(prompt, run_fallback, api_key=api_key, provider=provider, json_output=True)
    
    recs = result.get("recommendations", [])
    if not isinstance(recs, list) or len(recs) == 0:
        return run_fallback()
        
    return "\n".join(f"- {str(item).strip().lstrip('*- ')}" for item in recs)


def compile_campaign_plan(
    state: CampaignPlanState
) -> tuple[str, str, str, str]:
    """
    Compiles every generated component into a single, professional Markdown report.
    Saves the file to the ``output/`` directory and returns (markdown_content, file_path).
    """
    logger.info("Compiling campaign plan for '%s'...", state.name)

    # --- Build markdown segments with safe .get() everywhere ---
    objectives_md = "\n".join(f"* {obj}" for obj in state.objectives)

    timeline_md = ""
    for idx, t in enumerate(state.timeline, 1):
        timeline_md += f"### {t.get('phase', f'Phase {idx}')} ({t.get('timeframe', '')})\n"
        for act in t.get("activities", []):
            timeline_md += f"- {act}\n"
        timeline_md += "\n"

    phys_md = "\n".join(
        f"| {p.get('item', '')} | {p.get('suggested_quantity', '')} | {p.get('purpose', '')} |"
        for p in state.resources.get("physical_materials", [])
    )
    digi_md = "\n".join(
        f"| {d.get('item', '')} | {d.get('purpose', '')} |"
        for d in state.resources.get("digital_resources", [])
    )
    budget_md = "\n".join(
        f"| {b.get('category', '')} | {b.get('percentage', 0)}% | INR {b.get('amount_inr', 0)} |"
        for b in state.resources.get("budget_allocation", [])
    )
    vol_md = "\n".join(
        f"| {r.get('role_name', '')} | {r.get('count', 0)} | {r.get('responsibilities', '')} |"
        for r in state.volunteers.get("roles", [])
    )
    risks_md = "\n".join(
        f"| {rk.get('risk', '')} | {rk.get('mitigation', '')} |"
        for rk in state.risks
    )
    metrics_md = "\n".join(
        f"| {m.get('name', '')} | {m.get('target', '')} | {m.get('method', '')} |"
        for m in state.metrics
    )

    vol_count = state.resources.get("calculated_volunteers", 0)

    # Strategic recommendations
    summary_ctx = (
        f"Campaign: {state.name}\nTopic: {state.topic}\nAudience: {state.audience}\n"
        f"Budget: INR {state.budget}\nReach: {state.reach}\n"
        f"Objectives: {', '.join(state.objectives[:2])}\nVolunteers: {vol_count}"
    )
    recommendations_md = generate_strategic_recommendations(summary_ctx, api_key=state.api_key, provider=state.provider)

    # --- Assemble final document ---
    markdown_content = f"""# NGO Campaign Execution Plan: {state.name}

## Campaign Overview
- **Topic / Focus**: {state.topic}
- **Target Audience**: {state.audience}
- **Campaign Duration**: {state.duration} {state.duration_unit}
- **Expected Reach**: {state.reach} participants
- **Projected Budget**: INR {state.budget}
- **Total Volunteer Workforce**: {vol_count} volunteers

---

## Objectives
{objectives_md}

---

## Execution Timeline

{timeline_md}
---

## Resource Requirements

### Physical Materials
| Material Item | Quantity | Purpose |
| :--- | :--- | :--- |
{phys_md}

### Digital Assets & Platforms
| Tool / Platform | Purpose |
| :--- | :--- |
{digi_md}

### Budget Allocation
| Expense Category | Allocation % | Estimated Cost |
| :--- | :---: | :---: |
{budget_md}

*Note: All cost estimates are preliminary and subject to local vendor quotes.*

---

## Volunteer Mobilization Plan
Distribution of roles for {vol_count} volunteers:

| Volunteer Role | Count | Core Responsibilities |
| :--- | :---: | :--- |
{vol_md}

**Coordination Tip**: *{state.volunteers.get('coordination_tips', 'N/A')}*

---

## Risk & Mitigation Assessment

| Identified Risk | Mitigation Strategy |
| :--- | :--- |
{risks_md}

---

## Success Metrics & Evaluation

| Metric | Target Value | Measurement Method |
| :--- | :--- | :--- |
{metrics_md}

---

## Strategic Recommendations
{recommendations_md}
"""

    # Save to file
    os.makedirs("output", exist_ok=True)
    safe_name = "".join(c if c.isalnum() else "_" for c in state.name.strip()).lower()
    # Guard against empty filenames
    if not safe_name:
        safe_name = "campaign"
    md_file_path = f"output/campaign_plan_{safe_name}.md"
    pdf_file_path = f"output/campaign_plan_{safe_name}.pdf"
    docx_file_path = f"output/campaign_plan_{safe_name}.docx"

    # 1. Save Markdown
    with open(md_file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    logger.info("Campaign plan saved to '%s'.", md_file_path)

    # 2. Save PDF
    html_body = markdown.markdown(markdown_content, extensions=['tables'])
    compile_campaign_plan_pdf(html_body, pdf_file_path)

    # 3. Save DOCX
    compile_markdown_to_docx(markdown_content, docx_file_path)

    return markdown_content, md_file_path, pdf_file_path, docx_file_path




def refine_campaign_plan(
    current_markdown: str,
    prompt: str,
    api_key: str | None = None,
    provider: str = "Gemini (Google)"
) -> tuple[str, str, str, str]:
    """
    Calls the LLM to refine an existing campaign plan based on a prompt.
    Regenerates Markdown, HTML, PDF, and DOCX files.
    Returns (refined_markdown, md_file_path, pdf_file_path, docx_file_path).
    """
    logger.info("Refining campaign plan with prompt: %s", prompt)
    
    # Strip any legacy footer line or legacy error messages from the markdown before sending to LLM
    import re
    cleaned_markdown = current_markdown.replace(
        "*Document generated by NGO Campaign Planning Copilot.*", ""
    )
    cleaned_markdown = re.sub(r'\*Refinement failed:.*?\*', '', cleaned_markdown, flags=re.DOTALL)
    cleaned_markdown = cleaned_markdown.rstrip().rstrip("-").rstrip()

    # Construct prompt
    llm_prompt = (
        "You are an expert AI Campaign Planning Assistant.\n"
        "Here is the current campaign execution plan (in Markdown format):\n\n"
        f"{cleaned_markdown}\n\n"
        "The user wants to refine/update this plan with the following request:\n"
        f"\"{prompt}\"\n\n"
        "Please provide the updated, complete campaign plan in Markdown format. "
        "Keep the exact same layout, header structure, table formats, and styling. "
        "Modify ONLY the sections that need changes based on the user's request. "
        "Output ONLY the markdown content. Do not include any introductory or concluding comments. "
        "Do NOT add any footer attribution lines like 'Document generated by...'."
    )
    
    try:
        refined_markdown = safe_llm_execute(llm_prompt, lambda: current_markdown, api_key=api_key, provider=provider, json_output=False)
        # Strip markdown code fences if the LLM wraps the output in them
        stripped = refined_markdown.strip()
        if stripped.startswith("```"):
            # Remove opening fence (e.g. ```markdown or ```)
            first_newline = stripped.find("\n")
            if first_newline != -1:
                stripped = stripped[first_newline + 1:]
            # Remove closing fence
            if stripped.rstrip().endswith("```"):
                stripped = stripped.rstrip()[:-3].rstrip()
            refined_markdown = stripped
    except Exception as e:
        logger.error("Error calling LLM for refinement: %s", e)
        raise e

    # Extract the campaign name to construct a safe filename
    campaign_name = "refined_campaign"
    for line in refined_markdown.split("\n")[:5]:
        if line.startswith("# NGO Campaign Execution Plan:"):
            campaign_name = line.replace("# NGO Campaign Execution Plan:", "").strip()
            break
            
    safe_name = "".join(c if c.isalnum() else "_" for c in campaign_name.strip()).lower()
    if not safe_name:
        safe_name = "campaign"
        
    os.makedirs("output", exist_ok=True)
    md_file_path = f"output/campaign_plan_{safe_name}.md"
    pdf_file_path = f"output/campaign_plan_{safe_name}.pdf"
    docx_file_path = f"output/campaign_plan_{safe_name}.docx"

    # 1. Save Markdown
    with open(md_file_path, "w", encoding="utf-8") as f:
        f.write(refined_markdown)

    # 2. Save PDF
    html_body = markdown.markdown(refined_markdown, extensions=['tables'])
    compile_campaign_plan_pdf(html_body, pdf_file_path)

    # 3. Save DOCX
    compile_markdown_to_docx(refined_markdown, docx_file_path)

    return refined_markdown, md_file_path, pdf_file_path, docx_file_path
