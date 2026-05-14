import pytest
from unittest.mock import MagicMock
from core.Structs import AIBehavior, DecisionNode
from controllers.CharacterController import AIPriorityController
from tests.utils.entity_factory import create_dummy_character
from tests.utils.test_utils import create_test_battle_manager
from battle.BattleActions import AttackAction, GenerateFocusAction

def test_ai_priority_controller_targeting():
    node = DecisionNode(
        priority=10,
        required_state="Neutral",
        target_selector="any_enemy",
        filters=["lowest_hp"],
        action_id="SkillN1",
        next_state=None
    )
    behavior = AIBehavior("test_ai", "Neutral", [node])
    
    ctrl = AIPriorityController(behavior)
    actor = create_dummy_character(char_id="hero")
    actor.floating_focus = 100
    
    enemy1 = create_dummy_character(char_id="enemy1")
    enemy1.team = 1
    enemy1.current_hp = 50
    enemy2 = create_dummy_character(char_id="enemy2")
    enemy2.team = 1
    enemy2.current_hp = 10
    
    context = create_test_battle_manager()
    context.add_character(actor, ctrl)
    context.add_character(enemy1, MagicMock())
    context.add_character(enemy2, MagicMock())
    
    action = ctrl.choose_action(actor, context)
    
    assert isinstance(action, AttackAction)
    assert action.targets == [enemy2]

def test_ai_priority_state_transition():
    node1 = DecisionNode(
        priority=20,
        required_state="Neutral",
        target_selector="self",
        filters=["hp_lt_50"],
        action_id=None,
        next_state="Panic"
    )
    node2 = DecisionNode(
        priority=10,
        required_state="Neutral",
        target_selector="any_enemy",
        filters=[],
        action_id="attack_basic",
        next_state=None
    )
    node3 = DecisionNode(
        priority=30,
        required_state="Panic",
        target_selector="self",
        filters=[],
        action_id="GenerateFocus",
        next_state=None
    )
    behavior = AIBehavior("test_ai", "Neutral", [node1, node2, node3])
    
    ctrl = AIPriorityController(behavior)
    actor = create_dummy_character(char_id="hero")
    actor.current_hp = 40
    actor.max_hp = 100
    
    enemy1 = create_dummy_character(char_id="enemy1")
    enemy1.team = 1
    
    context = create_test_battle_manager()
    context.add_character(actor, ctrl)
    context.add_character(enemy1, MagicMock())
    
    action = ctrl.choose_action(actor, context)
    
    assert ctrl.current_state == "Panic"
    assert action.__class__.__name__ == "GenerateFocusAction"
