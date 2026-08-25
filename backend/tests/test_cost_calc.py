import pytest
from app.services.cost_calculator import IRCCostCalculator

def test_pothole_cost_calculation():
    # 16.4 cm pothole crater
    metrics = IRCCostCalculator.calculate_repair_metrics(depth_cm=16.4, estimated_diameter_m=1.2, defect_type="POTHOLE")
    
    assert metrics["depth_cm"] == 16.4
    assert metrics["volume_m3"] > 0.1
    assert metrics["tonnage_mt"] >= 0.5
    assert metrics["estimated_cost_inr"] > 4000.0

def test_waterlogging_adjustment():
    pothole_metrics = IRCCostCalculator.calculate_repair_metrics(depth_cm=10.0, defect_type="POTHOLE")
    waterlog_metrics = IRCCostCalculator.calculate_repair_metrics(depth_cm=10.0, defect_type="WATERLOGGED_SHOULDER")
    
    # Waterlogged area footprint should require more material
    assert waterlog_metrics["volume_m3"] > pothole_metrics["volume_m3"]
    assert waterlog_metrics["estimated_cost_inr"] > pothole_metrics["estimated_cost_inr"]

def test_minimum_tonnage_floor():
    # Very shallow defect (1 cm) should still satisfy minimum 0.5 MT dispatch
    metrics = IRCCostCalculator.calculate_repair_metrics(depth_cm=1.0)
    assert metrics["tonnage_mt"] >= 0.5
