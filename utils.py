import json
import logging
from typing import Callable, Any, Optional
from config import call_llm

logger = logging.getLogger("NGO-Campaign-Copilot.Utils")

def safe_llm_execute(
    prompt: str,
    fallback_fn: Callable[[], Any],
    api_key: Optional[str] = None,
    provider: str = "Gemini (Google)",
    json_output: bool = True
) -> Any:
    """
    Safely executes an LLM call. If it fails or JSON parsing fails,
    logs the error and invokes the fallback function.
    """
    try:
        raw = call_llm(prompt, api_key=api_key, json_output=json_output, provider=provider)
        if json_output:
            return json.loads(raw)
        return raw
    except Exception as e:
        err_str = str(e)
        err_str_lower = err_str.lower()
        if "429" in err_str_lower or "rate limit" in err_str_lower or "quota" in err_str_lower:
            raise RuntimeError("We are sorry, we hit the API rate limit. Please try again later.")
            
        logger.error("LLM execution failed: %s. Triggering fallback.", e)
        return fallback_fn()
