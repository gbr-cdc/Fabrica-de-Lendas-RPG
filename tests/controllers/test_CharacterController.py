import pytest
from controllers.CharacterController import PvP1v1Controller
from tests.utils.entity_factory import create_dummy_character
from tests.utils.test_context import BattleTestContext
from battle.BattleActions import AttackAction

def test_pvp1v1_controller_no_target():
    ctrl = PvP1v1Controller()
    actor = create_dummy_character(char_id="hero")
    context = BattleTestContext(characters=[actor])
    
    with pytest.raises(RuntimeError) as excinfo:
        ctrl.choose_action(actor, context)
    assert "não conseguiu achar um alvo" in str(excinfo.value)

def test_pvp1v1_controller_chooses_basic_attack_when_no_focus():
    ctrl = PvP1v1Controller()
    actor = create_dummy_character(char_id="hero")
    actor.floating_focus = 0
    target = create_dummy_character(char_id="enemy")
    context = BattleTestContext(characters=[actor, target])
    
    action = ctrl.choose_action(actor, context)
    
    assert isinstance(action, AttackAction)
    assert action.template.id == "BasicAttack"
    assert action.targets == [target]

def test_pvp1v1_controller_chooses_skill_when_has_focus():
    ctrl = PvP1v1Controller()
    actor = create_dummy_character(char_id="hero")
    actor.floating_focus = 10
    target = create_dummy_character(char_id="enemy")
    context = BattleTestContext(characters=[actor, target])
    
    action = ctrl.choose_action(actor, context)
    
    assert isinstance(action, AttackAction)
    assert action.template.id == "SkillN1"
    assert action.targets == [target]

def test_pvp1v1_controller_with_action_load_chooses_basic_attack():
    # When action_load is provided (e.g. reaction or specific trigger), 
    # the controller logic currently always falls back to BasicAttack in PvP1v1Controller
    ctrl = PvP1v1Controller()
    actor = create_dummy_character(char_id="hero")
    target = create_dummy_character(char_id="enemy")
    context = BattleTestContext(characters=[actor, target])
    action_load = object() # Dummy non-None action_load
    
    action = ctrl.choose_action(actor, context, action_load)
    
    assert isinstance(action, AttackAction)
    assert action.template.id == "BasicAttack"
    assert action.targets == [target]

def test_pvp1v1_controller_reaction_always_true():
    ctrl = PvP1v1Controller()
    actor = create_dummy_character()
    context = BattleTestContext()
    action_load = object()
    
    assert ctrl.choose_reaction(actor, "any_id", action_load, context) is True
