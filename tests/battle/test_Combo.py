import pytest
from unittest.mock import MagicMock, patch
from tests.utils.test_utils import create_test_battle_manager
from tests.utils.entity_factory import create_dummy_character
from battle.BattleActions import AttackAction
from core.Events import AttackLoad

def test_combo_passive_progression():
    """
    Test that Combo passive correctly increments stage and triggers extra attacks.
    """
    manager = create_test_battle_manager()
    owner = create_dummy_character(char_id="owner")
    owner.passive_abilities.append("Combo")
    target = create_dummy_character(char_id="target")
    
    manager.add_character(owner, None, start_tick=1000)
    manager.add_character(target, None, start_tick=1000)
    
    manager.set_tick(owner, 0)
    actor = manager.get_next_actor()
    
    # 1. First Attack (Hit) -> Triggers 1st Extra Attack
    # We mock AttackAction to avoid recursive dice consumption in this specific logic test
    action_mock = MagicMock()
    action_mock.execute_if_possible.return_value = MagicMock(success=True, history=["EXEC|ExtraAttack|1"])
    
    manager.dice_service.queue.clear()
    manager.dice_service.schedule_result(10) # ATK
    manager.dice_service.schedule_result(1)  # DEF
    
    with patch("battle.BattlePassives.AttackAction", return_value=action_mock):
        action = AttackAction(None, actor, [target], manager)
        load = manager.run_action(action)
        
    assert any("COMBO|owner|1" in h for h in load.history)
    assert any("EXEC|ExtraAttack|1" in h for h in load.history)

def test_combo_reset_on_miss():
    """
    Test that Combo resets when an attack misses.
    """
    # This can be tested more simply by triggering the hook directly or using a real battle
    from battle.BattlePassives import Combo
    owner = create_dummy_character(char_id="owner")
    manager = create_test_battle_manager()
    
    combo = Combo(owner, manager)
    combo.stage = 1
    combo.hit = True
    
    # Simulate a miss
    load = AttackLoad(character=owner, target=create_dummy_character(), 
                      attack_type=MagicMock(), attack_state=MagicMock(), defense_state=MagicMock())
    load.hit = False
    
    hooks = combo.get_hooks()
    hooks['on_attack_end'](load)
    
    assert combo.stage == 0
    assert combo.hit is False
