import re
import html
import logging
import time
import threading

logger = logging.getLogger("NGO-Campaign-Copilot.Security")

# ---------------------------------------------------------------------------
# Prompt injection detection
# ---------------------------------------------------------------------------

# Heuristic patterns that strongly indicate prompt injection attempts.
# These are checked case-insensitively against every user-supplied text field.
PROMPT_INJECTION_PATTERNS = [
    # Direct instruction overrides
    r"ignore\s+(?:all\s+)?(?:previous\s+)?(?:instructions|rules|guidelines)",
    r"bypass\s+(?:system\s+)?(?:rules|filters|safety)",
    r"override\s+(?:system\s+)?(?:prompt|instructions|rules)",
    r"disregard\s+(?:all\s+)?(?:previous\s+)?(?:instructions|rules)",
    # Prompt / secret leaking
    r"reveal\s+(?:your\s+)?(?:system\s+)?(?:prompt|instructions|rules)",
    r"show\s+(?:me\s+)?(?:your\s+)?(?:system\s+)?(?:prompt|instructions)",
    r"(?:output|print|display|return)\s+(?:the\s+)?(?:api|secret)\s*(?:key|token)",
    r"what\s+(?:is|are)\s+your\s+(?:system\s+)?(?:prompt|instructions)",
    # Role-play / identity hijacking
    r"you\s+are\s+now\s+(?:a|an|the)\b",
    r"act\s+as\s+(?:a|an|the)\b",
    r"pretend\s+(?:to\s+be|you\s+are)",
    r"simulate\s+(?:being|a)",
    # Instruction manipulation
    r"new\s+instruction",
    r"do\s+not\s+follow\s+(?:your\s+)?(?:previous\s+)?instructions",
    r"forget\s+(?:everything\s+)?(?:before\s+)?(?:this|above)",
    r"(?:system|hidden|secret)\s+instructions",
    r"jailbreak",
    r"system\s+override",
    r"(?:DAN|developer)\s+mode",
    # Code / markdown escape attempts
    r"```\s*(?:system|python|bash|exec)",
]

# Compile patterns once at module load for performance
_COMPILED_PATTERNS = [
    re.compile(pattern, re.IGNORECASE) for pattern in PROMPT_INJECTION_PATTERNS
]


def check_prompt_injection(text: str) -> bool:
    """
    Returns True if the text triggers any prompt injection pattern.
    """
    for pattern in _COMPILED_PATTERNS:
        if pattern.search(text):
            return True
    return False


# ---------------------------------------------------------------------------
# Input sanitization
# ---------------------------------------------------------------------------

def sanitize_input_text(text: str) -> str:
    """
    Cleans user text:
      1. Strips leading/trailing whitespace.
      2. Removes ASCII and Latin-1 control characters.
      3. Escapes HTML special characters to prevent XSS.
    """
    if not text:
        return ""
    cleaned = text.strip()
    # Remove control characters (C0, DEL, C1 range)
    cleaned = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', cleaned)
    # Re-strip in case control-char removal exposed new edge whitespace
    cleaned = cleaned.strip()
    # Escape HTML to neutralise <script>, <img onerror>, etc.
    cleaned = html.escape(cleaned)
    return cleaned


# ---------------------------------------------------------------------------
# Full input validation
# ---------------------------------------------------------------------------

def validate_campaign_inputs(
    name: str,
    topic: str,
    audience: str,
    budget: float,
    duration: int,
    duration_unit: str,
    reach: int,
) -> tuple[bool, str]:
    """
    Validates and sanitizes all user-supplied campaign inputs.
    Returns (is_valid: bool, error_message: str).
    An empty error_message means validation passed.
    """
    # --- Text fields ---
    fields = {
        "name": (sanitize_input_text(name), 1, 100),
        "topic": (sanitize_input_text(topic), 1, 250),
        "audience": (sanitize_input_text(audience), 1, 250),
    }

    for field_name, (value, min_len, max_len) in fields.items():
        if not value or len(value) < min_len:
            return False, f"Campaign {field_name} is required (minimum {min_len} character)."
        if len(value) > max_len:
            return False, f"Campaign {field_name} must be {max_len} characters or fewer."

        # Prompt injection check on raw and sanitized text
        if check_prompt_injection(value):
            logger.warning(
                "Prompt injection detected in field '%s'.", field_name
            )
            return False, f"Invalid input detected in campaign {field_name}. Please refine your description."

    # --- Numeric fields ---
    try:
        budget = float(budget)
    except (TypeError, ValueError):
        return False, "Budget must be a valid number."

    if budget < 0 or budget > 10_000_000:
        return False, "Budget must be between 0 and 10,000,000 (1 Crore)."

    try:
        reach = int(reach)
    except (TypeError, ValueError):
        return False, "Expected reach must be a valid integer."

    if reach < 1 or reach > 5_000_000:
        return False, "Expected reach must be between 1 and 5,000,000 participants."

    try:
        duration = int(duration)
    except (TypeError, ValueError):
        return False, "Duration must be a valid integer."

    if duration < 1:
        return False, "Duration must be at least 1."

    # --- Duration unit ---
    allowed_units = ("Days", "Weeks", "Months")
    if duration_unit not in allowed_units:
        return False, f"Duration unit must be one of: {', '.join(allowed_units)}."

    # Max-duration guard rails
    max_durations = {"Days": 365, "Weeks": 52, "Months": 12}
    cap = max_durations[duration_unit]
    if duration > cap:
        return False, f"Duration in {duration_unit.lower()} cannot exceed {cap}."

    return True, ""


# ---------------------------------------------------------------------------
# Simple in-memory rate limiter (per-session / IP is not available in Gradio
# free tier, so we use a global counter to protect the shared API key)
# ---------------------------------------------------------------------------

class RateLimiter:
    """
    Token-bucket rate limiter.
    Default: 5 generations per 60 seconds across all users.
    """

    def __init__(self, max_calls: int = 5, window_seconds: int = 60):
        self._max_calls = max_calls
        self._window = window_seconds
        self._timestamps: list[float] = []
        self._lock = threading.Lock()

    def allow(self) -> bool:
        now = time.time()
        with self._lock:
            # Prune expired timestamps
            self._timestamps = [t for t in self._timestamps if now - t < self._window]
            if len(self._timestamps) >= self._max_calls:
                return False
            self._timestamps.append(now)
            return True


# Global rate limiter instance
rate_limiter = RateLimiter(max_calls=5, window_seconds=60)
