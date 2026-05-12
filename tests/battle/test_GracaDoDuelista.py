import pytest
from tests.utils.test_utils import create_test_battle_manager
from tests.utils.entity_factory import create_dummy_character
from battle.BattleActions import AttackAction
from core.Enums import RollState
from unittest.mock import MagicMock
from core.Events import HistoryEmitter

def test_graca_do_duelista_full_flow():
    """
    Test the full flow of GracaDoDuelista following [ARCH.TEST_QUALITY]:
    - Success bonus (on hit)
    - Defensive reaction (on being targeted)
    """
    manager = create_test_battle_manager()
    
    # 1. Setup characters
    # Attacker with GracaDoDuelista
    attacker = create_dummy_character(char_id="duelista", name="Duelista")
    attacker.passive_abilities.append("GraçaDoDuelista")
    attacker.floating_focus = 10
    
    # Target (will also have it to test reaction later)
    target = create_dummy_character(char_id="alvo", name="Alvo")
    target.passive_abilities.append("GraçaDoDuelista")
    target.floating_focus = 10
    
    # Mock controllers
    ctrl_duelista = MagicMock()
    ctrl_alvo = MagicMock()
    # Target always chooses to react
    ctrl_alvo.choose_reaction.return_value = True
    
    manager.add_character(attacker, ctrl_duelista, start_tick=1000)
    manager.add_character(target, ctrl_alvo, start_tick=1000)
    
    # --- PHASE 1: Duelista attacks Alvo (Success Bonus) ---
    manager.set_tick(attacker, 0)
    actor = manager.get_next_actor()
    
    # Fetch data-driven parameters
    params = manager.data_service.get_passive_template("GraçaDoDuelista").parameters
    bonus_die = params.get("bonus_die", 6)
    reaction_die = params.get("reaction_die", 4)
    reaction_cost = params.get("reaction_cost", 2)
    
    # Dice: 
    # Atk: 10
    # Def: 5
    # Reaction (reaction_die): 2
    # Success Bonus (bonus_die): 4
    manager.dice_service.queue.clear()
    manager.dice_service.schedule_result(10) # ATK
    manager.dice_service.schedule_result(5)  # DEF
    manager.dice_service.schedule_result(2)  # Reaction
    manager.dice_service.schedule_result(4)  # Success Bonus
    
    action = AttackAction(None, actor, [target], manager)
    load = manager.run_action(action)
    
    # Assertions:
    # 1. Success Bonus triggered
    assert any("PASSIVE|Graça do Duelista|duelista" in h for h in load.history)
    assert any("ATK_LOAD|gda|4|" in h for h in load.history)
    
    # 2. Reaction triggered
    assert any("PASSIVE|Graça do Duelista|alvo" in h for h in load.history)
    assert any("ATK_LOAD|gda|-2|" in h for h in load.history)
    assert any(f"FOCUS|alvo|-{reaction_cost}|{10 - reaction_cost}" in h for h in load.history)
    assert target.floating_focus == 10 - reaction_cost


def test_graca_do_duelista_reaction_threshold():
    """
    Test that the reaction only triggers when it would be a hit.
    """
    manager = create_test_battle_manager()
    
    attacker = create_dummy_character(char_id="attacker")
    target = create_dummy_character(char_id="duelista")
    target.passive_abilities.append("GraçaDoDuelista")
    target.floating_focus = 10
    
    # Set stats to 0 to simplify
    attacker.base_pre = 0
    attacker.base_rank = 0
    target.base_grd = 0
    target.base_rank = 0
    
    ctrl_duelista = MagicMock()
    ctrl_duelista.choose_reaction.return_value = True
    
    manager.add_character(attacker, MagicMock(), start_tick=1000)
    manager.add_character(target, ctrl_duelista, start_tick=1000)
    
    # Scenario A: Exactly threshold (gda = 0). 
    # Hit condition: gda > grd - pre => 0 > 0 - 0 => False.
    # Reaction should NOT trigger.
    manager.set_tick(attacker, 0)
    actor = manager.get_next_actor()
    
    manager.dice_service.queue.clear()
    manager.dice_service.schedule_result(5) # ATK
    manager.dice_service.schedule_result(5) # DEF
    
    action = AttackAction(None, actor, [target], manager)
    load = manager.run_action(action)
    
    assert not any("PASSIVE|Graça do Duelista" in h for h in load.history)
    assert target.floating_focus == 10
    
    # Scenario B: Just above threshold (gda = 1).
    # Hit condition: 1 > 0 => True.
    # Reaction SHOULD trigger.
    manager.set_tick(attacker, 0)
    actor = manager.get_next_actor()
    
    params = manager.data_service.get_passive_template("GraçaDoDuelista").parameters
    reaction_cost = params.get("reaction_cost", 2)
    
    manager.dice_service.queue.clear()
    manager.dice_service.schedule_result(6) # ATK
    manager.dice_service.schedule_result(5) # DEF
    manager.dice_service.schedule_result(1) # Reaction (d4)
    
    action = AttackAction(None, actor, [target], manager)
    load = manager.run_action(action)
    
    assert any("PASSIVE|Graça do Duelista|duelista" in h for h in load.history)
    assert any("ATK_LOAD|gda|-1|" in h for h in load.history)
    assert target.floating_focus == 10 - reaction_cost

