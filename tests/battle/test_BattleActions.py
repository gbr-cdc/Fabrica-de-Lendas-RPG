import pytest
from battle.BattleActions import AttackAction, GenerateManaAction, GenerateFocusAction
from core.Events import ActionLoad, AttackLoad
from core.Structs import AttackActionTemplate, AttackEffects, RollResult
from core.Enums import BattleActionType, RollState, AttackType
from core.DiceManager import DiceManager
from tests.utils.entity_factory import create_dummy_character
from unittest.mock import MagicMock

def test_generate_mana_action():
    actor = create_dummy_character()
    actor.current_mp = 5
    actor.rules.limite_mana = 2
    actor.men = 10 # MEN 10
    actor.floating_mp = 0
    
    action = GenerateManaAction(actor, targets=[actor], context=MagicMock())
    
    can_exec, msg = action.can_execute()
    assert can_exec is True
    
    load = action.execute()
    assert "gerou 5 de Mana!" in load.history[0]
    assert actor.current_mp == 0 
    assert actor.floating_mp == 5 

def test_generate_focus_action():
    actor = create_dummy_character()
    actor.rules.limite_foco = 3
    actor.men = 10 # MEN 10
    actor.floating_focus = 0
    
    action = GenerateFocusAction(actor, targets=[actor], context=MagicMock())
    
    can_exec, msg = action.can_execute()
    assert can_exec is True
    
    load = action.execute()
    assert "gerou 10 de Foco!" in load.history[0]
    assert actor.floating_focus == 10

def test_attack_action_execution_flow():
    dice = DiceManager(seed=42)
    
    actor = create_dummy_character(char_id="actor", attributes=[10, 10, 10])
    actor.floating_focus = 10
    actor.hab = 10 # HAB 10 -> Atk Mod = 10 + Rank
    # Let's check character stats: rank is calculated from total attributes? 
    # No, Character constructor sets self.rank = (sum(attributes)//3)//5
    # sum = 30, sum//3 = 10, 10//5 = 2. So Rank = 2.
    # Atk Mod = 10 + 2 = 12.
    
    target = create_dummy_character(char_id="target", attributes=[10, 10, 10])
    target.current_hp = 100
    # Rank = 2. Def Mod = 10 + 2 = 12.
    
    context = MagicMock()
    context.dice_service = dice
    
    # schedule rolls: atk roll = 10, def roll = 5
    dice.schedule_result(10)
    dice.schedule_result(5)
    
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
        if event == 'on_damage_calculation':
            hooks['on_damage_calculation'](load)
        if event == 'on_attack_end':
            emitted_loads.append(load)
    context.emit.side_effect = mock_emit

    action_load = action.execute()
    
    # Atk = 10 + 12 = 22. Def = 5 + 12 = 17. GdA = 22 - 17 = 5.
    # With hook (+5), GdA = 10.
    
    assert len(emitted_loads) == 1
    load = emitted_loads[0]
    assert load.hit is True
    assert load.gda == 10
    
    # Check if target HP changed
    assert target.current_hp < 100

def test_attack_action_can_execute_failures():
    actor = create_dummy_character()
    actor.floating_focus = 0
    target = create_dummy_character()
    
    template = AttackActionTemplate(id="A", nome="A", action_type=BattleActionType.STANDARD_ACTION, attack_type=AttackType.BASIC_ATTACK, focus_cost=5, effects=[])
    action = AttackAction(template, actor, [target], MagicMock())
    
    # Focus insufficient
    can, msg = action.can_execute()
    assert can is False
    assert "insuficiente" in msg

    # Target dead
    actor.floating_focus = 10
    target.current_hp = 0
    can, msg = action.can_execute()
    assert can is False
    assert "derrotado" in msg

def test_attack_action_gda_hook():
    actor = create_dummy_character()
    action = AttackAction(AttackActionTemplate(id="A", nome="A", action_type=BattleActionType.STANDARD_ACTION, attack_type=AttackType.BASIC_ATTACK, focus_cost=0, effects=[AttackEffects("add_gda", {"amount": 5})]), actor, [], MagicMock())
    hooks = action.get_hooks()
    
    load = ActionLoad(character=actor)
    load.gda = 0
    load.history = []
    
    hooks["on_damage_calculation"](load)
    assert load.gda == 5
    assert "adicionou +5" in load.history[0]

def test_attack_action_execute_miss():
    dice = DiceManager(seed=42)
    actor = create_dummy_character(attributes=[1, 1, 1])
    actor.floating_focus = 10
    
    target = create_dummy_character(attributes=[15, 15, 15])
    
    context = MagicMock()
    context.dice_service = dice
    dice.schedule_result(1) # atk
    dice.schedule_result(20) # def
    
    action = AttackAction(AttackActionTemplate(id="A", nome="A", action_type=BattleActionType.STANDARD_ACTION, attack_type=AttackType.BASIC_ATTACK, focus_cost=0, effects=[]), actor, [target], context)
    
    emitted_loads = []
    context.emit.side_effect = lambda ev, ld: emitted_loads.append(ld) if ev == 'on_attack_end' else None

    action.execute()
    load = emitted_loads[0]
    assert load.hit is False
    assert "completamente defendido" in load.history[-1]

def test_generate_mana_action_failures():
    actor = create_dummy_character()
    actor.current_mp = 0
    action = GenerateManaAction(actor, targets=[actor], context=MagicMock())
    
    # Out of daily mana
    can, msg = action.can_execute()
    assert can is False
    assert "esgotou" in msg
    
    # Floating limit reached
    actor.current_mp = 10
    actor.rules.limite_mana = 1
    actor.men = 5 # MEN 5
    actor.floating_mp = 5 # limit 5
    can, msg = action.can_execute()
    assert can is False
    assert "limite" in msg

def test_generate_focus_action_failures():
    actor = create_dummy_character()
    actor.rules.limite_foco = 1
    actor.men = 5 # MEN 5
    actor.floating_focus = 5 # limit 5
    action = GenerateFocusAction(actor, targets=[actor], context=MagicMock())
    
    can, msg = action.can_execute()
    assert can is False
    assert "limite" in msg

