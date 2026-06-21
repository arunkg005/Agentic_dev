import json
import asyncio
import markdown
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from agent import run_campaign_planner
from modules.compiler import refine_campaign_plan
import uvicorn
import os

app = FastAPI()

# Ensure output directory exists for static mounting
os.makedirs("output", exist_ok=True)
os.makedirs("static", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/output", StaticFiles(directory="output"), name="output")

@app.get("/")
def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/generate")
async def generate(request: Request):
    data = await request.json()
    name = data.get("name")
    topic = data.get("topic")
    audience = data.get("audience")
    budget = float(data.get("budget", 5000))
    duration = int(data.get("duration", 2))
    duration_unit = data.get("duration_unit", "Weeks")
    reach = int(data.get("reach", 250))
    
    # We do NOT read provider or api_key from the UI. 
    # It purely relies on the backend env variables and auto-fallback abstraction.
    
    async def ndjson_generator():
        try:
            
            # For streaming properly, we iterate the generator directly.
            # Note: since the LLM calls are synchronous and block, we'd ideally use run_in_executor
            # for each yield. But for simplicity in this local app, yielding directly works fine.
            generator = run_campaign_planner(
                name=name,
                topic=topic,
                audience=audience,
                budget=budget,
                duration=duration,
                duration_unit=duration_unit,
                reach=reach
            )
            
            for status, md_preview, file_path in generator:
                html_preview = ""
                if md_preview:
                    html_preview = markdown.markdown(md_preview, extensions=['tables'])
                
                payload = {
                    "status": status,
                    "html": html_preview,
                    "markdown": md_preview
                }
                if isinstance(file_path, dict):
                    payload["file_path"] = file_path.get("md")
                    payload["pdf_path"] = file_path.get("pdf")
                    payload["docx_path"] = file_path.get("docx")
                else:
                    payload["file_path"] = file_path
                    payload["pdf_path"] = None
                    payload["docx_path"] = None
                
                yield json.dumps(payload) + "\n"
                # Yield to the event loop
                await asyncio.sleep(0.01)
                
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"
            
    return StreamingResponse(ndjson_generator(), media_type="application/x-ndjson")

@app.post("/api/refine")
async def refine(request: Request):
    try:
        data = await request.json()
        current_markdown = data.get("markdown", "")
        prompt = data.get("prompt", "")
        
        # Sanitize and validate prompt against prompt injection
        from security import sanitize_input_text, check_prompt_injection
        prompt = sanitize_input_text(prompt)
        if check_prompt_injection(prompt):
            return {"error": "Invalid request detected. Security filter triggered."}
            
        refined_md, md_path, pdf_path, docx_path = refine_campaign_plan(
            current_markdown=current_markdown,
            prompt=prompt
        )
        
        html_preview = markdown.markdown(refined_md, extensions=['tables'])
        
        return {
            "markdown": refined_md,
            "html": html_preview,
            "file_path": md_path,
            "pdf_path": pdf_path,
            "docx_path": docx_path
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
