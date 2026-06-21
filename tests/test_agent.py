import pytest
from unittest.mock import patch, MagicMock
from agent import run_campaign_planner
from models import CampaignPlanState

def test_run_campaign_planner_integration():
    with patch("agent.generate_objectives", return_value=["Obj1", "Obj2"]) as mock_obj, \
         patch("agent.generate_timeline", return_value=[{"phase": "1", "timeframe": "1", "activities": []}]) as mock_time, \
         patch("agent.estimate_resources", return_value={"calculated_volunteers": 5}) as mock_res, \
         patch("agent.plan_volunteers", return_value={"roles": []}) as mock_vol, \
         patch("agent.analyze_risks", return_value=[{"risk": "R1"}]) as mock_risk, \
         patch("agent.generate_metrics", return_value=[{"name": "M1"}]) as mock_met, \
         patch("agent.compile_campaign_plan", return_value=("MD", "path.md", "path.pdf", "path.docx")) as mock_comp:
         
         generator = run_campaign_planner(
             name="Test", topic="T", audience="A", budget=1000,
             duration=1, duration_unit="Weeks", reach=100,
             api_key="key", provider="prov"
         )
         
         events = list(generator)
         
         # Assert the final event has the generated outputs
         final_event = events[-1]
         assert final_event[0] == "Campaign plan compiled successfully! Download it below."
         assert final_event[1] == "MD"
         assert final_event[2] == {"md": "path.md", "pdf": "path.pdf", "docx": "path.docx"}
         
         # Assert compiler was called with the CampaignPlanState object
         mock_comp.assert_called_once()
         args, kwargs = mock_comp.call_args
         state = args[0]
         assert isinstance(state, CampaignPlanState)
         assert state.name == "Test"
         assert state.objectives == ["Obj1", "Obj2"]
         assert state.timeline == [{"phase": "1", "timeframe": "1", "activities": []}]
