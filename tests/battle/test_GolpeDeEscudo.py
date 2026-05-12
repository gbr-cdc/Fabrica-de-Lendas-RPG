import pytest
from unittest.mock import MagicMock
from battle.BattleActions import AttackAction
from core.Events import AttackLoad
from tests.utils.entity_factory import create_dummy_character
from tests.utils.test_utils import create_test_battle_manager

def test_golpe_de_escudo_mechanics():
    manager = create_test_battle_manager()
    dm = manager.data_service
    template = dm.get_action_template("GolpeEscudo")
    
    # 1. Test case: GdA > 3 triggers Atordoado
    style = dm.get_combat_style('Defensor')
    actor = create_dummy_character(char_id="actor", combat_style=style, attributes=[5,5,5])
    actor.floating_focus = template.focus_cost
    target = create_dummy_character(char_id="target", attributes=[5,5,5])
    target_hp = target.current_hp
    
    manager.add_character(actor, MagicMock())
    manager.add_character(target, MagicMock())
    
    manager.dice_service.schedule_result(10) # actor roll
    manager.dice_service.schedule_result(2)  # target roll
    
    actor = manager.get_next_actor()
    action = AttackAction(template, actor, [target], manager)
    load = manager.run_action(action)
    
    assert load.success is True
    assert any(effect.__class__.__name__ == "Atordoado" for effect, hooks in manager.active_status_effects[target.char_id])
    assert any("STATUS|" in h and "Atordoado" in h for h in load.history)
    assert target.current_hp == (target_hp - 5)
    assert actor.floating_focus == 0
    
    # 2. Test case: GdA <= 3 does NOT trigger Atordoado
    manager = create_test_battle_manager() # Clean context
    
    actor = create_dummy_character(char_id="actor", combat_style=style, attributes=[5,5,5])
    actor.floating_focus = template.focus_cost
    target = create_dummy_character(char_id="target", attributes=[5,5,5])
    target_hp = target.current_hp
    
    manager.add_character(actor, MagicMock())
    manager.add_character(target, MagicMock())
    
    manager.dice_service.schedule_result(5)
    manager.dice_service.schedule_result(4)
    
    actor = manager.get_next_actor()
    action = AttackAction(template, actor, [target], manager)
    load = manager.run_action(action)

    assert load.success is True
    assert not any(effect.__class__.__name__ == "Atordoado" for effect, hooks in manager.active_status_effects[target.char_id])
    assert not any("STATUS|" in h and "Atordoado" in h for h in load.history)
    assert target.current_hp == (target_hp - 5)
    assert actor.floating_focus == 0

def test_swap_atk_def_die_cleanup():
    actor = create_dummy_character()
    actor.base_atk_die = 6
    actor.base_def_die = 12
    
    manager = create_test_battle_manager()
    template = manager.get_template("GolpeEscudo")
    
    action = AttackAction(template, actor, [create_dummy_character()], manager)
    hooks = action.get_hooks()
    
    # During on_roll_modify
    from core.Enums import AttackType, RollState
    load = AttackLoad(character=actor, attack_type=AttackType.BASIC_ATTACK, attack_state=RollState.NEUTRAL, defense_state=RollState.NEUTRAL, atk_die=actor.atk_die)
    
    hooks['on_roll_modify'](load)
    assert load.atk_die == 12
