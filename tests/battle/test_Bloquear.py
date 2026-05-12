import pytest
from unittest.mock import MagicMock
from tests.utils.test_utils import create_test_battle_manager
from tests.utils.entity_factory import create_dummy_character
from battle.BattleActions import AttackAction

def test_bloquear_reaction_trigger():
    """
    Test that Bloquear correctly triggers a defensive reaction using focus.
    """
    manager = create_test_battle_manager()
    defensor = create_dummy_character(char_id="defensor")
    defensor.passive_abilities.append("Bloquear")
    defensor.floating_focus = 10
    
    attacker = create_dummy_character(char_id="attacker")
    
    ctrl_defensor = MagicMock()
    ctrl_defensor.choose_reaction.return_value = True
    
    manager.add_character(defensor, ctrl_defensor, start_tick=1000)
    manager.add_character(attacker, MagicMock(), start_tick=1000)
    
    manager.set_tick(attacker, 0)
    actor = manager.get_next_actor()
    
    # 10 (atk), 5 (def), 3 (bloquear d4)
    manager.dice_service.queue.clear()
    manager.dice_service.schedule_result(10)
    manager.dice_service.schedule_result(5)
    manager.dice_service.schedule_result(3)
    
    action = AttackAction(None, actor, [defensor], manager)
    load = manager.run_action(action)
    
    assert any("PASSIVE|Bloquear|defensor" in h for h in load.history)
    assert any("ATK_LOAD|gda|-3|" in h for h in load.history)
    assert defensor.floating_focus == 8

def test_bloquear_counter_bonus():
    """
    Test the counter-bonus mechanism: +1 BDA on the next attack against the same target.
    """
    manager = create_test_battle_manager()
    defensor = create_dummy_character(char_id="defensor")
    defensor.passive_abilities.append("Bloquear")
    defensor.floating_focus = 10
    
    attacker = create_dummy_character(char_id="attacker")
    
    ctrl_defensor = MagicMock()
    ctrl_defensor.choose_reaction.return_value = True
    
    manager.add_character(defensor, ctrl_defensor, start_tick=1000)
    manager.add_character(attacker, MagicMock(), start_tick=1000)
    
    # 1. Attacker attacks defensor
    manager.set_tick(attacker, 0)
    actor = manager.get_next_actor()
    
    manager.dice_service.queue.clear()
    manager.dice_service.schedule_result(5)
    manager.dice_service.schedule_result(5)
    manager.dice_service.schedule_result(4)
    
    action = AttackAction(None, actor, [defensor], manager)
    manager.run_action(action)
    
    # 2. Defensor attacks back
    manager.set_tick(defensor, 0)
    actor = manager.get_next_actor()
    
    manager.dice_service.queue.clear()
    manager.dice_service.schedule_result(5)
    manager.dice_service.schedule_result(5)
    
    action = AttackAction(None, actor, [attacker], manager)
    load_counter = manager.run_action(action)
    
    assert any("PASSIVE|Bloquear|defensor" in h for h in load_counter.history)
    assert any("ATK_LOAD|bda|1|" in h for h in load_counter.history)
    assert not any(m.source == "Bloquear_Counter" for m in defensor.modifiers)
