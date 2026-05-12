import pytest
from tests.utils.test_utils import create_test_battle_manager
from tests.utils.entity_factory import create_dummy_character
from battle.BattleActions import AttackAction

def test_maos_pesadas_stun():
    """
    Test that MaosPesadas applies Atordoado status on high GdA hit.
    """
    manager = create_test_battle_manager()
    char = create_dummy_character(char_id="heavy", equipped=True)
    char.passive_abilities.append("MãosPesadas")
    target = create_dummy_character(char_id="target")
    
    manager.add_character(char, None, start_tick=1000)
    manager.add_character(target, None, start_tick=1000)
    
    manager.set_tick(char, 0)
    actor = manager.get_next_actor()
    
    # 10 (atk) - 1 (def) = 9 GdA (> 3 threshold).
    manager.dice_service.queue.clear()
    manager.dice_service.schedule_result(10)
    manager.dice_service.schedule_result(1)
    
    action = AttackAction(None, actor, [target], manager)
    load = manager.run_action(action)
    
    # Check status applied
    assert any(effect.__class__.__name__ == "Atordoado" for effect, hooks in manager.active_status_effects[target.char_id])
    assert any("STATUS|target|Atordoado|0|APPLIED" in h for h in load.history)
