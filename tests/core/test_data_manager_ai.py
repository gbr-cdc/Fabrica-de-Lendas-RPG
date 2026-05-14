import pytest
import json
from core.DataManager import DataManager
from core.Structs import DecisionNode, AIBehavior

def test_ai_behavior_instantiation():
    node = DecisionNode(
        priority=10,
        required_state="Neutral",
        target_selector="any_enemy",
        filters=["hp_lt_50"],
        action_id="attack_basic",
        next_state="Aggressive",
        parameters={"x": 1}
    )
    behavior = AIBehavior(
        id="test_behavior",
        initial_state="Neutral",
        nodes=[node]
    )
    assert behavior.id == "test_behavior"
    assert behavior.nodes[0].priority == 10

def test_data_manager_ai_loading(tmp_path):
    # Setup mock JSON
    mock_data = {
        "test_behavior": {
            "id": "test_behavior",
            "initial_state": "Neutral",
            "nodes": [
                {
                    "priority": 10,
                    "required_state": "Neutral",
                    "target_selector": "any_enemy",
                    "filters": ["hp_lt_50"],
                    "action_id": "attack_basic",
                    "next_state": "Aggressive",
                    "parameters": {"x": 1}
                }
            ]
        }
    }
    
    file_path = tmp_path / "ai_behaviors.json"
    with open(file_path, "w") as f:
        json.dump(mock_data, f)
        
    dm = DataManager()
    dm.load_ai_behaviors(str(file_path))
    
    behavior = dm.get_ai_behavior("test_behavior")
    assert isinstance(behavior, AIBehavior)
    assert behavior.id == "test_behavior"
    assert behavior.initial_state == "Neutral"
    assert len(behavior.nodes) == 1
    assert behavior.nodes[0].priority == 10
    assert behavior.nodes[0].action_id == "attack_basic"
