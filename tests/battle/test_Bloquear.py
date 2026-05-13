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
    
    # Get parameters
    params = manager.data_service.get_passive_template("Bloquear").parameters
    focus_cost = params.get("focus_cost", 2)
    
    action = AttackAction(None, actor, [defensor], manager)
    load = manager.run_action(action)
    
    assert any("PASSIVE|Bloquear|defensor" in h for h in load.history)
    assert any("ATK_LOAD|gda|-3|" in h for h in load.history)
    assert defensor.floating_focus == 10 - focus_cost

def test_bloquear_counter_bonus():
    """
    Test the counter-bonus mechanism: +BDA on the next attack against the same target.
    Scenario: attacker hits (GdA=1 with atk=6, def=5), defensor blocks (rolls 1 → GdA=0),
    GdA=0 <= counter_threshold(0) so counter is set. Defensor then attacks back.
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

    # Get parameters
    params = manager.data_service.get_passive_template("Bloquear").parameters
    focus_cost = params.get("focus_cost", 2)
    counter_bda_bonus = params.get("counter_bda_bonus", 1)
    counter_threshold = params.get("counter_threshold", 0)

    # 1. Attacker attacks defensor: atk=6, def=5 → GdA=1 (hit), block_roll=1 → GdA=0 <= threshold
    manager.set_tick(attacker, 0)
    actor = manager.get_next_actor()

    manager.dice_service.queue.clear()
    manager.dice_service.schedule_result(6)  # atk roll
    manager.dice_service.schedule_result(5)  # def roll
    manager.dice_service.schedule_result(1)  # block reduction roll → GdA=1-1=0 <= counter_threshold

    action = AttackAction(None, actor, [defensor], manager)
    manager.run_action(action)

    # Counter must be set (reaction fired and GdA <= threshold)
    bloquear_passive = manager.get_active_passive(defensor.char_id, "Bloquear")
    assert bloquear_passive is not None
    assert attacker.char_id in bloquear_passive._counter_targets

    # 2. Defensor attacks back — counter BDA bonus should apply
    manager.set_tick(defensor, 0)
    actor = manager.get_next_actor()

    manager.dice_service.queue.clear()
    manager.dice_service.schedule_result(5)  # atk roll
    manager.dice_service.schedule_result(5)  # def roll

    action = AttackAction(None, actor, [attacker], manager)
    load_counter = manager.run_action(action)

    assert any("PASSIVE|Bloquear|defensor" in h for h in load_counter.history)
    assert any(f"ATK_LOAD|bda|{counter_bda_bonus}|" in h for h in load_counter.history)
    # Counter is consumed after the attack
    assert attacker.char_id not in bloquear_passive._counter_targets
