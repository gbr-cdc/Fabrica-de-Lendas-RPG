import pytest
from unittest.mock import MagicMock
from combat.BattleActions import AttackAction, GenerateManaAction, GenerateFocusAction
from core.Structs import AttackActionTemplate, AttackEffects, RollResult
from core.Enums import BattleActionType, RollState, AttackType

def test_generate_mana_action():
    actor = MagicMock()
    actor.current_mp = 5
    actor.rules.limite_mana = 2
    actor.men = 10 # limit is 20
    actor.floating_mp = 0
    # mock generate_mana to simulate side effect
    def mock_generate():
        actor.floating_mp += 5
        return actor.floating_mp
    actor.generate_mana.side_effect = mock_generate
    
    action = GenerateManaAction(actor, target=actor, context=MagicMock())
    
    can_exec, msg = action.can_execute()
    assert can_exec is True
    
    load = action.execute()
    assert "gerou 5 de Mana!" in load.history[0]

def test_generate_focus_action():
    actor = MagicMock()
    actor.rules.limite_foco = 3
    actor.men = 10 # limit 30
    actor.floating_focus = 0
    def mock_generate():
        actor.floating_focus += 10
        return actor.floating_focus
    actor.generate_focus.side_effect = mock_generate
    
    action = GenerateFocusAction(actor, target=actor, context=MagicMock())
    
    can_exec, msg = action.can_execute()
    assert can_exec is True
    
    load = action.execute()
    assert "gerou 10 de Foco!" in load.history[0]

def test_attack_action_execution_flow():
    actor = MagicMock()
    actor.floating_focus = 10
    actor.atk_die = 10
    actor.rank = 2
    actor.bda = 0
    actor.pre = 0
    actor.pda = 10
    actor.mda = 1
    
    target = MagicMock()
    target.is_alive.return_value = True
    target.def_die = 8
    target.rank = 2
    target.bdd = 0
    target.grd = 0
    
    context = MagicMock()
    # Mock dice rolls: atk roll = 10, def roll = 5
    def mock_roll_dice(die, state):
        return RollResult(final_roll=10 if die == actor.atk_die else 5, roll1=10, roll2=None)
    context.dice_service.roll_dice.side_effect = mock_roll_dice
    
    template = AttackActionTemplate(
        id="Atk", nome="Atk", action_type=BattleActionType.STANDARD_ACTION, attack_type=AttackType.BASIC_ATTACK, focus_cost=5,
        effects=[AttackEffects("add_gda", {"amount": 5})]
    )
    
    action = AttackAction(template, actor, target, context)
    
    # 1. Check get_hooks processes add_gda
    hooks = action.get_hooks()
    assert "on_damage_calculation" in hooks
    
    # 2. Check execute flow
    can_exec, msg = action.can_execute()
    assert can_exec is True
    
    load = action.execute()
    
    # Atk mod = 10 + 2 + 0 = 12. Def mod = 5 + 2 + 0 = 7. GdA base = 5.
    # We didn't execute the hook automatically in the mock event bus because it's mocked context
    # so GdA base remains 5.
    # Target GRD = 0. Actor PRE = 0. (0 + 0 - 0) = 0.
    # GdA 5 > 0, so Hit is True.
    # Damage = PDA(10) + MDA(1) * GdA(5) = 15.
    
    assert load.hit is True
    assert load.gda == 5
    assert load.damage == 15
    target.take_damage.assert_called_with(15)
    actor.spend_focus.assert_called_with(5)
