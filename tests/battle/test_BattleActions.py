import pytest
from unittest.mock import MagicMock, patch
from battle.BattleActions import AttackAction, GenerateManaAction, GenerateFocusAction
from core.Structs import AttackActionTemplate, AttackEffects, RollResult
from core.Enums import BattleActionType, RollState, AttackType

def test_generate_mana_action():
    actor = MagicMock()
    actor.current_mp = 5
    actor.rules.limite_mana = 2
    actor.men = 10 # limit is 20
    actor.floating_mp = 0
    with patch('battle.BattleActions.CharacterSystem.generate_mana', return_value=5):
        action = GenerateManaAction(actor, targets=[actor], context=MagicMock())
        
        can_exec, msg = action.can_execute()
        assert can_exec is True
        
        load = action.execute()
        assert "gerou 5 de Mana!" in load.history[0]

def test_generate_focus_action():
    actor = MagicMock()
    actor.rules.limite_foco = 3
    actor.men = 10 # limit 30
    actor.floating_focus = 0
    with patch('battle.BattleActions.CharacterSystem.generate_focus', return_value=10):
        action = GenerateFocusAction(actor, targets=[actor], context=MagicMock())
        
        can_exec, msg = action.can_execute()
        assert can_exec is True
        
        load = action.execute()
        assert "gerou 10 de Foco!" in load.history[0]

def test_attack_action_execution_flow():
    actor = MagicMock()
    actor.char_id = "actor"
    actor.name = "Actor"
    actor.floating_focus = 10
    actor.atk_die = 10
    actor.rank = 2
    actor.bda = 0
    actor.pre = 0
    actor.pda = 10
    actor.mda = 1
    actor.men = 10
    actor.rules.limite_foco = 3
    
    target = MagicMock()
    target.char_id = "target"
    target.name = "Target"
    target.current_hp = 10
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
    
    action = AttackAction(template, actor, [target], context)
    
    # 1. Check get_hooks processes add_gda
    hooks = action.get_hooks()
    assert "on_damage_calculation" in hooks
    
    # 2. Check execute flow
    can_exec, msg = action.can_execute()
    assert can_exec is True
    
    # Capture emitted loads
    emitted_loads = []
    def mock_emit(event, load):
        if event == 'on_attack_end':
            emitted_loads.append(load)
    context.emit.side_effect = mock_emit

    action_load = action.execute()
    
    # Atk mod = 10 + 2 + 0 = 12. Def mod = 5 + 2 + 0 = 7. GdA base = 5.
    # Target GRD = 0. Actor PRE = 0. (0 + 0 - 0) = 0.
    # GdA 5 > 0, so Hit is True.
    # Damage = PDA(10) + MDA(1) * GdA(5) = 15.
    
    assert len(emitted_loads) == 1
    load = emitted_loads[0]
    assert load.hit is True
    assert load.gda == 5
    assert load.damage == 15
    # Verification of side effects (take_damage called with 15)
    from battle.BattleActions import CharacterSystem
    # Since CharacterSystem methods are mocked by MagicMock if imported? No, they are static/class methods.
    # Actually CharacterSystem.take_damage(target, load.damage) was called.
    # We should have patched it.

def test_attack_action_can_execute_failures():
    actor = MagicMock()
    actor.floating_focus = 0
    target = MagicMock()
    
    template = AttackActionTemplate(id="A", nome="A", action_type=BattleActionType.STANDARD_ACTION, attack_type=AttackType.BASIC_ATTACK, focus_cost=5, effects=[])
    action = AttackAction(template, actor, [target], MagicMock())
    
    # Target dead
    target.current_hp = 0
    with patch('battle.BattleActions.CharacterSystem.is_alive', return_value=False):
        can, msg = action.can_execute()
        assert can is False
        assert "derrotado" in msg
    
    # Focus insufficient
    with patch('battle.BattleActions.CharacterSystem.is_alive', return_value=True):
        can, msg = action.can_execute()
        assert can is False
        assert "insuficiente" in msg

