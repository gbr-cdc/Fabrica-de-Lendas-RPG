from unittest.mock import MagicMock
from controllers import CharacterController
from _pytest import pytester_assertions
from _pytest import pytester_assertions
import pytest
from controllers.CharacterController import PvP1v1Controller
from tests.utils.entity_factory import create_dummy_character
from tests.utils.test_utils import create_test_battle_manager
from battle.BattleActions import AttackAction

def test_pvp1v1_controller_no_target():
    ctrl = PvP1v1Controller(MagicMock())
    actor = create_dummy_character(char_id="hero")
    context = create_test_battle_manager()
    context.add_character(actor, ctrl)
    
    with pytest.raises(RuntimeError) as excinfo:
        ctrl.choose_action(actor, context)
    assert "não conseguiu achar um alvo" in str(excinfo.value)

def test_pvp1v1_controller_chooses_basic_attack_when_no_focus():
    data_mock = MagicMock()
    template_mock = MagicMock()
    template_mock.nome = "Ataque Básico"
    template_mock.focus_cost = 5
    data_mock.get_action_template.return_value = template_mock
    ctrl = PvP1v1Controller(data_mock)
    actor = create_dummy_character(char_id="hero")
    actor.floating_focus = 0
    target = create_dummy_character(char_id="enemy")
    context = create_test_battle_manager()
    context.add_character(actor, ctrl)
    context.add_character(target, MagicMock())
    
    action = ctrl.choose_action(actor, context)
    
    assert isinstance(action, AttackAction)
    assert action.template.nome == "Ataque Básico"
    assert action.targets == [target]

def test_pvp1v1_controller_chooses_skill_when_has_focus():
    data_mock = MagicMock()
    template_mock = MagicMock()
    template_mock.nome = "Habilidade Nível 1"
    template_mock.focus_cost = 5
    data_mock.get_action_template.return_value = template_mock
    ctrl = PvP1v1Controller(data_mock)
    actor = create_dummy_character(char_id="hero")
    actor.floating_focus = 10
    target = create_dummy_character(char_id="enemy")
    context = create_test_battle_manager()
    context.add_character(actor, ctrl)
    context.add_character(target, MagicMock())
    
    action = ctrl.choose_action(actor, context)
    
    assert isinstance(action, AttackAction)
    assert action.template.nome == "Habilidade Nível 1"
    assert action.targets == [target]



def test_pvp1v1_controller_reaction_always_true():
    ctrl = PvP1v1Controller(MagicMock())
    actor = create_dummy_character()
    context = create_test_battle_manager()
    context.add_character(actor, ctrl)
    action_load = object()
    
    assert ctrl.choose_reaction(actor, "any_id", action_load, context) is True
