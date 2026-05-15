
import pytest
from tests.utils.test_utils import create_test_battle_manager
from tests.utils.entity_factory import create_dummy_character
from core.Enums import RollState, AttackType
from battle.BattleActions import AttackAction, WaitAction, GenerateFocusAction
from core.Structs import BattlePassiveTemplate

def test_bloquear_reacao_and_counter():
    bm = create_test_battle_manager()
    
    # Character B has Bloquear
    passive_template = BattlePassiveTemplate(
        id="Bloquear",
        name="Bloquear",
        parameters={
            "focus_cost": 2,
            "reduction_die": 4,
            "counter_threshold": -3,
            "counter_bda_bonus": 1
        }
    )
    
    char_a = create_dummy_character(char_id="A", name="Attacker", team=1)
    char_b = create_dummy_character(char_id="B", name="Defender", team=2)
    char_b.passive_abilities = ["Bloquear"]
    char_b.floating_focus = 10
    
    bm.add_character(char_a, bm.get_controller(char_a.char_id), start_tick=100)
    bm.add_character(char_b, bm.get_controller(char_b.char_id), start_tick=200)
    
    # Inject template parameters into the active passive
    passive = bm.get_active_passive("B", "Bloquear")
    passive.template = passive_template
    
    # 1. A attacks B. We want B to use reaction and GdA to end up <= -3.
    # Force rolls: A=6, B=5 -> GdA=1.
    # With reaction 1d4=4 -> GdA = 1 - 4 = -3.
    
    bm.dice_service.schedule_result(6) # A Atk roll
    bm.dice_service.schedule_result(5) # B Def roll
    bm.dice_service.schedule_result(4) # B Reaction roll (d4)
    
    # Mock reaction choice
    controller_b = bm.get_controller("B")
    def mock_choose_reaction(char, name, attack_load, context):
        return True
    controller_b.choose_reaction = mock_choose_reaction
    
    atk = AttackAction(None, char_a, [char_b], bm)
    res = bm.run_action(atk)
    
    # Check if reaction was used
    assert char_b.floating_focus == 8 # 10 - 2
    # GdA should be -3
    assert passive._counter_targets.get("A") is True
    
    # 2. B takes a turn and generates focus (MOVE_ACTION).
    gen_focus = GenerateFocusAction(char_b, [], bm)
    bm.run_action(gen_focus)
    
    # Bonus should be lost
    assert "A" not in passive._counter_targets

def test_bloquear_bonus_applied_and_cleared():
    bm = create_test_battle_manager()
    
    char_a = create_dummy_character(char_id="A", name="Attacker", team=1)
    char_b = create_dummy_character(char_id="B", name="Defender", team=2)
    char_b.passive_abilities = ["Bloquear"]
    
    bm.add_character(char_a, bm.get_controller(char_a.char_id), start_tick=100)
    bm.add_character(char_b, bm.get_controller(char_b.char_id), start_tick=200)
    
    passive = bm.get_active_passive("B", "Bloquear")
    passive._counter_targets["A"] = True # Force bonus against A
    
    # B attacks A
    bm.dice_service.schedule_result(5) # B Atk roll
    bm.dice_service.schedule_result(5) # A Def roll
    
    atk = AttackAction(None, char_b, [char_a], bm)
    res = bm.run_action(atk)
    
    # Check history for BDA bonus
    bda_bonus_found = any("ATK_LOAD|bda|1" in msg for msg in res.history)
    assert bda_bonus_found
    
    # Check if bonus was cleared after attack
    assert "A" not in passive._counter_targets
