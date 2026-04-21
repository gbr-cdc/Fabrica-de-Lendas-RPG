import pytest
from unittest.mock import MagicMock, patch
from battle.BattlePassives import PosturaDefensiva
from battle.BattleActions import TogglePosturaDefensiva
from core.Events import AttackLoad, ActionLoad
from core.Enums import BattleActionType

def test_postura_defensiva_toggle_modifiers():
    char = MagicMock()
    char.char_id = "c1"
    char.name = "Warrior"
    context = MagicMock()
    
    passive = PosturaDefensiva(char, context)
    
    # Toggle ON
    msg = passive.toggle()
    assert passive.is_active is True
    assert "assumiu a Postura Defensiva" in msg
    assert char.add_modifier.call_count == 2
    
    # Check if atk_die and def_die modifiers were added
    args1 = char.add_modifier.call_args_list[0][0][0]
    args2 = char.add_modifier.call_args_list[1][0][0]
    assert args1.stat_name == 'atk_die' and args1.value == -2
    assert args2.stat_name == 'def_die' and args2.value == 2

    # Toggle OFF
    msg = passive.toggle()
    assert passive.is_active is False
    assert "saiu da Postura Defensiva" in msg
    assert char.remove_modifier.call_count == 2

def test_postura_defensiva_hit_tracking():
    char = MagicMock()
    char.char_id = "owner"
    char.name = "Owner"
    target = MagicMock()
    target.char_id = "target"
    target.name = "Target"
    context = MagicMock()
    
    passive = PosturaDefensiva(char, context)
    passive.is_active = True
    hooks = passive.get_hooks()
    
    # 1. Hit target
    load = AttackLoad(character=char, target=target, battle_context=context, 
                      attack_type=MagicMock(), attack_state=MagicMock(), defense_state=MagicMock(), 
                      gda=5, damage=0)
    load.hit = True
    hooks["on_gda_modify"](load)
    
    assert passive._tracked_target == target
    assert "[POSTURA]" in load.history[0]
    
    # 2. Tracked target attacks owner
    atk_load = AttackLoad(character=target, target=char, battle_context=context, 
                          attack_type=MagicMock(), attack_state=MagicMock(), defense_state=MagicMock(), 
                          gda=0, damage=0)
    hooks["on_roll_modify"](atk_load)
    
    assert passive._penalty_applied is True
    target.add_modifier.assert_called_once()
    mod = target.add_modifier.call_args[0][0]
    assert mod.stat_name == 'pre' and mod.value == -1
    assert "[POSTURA]" in atk_load.history[0]

def test_postura_defensiva_cleanup_success():
    char = MagicMock()
    char.char_id = "owner"
    target = MagicMock()
    target.char_id = "target"
    context = MagicMock()
    
    passive = PosturaDefensiva(char, context)
    passive.is_active = True
    passive._tracked_target = target
    passive._penalty_applied = True
    hooks = passive.get_hooks()
    
    # Target attack ends
    atk_load = AttackLoad(character=target, target=char, battle_context=context, 
                          attack_type=MagicMock(), attack_state=MagicMock(), defense_state=MagicMock(), 
                          gda=5, damage=0)
    hooks["on_attack_end"](atk_load)
    
    target.remove_modifiers_by_source.assert_called_once_with("PosturaDefensiva_Penalidade")
    assert passive._tracked_target is None
    assert passive._penalty_applied is False

def test_postura_defensiva_cleanup_miss():
    char = MagicMock()
    char.char_id = "owner"
    target = MagicMock()
    target.char_id = "target"
    context = MagicMock()
    
    passive = PosturaDefensiva(char, context)
    passive.is_active = True
    passive._tracked_target = target
    passive._penalty_applied = False # No attack against owner happened
    hooks = passive.get_hooks()
    
    # Target turn ends
    action_load = ActionLoad(character=target)
    hooks["on_turn_end"](action_load)
    
    assert passive._tracked_target is None
    # remove_modifiers_by_source shouldn't be called if penalty wasn't applied
    target.remove_modifiers_by_source.assert_not_called()

def test_toggle_action_execution():
    char = MagicMock()
    char.char_id = "c1"
    context = MagicMock()
    passive = MagicMock()
    passive.toggle.return_value = "Toggled!"
    context.get_active_passive.return_value = passive
    
    action = TogglePosturaDefensiva(char, MagicMock(), context)
    assert action.action_type == BattleActionType.FREE_ACTION
    
    result = action.execute()
    assert result.success is True
    assert result.history[0] == "Toggled!"
    context.get_active_passive.assert_called_once_with("c1", "Postura Defensiva")
