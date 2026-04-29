import pytest
from battle.BattlePassives import PosturaDefensiva
from battle.BattleActions import TogglePosturaDefensiva
from core.Events import AttackLoad, ActionLoad
from core.Enums import BattleActionType, AttackType, RollState
from tests.utils.entity_factory import create_dummy_character
from unittest.mock import MagicMock

def test_postura_defensiva_toggle_modifiers():
    char = create_dummy_character()
    context = MagicMock()
    
    passive = PosturaDefensiva(char, context)
    
    # Toggle ON
    msg = passive.toggle()
    assert passive.is_active is True
    assert "assumiu a Postura Defensiva" in msg
    assert any(m.stat_name == 'atk_die' and m.value == -2 for m in char.modifiers)
    assert any(m.stat_name == 'def_die' and m.value == 2 for m in char.modifiers)
    
    # Toggle OFF
    msg = passive.toggle()
    assert passive.is_active is False
    assert "saiu da Postura Defensiva" in msg
    assert not any(m.source == 'PosturaDefensiva' for m in char.modifiers)

def test_postura_defensiva_hit_tracking():
    char = create_dummy_character(char_id="owner")
    target = create_dummy_character(char_id="target")
    context = MagicMock()
    
    passive = PosturaDefensiva(char, context)
    passive.is_active = True
    hooks = passive.get_hooks()
    
    # 1. Hit target
    load = AttackLoad(character=char, target=target, battle_context=context, 
                      attack_type=AttackType.BASIC_ATTACK, attack_state=RollState.NEUTRAL, defense_state=RollState.NEUTRAL, 
                      gda=5, damage=0)
    load.hit = True
    hooks["on_gda_modify"](load)
    
    assert target.char_id in passive._tracked_targets
    assert "[POSTURA]" in load.history[0]
    
    # 2. Tracked target attacks owner
    atk_load = AttackLoad(character=target, target=char, battle_context=context, 
                          attack_type=AttackType.BASIC_ATTACK, attack_state=RollState.NEUTRAL, defense_state=RollState.NEUTRAL, 
                          gda=0, damage=0)
    hooks["on_roll_modify"](atk_load)
    
    assert passive._tracked_targets[target.char_id] is True
    assert any(m.stat_name == 'pre' and m.value == -1 for m in target.modifiers)
    assert "[POSTURA]" in atk_load.history[0]

def test_postura_defensiva_cleanup_success():
    char = create_dummy_character(char_id="owner")
    target = create_dummy_character(char_id="target")
    context = MagicMock()
    context.get_characters.return_value = [target]
    
    passive = PosturaDefensiva(char, context)
    passive.is_active = True
    passive._tracked_targets[target.char_id] = True
    from core.Modifiers import EphemeralModifier
    target.add_modifier(EphemeralModifier(stat_name='pre', value=-1, source='PosturaDefensiva_Penalidade'))
    
    hooks = passive.get_hooks()
    
    # Target attack ends
    atk_load = AttackLoad(character=target, target=char, battle_context=context, 
                          attack_type=AttackType.BASIC_ATTACK, attack_state=RollState.NEUTRAL, defense_state=RollState.NEUTRAL, 
                          gda=5, damage=0)
    hooks["on_attack_end"](atk_load)
    
    assert not any(m.source == "PosturaDefensiva_Penalidade" for m in target.modifiers)
    assert target.char_id not in passive._tracked_targets

def test_postura_defensiva_cleanup_miss():
    char = create_dummy_character(char_id="owner")
    target = create_dummy_character(char_id="target")
    context = MagicMock()
    context.get_characters.return_value = [target]
    
    passive = PosturaDefensiva(char, context)
    passive.is_active = True
    passive._tracked_targets[target.char_id] = False # No attack against owner happened
    hooks = passive.get_hooks()
    
    # Target turn ends
    action_load = ActionLoad(character=target)
    hooks["on_turn_end"](action_load)
    
    assert target.char_id not in passive._tracked_targets
    assert not any(m.source == "PosturaDefensiva_Penalidade" for m in target.modifiers)

def test_postura_defensiva_multi_tracking():
    char = create_dummy_character(char_id="owner")
    t1 = create_dummy_character(char_id="t1")
    t2 = create_dummy_character(char_id="t2")
    context = MagicMock()
    
    passive = PosturaDefensiva(char, context)
    passive.is_active = True
    hooks = passive.get_hooks()
    
    # Hit T1
    load1 = AttackLoad(character=char, target=t1, battle_context=context, 
                       attack_type=AttackType.BASIC_ATTACK, attack_state=RollState.NEUTRAL, defense_state=RollState.NEUTRAL, 
                       hit=True)
    hooks["on_gda_modify"](load1)
    
    # Hit T2
    load2 = AttackLoad(character=char, target=t2, battle_context=context, 
                       attack_type=AttackType.BASIC_ATTACK, attack_state=RollState.NEUTRAL, defense_state=RollState.NEUTRAL, 
                       hit=True)
    hooks["on_gda_modify"](load2)
    
    assert "t1" in passive._tracked_targets
    assert "t2" in passive._tracked_targets
    assert len(passive._tracked_targets) == 2

def test_toggle_action_execution():
    char = create_dummy_character(char_id="c1")
    context = MagicMock()
    passive = MagicMock()
    passive.toggle.return_value = "Toggled!"
    context.get_active_passive.return_value = passive
    
    action = TogglePosturaDefensiva(char, [], context)
    assert action.action_type == BattleActionType.FREE_ACTION
    
    result = action.execute()
    assert result.success is True
    assert result.history[0] == "Toggled!"
    context.get_active_passive.assert_called_once_with("c1", "Postura Defensiva")

def test_postura_defensiva_on_roll_modify_no_target():
    char = create_dummy_character(char_id="owner")
    attacker = create_dummy_character(char_id="attacker")
    context = MagicMock()
    
    passive = PosturaDefensiva(char, context)
    passive.is_active = True
    passive._tracked_targets["attacker"] = False
    
    hooks = passive.get_hooks()
    
    # Attack with target=None (Master Roll scenario)
    load = AttackLoad(
        character=attacker,
        target=None,
        battle_context=context,
        attack_type=AttackType.AREA,
        attack_state=RollState.NEUTRAL,
        defense_state=RollState.NEUTRAL
    )
    
    # This should NOT crash
    hooks["on_roll_modify"](load)
    
    assert passive._tracked_targets["attacker"] is False

