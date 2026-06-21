import pytest
from modules.resources import calculate_rules_resources

def test_calculate_rules_resources_low_reach():
    res = calculate_rules_resources(reach=150, budget=1000)
    assert res["calculated_volunteers"] == 5
    assert res["suggested_flyers"] == 60

def test_calculate_rules_resources_medium_reach():
    res = calculate_rules_resources(reach=300, budget=1000)
    assert res["calculated_volunteers"] == 10
    assert res["suggested_flyers"] == 120

def test_calculate_rules_resources_high_reach():
    res = calculate_rules_resources(reach=1000, budget=5000)
    assert res["calculated_volunteers"] == 20
    assert res["suggested_flyers"] == 400

def test_calculate_rules_resources_zero_reach():
    res = calculate_rules_resources(reach=0, budget=1000)
    assert res["calculated_volunteers"] == 5
    assert res["suggested_flyers"] == 0
