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

def test_attack_action_can_execute_failures():
    actor = MagicMock()
    actor.floating_focus = 0
    target = MagicMock()
    
    template = AttackActionTemplate(id="A", nome="A", action_type=BattleActionType.STANDARD_ACTION, attack_type=AttackType.BASIC_ATTACK, focus_cost=5, effects=[])
    action = AttackAction(template, actor, target, MagicMock())
    
    # Target dead
    target.is_alive.return_value = False
    can, msg = action.can_execute()
    assert can is False
    assert "derrotado" in msg
    
    # Focus insufficient
    target.is_alive.return_value = True
    can, msg = action.can_execute()
    assert can is False
    assert "insuficiente" in msg

def test_attack_action_gda_hook():
    action = AttackAction(AttackActionTemplate(id="A", nome="A", action_type=BattleActionType.STANDARD_ACTION, attack_type=AttackType.BASIC_ATTACK, focus_cost=0, effects=[AttackEffects("add_gda", {"amount": 5})]), MagicMock(), MagicMock(), MagicMock())
    hooks = action.get_hooks()
    
    load = MagicMock()
    load.character.char_id = action.actor.char_id
    load.gda = 0
    load.history = []
    
    hooks["on_damage_calculation"](load)
    assert load.gda == 5
    assert "adicionou +5" in load.history[0]

def test_attack_action_execute_miss():
    actor = MagicMock()
    actor.floating_focus = 10
    actor.atk_die = 10
    actor.rank = 0
    actor.bda = 0
    actor.pre = 0
    actor.pda = 10
    actor.mda = 1
    
    target = MagicMock()
    target.is_alive.return_value = True
    target.def_die = 20
    target.rank = 0
    target.bdd = 0
    target.grd = 10
    
    context = MagicMock()
    # Mock dice rolls: atk roll = 1, def roll = 20
    def mock_roll_dice(die, state):
        return RollResult(final_roll=1 if die == actor.atk_die else 20, roll1=1, roll2=None)
    context.dice_service.roll_dice.side_effect = mock_roll_dice
    
    action = AttackAction(AttackActionTemplate(id="A", nome="A", action_type=BattleActionType.STANDARD_ACTION, attack_type=AttackType.BASIC_ATTACK, focus_cost=0, effects=[]), actor, target, context)
    
    load = action.execute()
    assert load.hit is False
    assert "completamente defendido" in load.history[-1]

def test_attack_action_execute_gda_below_zero():
    # To hit line 80 (gda < 0), gda must be > (grd - pre), but still < 0.
    # This happens if target.grd is negative or actor.pre is high enough.
    actor = MagicMock()
    actor.atk_die = 10
    actor.rank = 0
    actor.bda = 0
    actor.pre = 10 # very high precision
    actor.pda = 10
    actor.mda = 1
    
    target = MagicMock()
    target.is_alive.return_value = True
    target.def_die = 10
    target.rank = 0
    target.bdd = 0
    target.grd = 0
    
    context = MagicMock()
    # Mock dice rolls: atk roll = 1, def roll = 5.
    # mod_atk = 1. mod_def = 5. gda base = -4.
    # hit check: -4 > (0 - 10) => -4 > -10 (True!)
    # then gda is set to 0.
    def mock_roll_dice(die, state):
        return RollResult(final_roll=1 if die == actor.atk_die else 5, roll1=1, roll2=None)
    context.dice_service.roll_dice.side_effect = mock_roll_dice
    
    action = AttackAction(AttackActionTemplate(id="A", nome="A", action_type=BattleActionType.STANDARD_ACTION, attack_type=AttackType.BASIC_ATTACK, focus_cost=0, effects=[]), actor, target, context)
    
    load = action.execute()
    assert load.hit is True
    assert load.gda == 0 # Was clamped from -4 to 0

def test_attack_action_gda_clamp_to_zero_explicit():
    actor = MagicMock()
    actor.char_id = "actor"
    actor.name = "Actor"
    actor.atk_die = 10
    actor.rank = 0
    actor.bda = 0
    actor.pre = 100
    actor.pda = 10
    actor.mda = 1
    actor.action_cost_base = 10
    
    target = MagicMock()
    target.name = "Target"
    target.char_id = "target"
    target.is_alive.return_value = True
    target.def_die = 8 # Distinct from 10
    target.rank = 0
    target.bdd = 0
    target.grd = 0
    
    context = MagicMock()
    # Mock dice rolls: atk roll = 1, def roll = 10.
    # mod_atk = 1. mod_def = 10. gda base = -9.
    # hit check: -9 > (0 - 100) => -9 > -100 (True)
    # Then gda is set to 0.
    def mock_roll(die, state):
        if die == actor.atk_die:
            return RollResult(final_roll=1, roll1=1, roll2=None)
        return RollResult(final_roll=10, roll1=10, roll2=None)
    context.dice_service.roll_dice.side_effect = mock_roll
    
    template = AttackActionTemplate(id="A", nome="A", action_type=BattleActionType.STANDARD_ACTION, attack_type=AttackType.BASIC_ATTACK, focus_cost=0, effects=[])
    action = AttackAction(template, actor, target, context)
    
    load = action.execute()
    assert load.hit is True
    assert load.gda == 0

def test_generate_mana_action_failures():
    actor = MagicMock()
    actor.current_mp = 0
    action = GenerateManaAction(actor, target=actor, context=MagicMock())
    
    # Out of daily mana
    can, msg = action.can_execute()
    assert can is False
    assert "esgotou" in msg
    
    # Floating limit reached
    actor.current_mp = 5
    actor.rules.limite_mana = 2
    actor.men = 10
    actor.floating_mp = 20
    can, msg = action.can_execute()
    assert can is False
    assert "limite" in msg
    
    assert action.get_hooks() == {}

def test_generate_focus_action_failures():
    actor = MagicMock()
    actor.rules.limite_foco = 3
    actor.men = 10
    actor.floating_focus = 30
    action = GenerateFocusAction(actor, target=actor, context=MagicMock())
    
    can, msg = action.can_execute()
    assert can is False
    assert "limite" in msg
    
    assert action.get_hooks() == {}
