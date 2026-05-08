import pytest
from unittest.mock import MagicMock
from battle.BattleActions import AttackAction, EFFECT_HOOK_BUILDERS
from core.Events import AttackLoad
from core.Structs import AttackActionTemplate, AttackEffects
from core.Enums import BattleActionType, AttackType, RollState
from core.DiceManager import DiceManager
from tests.utils.entity_factory import create_dummy_character
from core.Modifiers import EphemeralModifier
from battle.StatusEffects import Atordoado

def test_golpe_de_escudo_mechanics():
    dice = DiceManager(seed=42)
    
    # Actor: FIS 10, HAB 10, MEN 10 -> Rank 2
    actor = create_dummy_character(char_id="actor", attributes=[10, 10, 10])
    actor.base_atk_die = 6
    actor.base_def_die = 12 # Higher def die for the shield strike
    actor.floating_focus = 10
    
    target = create_dummy_character(char_id="target", attributes=[10, 10, 10])
    target.current_hp = 100
    
    context = MagicMock()
    context.dice_service = dice
    
    # Template for Golpe de Escudo
    template = AttackActionTemplate(
        id="golpe_escudo",
        nome="Golpe de Escudo",
        action_type=BattleActionType.STANDARD_ACTION,
        attack_type=AttackType.BASIC_ATTACK,
        focus_cost=2,
        effects=[
            AttackEffects("swap_atk_def_die", {}),
            AttackEffects("set_gda_zero_on_dmg", {}),
            AttackEffects("apply_status_on_hit_threshold", {"status": "Atordoado", "threshold": 3, "duration": 1})
        ]
    )
    
    action = AttackAction(template, actor, [target], context)
    hooks = action.get_hooks()
    
    # Setup mock emit to trigger hooks
    def mock_emit(event, load):
        if event in hooks:
            hooks[event](load)
            
    context.emit.side_effect = mock_emit
    
    # --- Test Case 1: Hit with GdA > 3 ---
    # Atk Roll: 10 (on d12) + Rank 2 + BDA 0 = 12
    # Def Roll: 2 (on d6) + Rank 2 + BDD 0 = 4
    # GdA = 8
    dice.schedule_result(10) # Atk roll
    dice.schedule_result(2)  # Def roll
    
    action.execute()
    
    # Verify Atordoado applied (GdA 8 > 3)
    assert any(isinstance(s, Atordoado) for s in target.status_effects)
    
    # Verify GdA was zeroed for damage calculation
    # Damage = PDA 10 + (MDA 1 * GdA 0) = 10
    assert target.current_hp == 90 # 100 - 10
    
    # Verify die swap happened (ROLL|ATK|10|12|actor)
    # The history tags are in the action_load. Wait, I should capture it.
    
    # Cleanup target for next test
    target.status_effects.clear()
    target.modifiers.clear()
    target.current_hp = 100
    
    # --- Test Case 2: Hit with GdA <= 3 ---
    # Atk Roll: 4 (on d12) + Rank 2 = 6
    # Def Roll: 4 (on d6) + Rank 2 = 6
    # GdA = 0 -> Hit is only if GdA > target.grd - actor.pre (usually 0)
    # Let's make it hit but GdA <= 3
    # Atk Roll: 7 + 2 = 9
    # Def Roll: 4 + 2 = 6
    # GdA = 3
    dice.schedule_result(7) # Atk roll
    dice.schedule_result(4) # Def roll
    
    action.execute()
    
    # Verify Atordoado NOT applied (GdA 3 <= 3)
    assert not any(isinstance(s, Atordoado) for s in target.status_effects)
    assert target.current_hp == 90 # Damage still 10

def test_swap_atk_def_die_cleanup():
    actor = create_dummy_character()
    actor.base_atk_die = 6
    actor.base_def_die = 12
    
    template = AttackActionTemplate(
        id="swap", nome="Swap", action_type=BattleActionType.STANDARD_ACTION,
        attack_type=AttackType.BASIC_ATTACK, focus_cost=0,
        effects=[AttackEffects("swap_atk_def_die", {})]
    )
    
    context = MagicMock()
    action = AttackAction(template, actor, [create_dummy_character()], context)
    hooks = action.get_hooks()
    
    # Before
    assert actor.atk_die == 6
    
    # During on_roll_modify
    load = MagicMock()
    load.character = actor
    hooks['on_roll_modify'](load)
    assert actor.atk_die == 12
    
    # After on_attack_end
    hooks['on_attack_end'](load)
    assert actor.atk_die == 6
