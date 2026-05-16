import pytest
from unittest.mock import MagicMock, patch
from tests.utils.test_utils import create_test_battle_manager
from tests.utils.entity_factory import create_dummy_character
from battle.BattleActions import AttackAction
from core.Events import AttackLoad
from core.Enums import AttackType

def test_combo_second_attack_trigger():
    """
    Test that Combo triggers a second attack only if hit and roll >= threshold.
    """
    manager = create_test_battle_manager()
    owner = create_dummy_character(char_id="owner")
    owner.passive_abilities.append("Combo")
    target = create_dummy_character(char_id="target")
    
    manager.add_character(owner, None, start_tick=1000)
    manager.add_character(target, None, start_tick=1000)
    
    # 1. Roll < 5 -> No second attack
    manager.dice_service.queue.clear()
    manager.dice_service.schedule_result(4) # ATK Roll
    manager.dice_service.schedule_result(1) # DEF Roll
    
    action = AttackAction(None, owner, [target], manager)
    load = manager.run_action(action)
    
    assert not any("COMBO|owner|1" in h for h in load.history)

    # 2. Roll >= 5 and Hit -> Second attack triggers
    manager.dice_service.queue.clear()
    manager.dice_service.schedule_result(6) # ATK Roll
    manager.dice_service.schedule_result(1) # DEF Roll
    
    # Mock the second attack's rolls
    manager.dice_service.schedule_result(5) # ATK Roll (Second)
    manager.dice_service.schedule_result(1) # DEF Roll (Second)
    
    action = AttackAction(None, owner, [target], manager)
    load = manager.run_action(action)
    
    assert any("COMBO|owner|1" in h for h in load.history)
    # Check that it executed a second "Ataque Básico"
    # The history will have two "EXEC|Ataque Básico|owner"
    exec_tags = [h for h in load.history if "EXEC|Ataque Básico|owner" in h]
    assert len(exec_tags) == 2

def test_combo_no_third_attack():
    """
    Test that Combo does NOT trigger a third attack even if the second one hits.
    """
    manager = create_test_battle_manager()
    owner = create_dummy_character(char_id="owner")
    owner.passive_abilities.append("Combo")
    target = create_dummy_character(char_id="target")
    
    manager.add_character(owner, None, start_tick=1000)
    manager.add_character(target, None, start_tick=1000)
    
    # Schedule rolls for 1st and 2nd attacks, both hitting with high rolls
    manager.dice_service.queue.clear()
    # 1st Attack
    manager.dice_service.schedule_result(10) # ATK
    manager.dice_service.schedule_result(1)  # DEF
    # 2nd Attack
    manager.dice_service.schedule_result(10) # ATK
    manager.dice_service.schedule_result(1)  # DEF
    # No 3rd attack rolls scheduled. If it tries to roll, it might error or use default if queue empty,
    # but we will check history.
    
    action = AttackAction(None, owner, [target], manager)
    load = manager.run_action(action)
    
    # Should only have one COMBO event (the one that triggered the 2nd attack)
    combo_tags = [h for h in load.history if "COMBO|owner" in h]
    assert len(combo_tags) == 1
    
    # Should only have two EXEC tags
    exec_tags = [h for h in load.history if "EXEC|Ataque Básico|owner" in h]
    assert len(exec_tags) == 2

def test_combo_generates_focus():
    """
    Test that the second attack from Combo generates focus (since it's a BASIC_ATTACK).
    """
    manager = create_test_battle_manager()
    owner = create_dummy_character(char_id="owner")
    owner.passive_abilities.append("Combo")
    owner.floating_focus = 0
    target = create_dummy_character(char_id="target")
    
    manager.add_character(owner, None, start_tick=1000)
    manager.add_character(target, None, start_tick=1000)
    
    # Schedule rolls for two successful hits
    manager.dice_service.queue.clear()
    manager.dice_service.schedule_result(10) # 1st ATK
    manager.dice_service.schedule_result(1)  # 1st DEF
    manager.dice_service.schedule_result(10) # 2nd ATK
    manager.dice_service.schedule_result(1)  # 2nd DEF
    
    action = AttackAction(None, owner, [target], manager)
    load = manager.run_action(action)
    
    # Focus generation happens at the end of BASIC_ATTACK.
    # History should have two FOCUS tags with positive values (from focus generation).
    focus_tags = [h for h in load.history if "FOCUS|owner|" in h]
    # Each basic attack generates focus.
    # Depending on how Focus generation is implemented, it might be 1 per hit or similar.
    # We just want to see multiple focus increases.
    positive_focus = [f for f in focus_tags if int(f.split("|")[2]) > 0]
    assert len(positive_focus) >= 2

def test_combo_no_stun():
    """
    Test that Combo no longer applies Atordoado.
    """
    manager = create_test_battle_manager()
    owner = create_dummy_character(char_id="owner")
    owner.passive_abilities.append("Combo")
    target = create_dummy_character(char_id="target")
    
    manager.add_character(owner, None, start_tick=1000)
    manager.add_character(target, None, start_tick=1000)
    
    # Schedule rolls for two successful hits
    manager.dice_service.queue.clear()
    manager.dice_service.schedule_result(10) # 1st ATK
    manager.dice_service.schedule_result(1)  # 1st DEF
    manager.dice_service.schedule_result(10) # 2nd ATK
    manager.dice_service.schedule_result(1)  # 2nd DEF
    
    action = AttackAction(None, owner, [target], manager)
    load = manager.run_action(action)
    
    # Verify no "Atordoado" status in history
    assert not any("STATUS|target|Atordoado" in h for h in load.history)
    # Verify target doesn't have the status effect
    assert not any(se.name == "Atordoado" for se in target.status_effects)
