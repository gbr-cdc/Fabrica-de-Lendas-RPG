from unittest.mock import MagicMock
from controllers import CharacterController
from _pytest import pytester_assertions
from _pytest import pytester_assertions
import pytest
from controllers.CharacterController import AIPriorityController
from core.Structs import AIBehavior, DecisionNode
from tests.utils.entity_factory import create_dummy_character
from tests.utils.test_utils import create_test_battle_manager
from battle.BattleActions import AttackAction

def get_basic_agressive_behavior():
    return AIBehavior(
        id="basic_agressive",
        initial_state="Neutral",
        nodes=[
            DecisionNode(
                priority=2,
                required_state="Neutral",
                target_selector="any_enemy",
                filters=["lowest_hp"],
                action_id="SkillN1",
                next_state=None
            ),
            DecisionNode(
                priority=1,
                required_state="Neutral",
                target_selector="any_enemy",
                filters=["lowest_hp"],
                action_id="Attack",
                next_state=None
            )
        ]
    )

def test_ai_priority_controller_no_target():
    ctrl = AIPriorityController(get_basic_agressive_behavior(), MagicMock())
    actor = create_dummy_character(char_id="hero")
    context = create_test_battle_manager()
    context.add_character(actor, ctrl)
    
    # AIPriorityController handles no targets by returning WaitAction
    from battle.BattleActions import WaitAction
    action = ctrl.choose_action(actor, context)
    assert isinstance(action, WaitAction)

def test_ai_priority_controller_chooses_basic_attack_when_no_focus():
    data_mock = MagicMock()
    template_mock = MagicMock()
    template_mock.nome = "Habilidade Nível 1"
    template_mock.focus_cost = 5
    data_mock.get_action_template.return_value = template_mock
    data_mock.list_action_templates.return_value = ["SkillN1"]
    
    ctrl = AIPriorityController(get_basic_agressive_behavior(), data_mock)
    actor = create_dummy_character(char_id="hero")
    actor.floating_focus = 0
    target = create_dummy_character(char_id="enemy")
    target.team = 2 # Ensure it's an enemy
    context = create_test_battle_manager()
    context.add_character(actor, ctrl)
    context.add_character(target, MagicMock())
    
    action = ctrl.choose_action(actor, context)
    
    assert isinstance(action, AttackAction)
    assert action.template.nome == "Ataque Básico"
    assert action.targets == [target]

def test_ai_priority_controller_chooses_skill_when_has_focus():
    data_mock = MagicMock()
    template_mock = MagicMock()
    template_mock.nome = "Habilidade Nível 1"
    template_mock.focus_cost = 5
    data_mock.get_action_template.return_value = template_mock
    data_mock.list_action_templates.return_value = ["SkillN1"]
    
    ctrl = AIPriorityController(get_basic_agressive_behavior(), data_mock)
    actor = create_dummy_character(char_id="hero")
    actor.floating_focus = 10
    target = create_dummy_character(char_id="enemy")
    target.team = 2 # Ensure it's an enemy
    context = create_test_battle_manager()
    context.add_character(actor, ctrl)
    context.add_character(target, MagicMock())
    
    action = ctrl.choose_action(actor, context)
    
    assert isinstance(action, AttackAction)
    assert action.template.nome == "Habilidade Nível 1"
    assert action.targets == [target]



def test_ai_priority_controller_reaction_always_true():
    ctrl = AIPriorityController(MagicMock(), MagicMock())
    actor = create_dummy_character()
    context = create_test_battle_manager()
    context.add_character(actor, ctrl)
    action_load = object()
    
    assert ctrl.choose_reaction(actor, "any_id", action_load, context) is True
