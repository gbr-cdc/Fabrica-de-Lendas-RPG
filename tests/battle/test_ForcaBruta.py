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
    
    # Get the multiplier from the data manager to avoid hardcoding
    template = manager.data_service.get_passive_template("ForçaBruta")
    multiplier = template.parameters.get("multiplier", 2)
    
    # 10 (atk) - 5 (def) = 5 GdA. 
    base_gda = 10 - 5
    manager.dice_service.queue.clear()
    manager.dice_service.schedule_result(10)
    manager.dice_service.schedule_result(5)
    
    action = AttackAction(None, actor, [target], manager)
    load = manager.run_action(action)
    
    # Calculation following Força Bruta logic: added_val = val * (multiplier - 1)
    expected_added_gda = base_gda * (multiplier - 1)
    
    # In AttackAction, the final GdA is not exposed in the ActionLoad return.
    assert any("PASSIVE|Força Bruta|brucutu" in h for h in load.history)
    assert any(f"ATK_LOAD|gda|{expected_added_gda}|" in h for h in load.history)
