from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class CampaignPlanState:
    # Inputs
    name: str
    topic: str
    audience: str
    budget: float
    duration: int
    duration_unit: str
    reach: int
    
    # Internal variables
    api_key: Optional[str] = None
    provider: str = "Gemini (Google)"

    # Generated Outputs
    objectives: List[str] = field(default_factory=list)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    resources: Dict[str, Any] = field(default_factory=dict)
    volunteers: Dict[str, Any] = field(default_factory=dict)
    risks: List[Dict[str, Any]] = field(default_factory=list)
    metrics: List[Dict[str, Any]] = field(default_factory=list)
