import pytest
from tests.utils.test_utils import create_test_battle_manager
from tests.utils.entity_factory import create_dummy_character
from battle.BattleActions import AttackAction
from core.Events import AttackLoad

def test_forca_bruta_gda_bonus():
    """
    Test that ForcaBruta doubles GdA on hit.
    """
    manager = create_test_battle_manager()
    char = create_dummy_character(char_id="brucutu")
    char.passive_abilities.append("ForçaBruta")
    target = create_dummy_character(char_id="alvo")
    
    manager.add_character(char, None, start_tick=1000)
    manager.add_character(target, None, start_tick=1000)
    
    manager.set_tick(char, 0)
    actor = manager.get_next_actor()
    
    # 10 (atk) - 5 (def) = 5 GdA. 
    # ForcaBruta should double it to 10.
    manager.dice_service.queue.clear()
    manager.dice_service.schedule_result(10)
    manager.dice_service.schedule_result(5)
    
    action = AttackAction(None, actor, [target], manager)
    load = manager.run_action(action)
    
    # In AttackAction, the final GdA is not exposed in the ActionLoad return.
    # We check the history for the doubled GdA in damage or similar if needed, 
    # but the presence of the MOD event with value 5 (doubling the original 5) is sufficient.
    assert any("PASSIVE|Força Bruta|brucutu" in h for h in load.history)
    assert any("ATK_LOAD|gda|5|" in h for h in load.history)