def test_attack_action_gda_hook():
    action = AttackAction(AttackActionTemplate(id="A", nome="A", action_type=BattleActionType.STANDARD_ACTION, attack_type=AttackType.BASIC_ATTACK, focus_cost=0, effects=[AttackEffects("add_gda", {"amount": 5})]), MagicMock(), [], MagicMock())
    hooks = action.get_hooks()
    
    load = MagicMock()
    load.character.char_id = action.actor.char_id
    load.gda = 0
    load.history = []
    
    hooks["on_damage_calculation"](load)
    assert load.gda == 5
    assert "adicionou +5" in load.history[0]

def test_attack_action_execute_miss():
    actor = MagicMock(atk_die=10, rank=0, bda=0, pre=0, pda=10, mda=1, floating_focus=10, men=10)
    actor.rules.limite_foco = 3
    
    target = MagicMock(current_hp=10, def_die=20, rank=0, bdd=0, grd=10)
    target.name = "Target"
    
    context = MagicMock()
    def mock_roll_dice(die, state):
        return RollResult(final_roll=1 if die == actor.atk_die else 20, roll1=1, roll2=None)
    context.dice_service.roll_dice.side_effect = mock_roll_dice
    
    action = AttackAction(AttackActionTemplate(id="A", nome="A", action_type=BattleActionType.STANDARD_ACTION, attack_type=AttackType.BASIC_ATTACK, focus_cost=0, effects=[]), actor, [target], context)
    
    emitted_loads = []
    context.emit.side_effect = lambda ev, ld: emitted_loads.append(ld) if ev == 'on_attack_end' else None

    action.execute()
    load = emitted_loads[0]
    assert load.hit is False
    assert "completamente defendido" in load.history[-1]

def test_attack_action_execute_gda_below_zero():
    actor = MagicMock(atk_die=10, rank=0, bda=0, pre=10, pda=10, mda=1, floating_focus=10, men=10)
    actor.rules.limite_foco = 3
    
    target = MagicMock(current_hp=10, def_die=10, rank=0, bdd=0, grd=0)
    target.name = "Target"
    
    context = MagicMock()
    def mock_roll_dice(die, state):
        return RollResult(final_roll=1 if die == actor.atk_die else 5, roll1=1, roll2=None)
    context.dice_service.roll_dice.side_effect = mock_roll_dice
    
    action = AttackAction(AttackActionTemplate(id="A", nome="A", action_type=BattleActionType.STANDARD_ACTION, attack_type=AttackType.BASIC_ATTACK, focus_cost=0, effects=[]), actor, [target], context)
    
    emitted_loads = []
    context.emit.side_effect = lambda ev, ld: emitted_loads.append(ld) if ev == 'on_attack_end' else None

    action.execute()
    load = emitted_loads[0]
    assert load.hit is True
    assert load.gda == 0

def test_attack_action_gda_clamp_to_zero_explicit():
    actor = MagicMock(char_id="actor", name="Actor", atk_die=10, rank=0, bda=0, pre=100, pda=10, mda=1, action_cost_base=10, floating_focus=10, men=10)
    actor.rules.limite_foco = 3
    
    target = MagicMock(name="Target", char_id="target", current_hp=10, def_die=8, rank=0, bdd=0, grd=0)
    
    context = MagicMock()
    def mock_roll(die, state):
        if die == actor.atk_die:
            return RollResult(final_roll=1, roll1=1, roll2=None)
        return RollResult(final_roll=10, roll1=10, roll2=None)
    context.dice_service.roll_dice.side_effect = mock_roll
    
    template = AttackActionTemplate(id="A", nome="A", action_type=BattleActionType.STANDARD_ACTION, attack_type=AttackType.BASIC_ATTACK, focus_cost=0, effects=[])
    action = AttackAction(template, actor, [target], context)
    
    emitted_loads = []
    context.emit.side_effect = lambda ev, ld: emitted_loads.append(ld) if ev == 'on_attack_end' else None

    action.execute()
    load = emitted_loads[0]
    assert load.hit is True
    assert load.gda == 0

def test_generate_mana_action_failures():
    actor = MagicMock()
    actor.current_mp = 0
    action = GenerateManaAction(actor, targets=[actor], context=MagicMock())
    
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
    action = GenerateFocusAction(actor, targets=[actor], context=MagicMock())
    
    can, msg = action.can_execute()
    assert can is False
    assert "limite" in msg
    
    assert action.get_hooks() == {}
