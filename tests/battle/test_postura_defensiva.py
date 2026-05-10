import pytest
from battle.BattlePassives import PosturaDefensiva
from battle.BattleActions import TogglePosturaDefensiva
from core.Events import AttackLoad, ActionLoad
from core.Enums import BattleActionType, AttackType, RollState
from tests.utils.entity_factory import create_dummy_character
from unittest.mock import MagicMock
from tests.utils.test_utils import create_test_battle_manager

def test_postura_defensiva_toggle_modifiers():
    char = create_dummy_character()
    manager = create_test_battle_manager()
    manager.add_character(char, MagicMock())
    
    passive = PosturaDefensiva(char, manager)
    
    # Toggle ON
    msg = passive.toggle()
    assert passive.is_active is True
    assert f"POSTURA|{char.char_id}|ON" in msg
    assert any(m.stat_name == 'atk_die' and m.value == -2 for m in char.modifiers)
    assert any(m.stat_name == 'def_die' and m.value == 2 for m in char.modifiers)
    
    # Toggle OFF
    msg = passive.toggle()
    assert passive.is_active is False
    assert f"POSTURA|{char.char_id}|OFF" in msg
    assert not any(m.source == 'PosturaDefensiva' for m in char.modifiers)

def test_postura_defensiva_hit_tracking():
    char = create_dummy_character(char_id="owner")
    target = create_dummy_character(char_id="target")
    manager = create_test_battle_manager()
    manager.add_character(char, MagicMock())
    manager.add_character(target, MagicMock())
    
    passive = PosturaDefensiva(char, manager)
    passive.is_active = True
    hooks = passive.get_hooks()
    
    for ev, cb in hooks.items():
        manager.subscribe(ev, cb)
    
    baseline = sum(len(subs) for subs in manager.listeners.values())
    
    # 1. Hit target
    load = AttackLoad(character=char, target=target, 
                      attack_type=AttackType.BASIC_ATTACK, attack_state=RollState.NEUTRAL, defense_state=RollState.NEUTRAL, 
                      gda=5, damage=0)
    load.hit = True
    manager.emit("on_gda_modify", load)
    
    assert target.char_id in passive._tracked_targets
    assert "POSTURA|owner|OBSERVE|target" in load.history[0]
    
    # 2. Tracked target attacks owner
    atk_load = AttackLoad(character=target, target=char, 
                          attack_type=AttackType.BASIC_ATTACK, attack_state=RollState.NEUTRAL, defense_state=RollState.NEUTRAL, 
                          gda=0, damage=0)
    manager.emit("on_roll_modify", atk_load)
    
    assert passive._tracked_targets[target.char_id] is True
    assert any(m.stat_name == 'pre' and m.value == -1 for m in target.modifiers)
    assert "MOD|PosturaDefensiva" in atk_load.history[0]
    assert sum(len(subs) for subs in manager.listeners.values()) == baseline

def test_postura_defensiva_cleanup_success():
    char = create_dummy_character(char_id="owner")
    target = create_dummy_character(char_id="target")
    manager = create_test_battle_manager()
    manager.add_character(char, MagicMock())
    manager.add_character(target, MagicMock())
    
    passive = PosturaDefensiva(char, manager)
    passive.is_active = True
    passive._tracked_targets[target.char_id] = True
    from core.Modifiers import EphemeralModifier
    target.add_modifier(EphemeralModifier(stat_name='pre', value=-1, source='PosturaDefensiva_Penalidade'))
    
    hooks = passive.get_hooks()
    for ev, cb in hooks.items():
        manager.subscribe(ev, cb)
    baseline = sum(len(subs) for subs in manager.listeners.values())
    
    # Target attack ends
    atk_load = AttackLoad(character=target, target=char, 
                          attack_type=AttackType.BASIC_ATTACK, attack_state=RollState.NEUTRAL, defense_state=RollState.NEUTRAL, 
                          gda=5, damage=0)
    manager.emit("on_attack_end", atk_load)
    
    assert not any(m.source == "PosturaDefensiva_Penalidade" for m in target.modifiers)
    assert target.char_id not in passive._tracked_targets
    assert sum(len(subs) for subs in manager.listeners.values()) == baseline

def test_postura_defensiva_cleanup_miss():
    char = create_dummy_character(char_id="owner")
    target = create_dummy_character(char_id="target")
    manager = create_test_battle_manager()
    manager.add_character(char, MagicMock())
    manager.add_character(target, MagicMock())
    
    passive = PosturaDefensiva(char, manager)
    passive.is_active = True
    passive._tracked_targets[target.char_id] = False # No attack against owner happened
    hooks = passive.get_hooks()
    for ev, cb in hooks.items():
        manager.subscribe(ev, cb)
    baseline = sum(len(subs) for subs in manager.listeners.values())
    
    # Target turn ends
    action_load = ActionLoad(character=target)
    manager.emit("on_turn_end", action_load)
    
    assert target.char_id not in passive._tracked_targets
    assert not any(m.source == "PosturaDefensiva_Penalidade" for m in target.modifiers)
    assert sum(len(subs) for subs in manager.listeners.values()) == baseline

def test_postura_defensiva_multi_tracking():
    char = create_dummy_character(char_id="owner")
    t1 = create_dummy_character(char_id="t1")
    t2 = create_dummy_character(char_id="t2")
    manager = create_test_battle_manager()
    manager.add_character(char, MagicMock())
    manager.add_character(t1, MagicMock())
    manager.add_character(t2, MagicMock())
    
    passive = PosturaDefensiva(char, manager)
    passive.is_active = True
    hooks = passive.get_hooks()
    for ev, cb in hooks.items():
        manager.subscribe(ev, cb)
    baseline = sum(len(subs) for subs in manager.listeners.values())
    
    # Hit T1
    load1 = AttackLoad(character=char, target=t1, 
                       attack_type=AttackType.BASIC_ATTACK, attack_state=RollState.NEUTRAL, defense_state=RollState.NEUTRAL, 
                       hit=True)
    manager.emit("on_gda_modify", load1)
    
    # Hit T2
    load2 = AttackLoad(character=char, target=t2, 
                       attack_type=AttackType.BASIC_ATTACK, attack_state=RollState.NEUTRAL, defense_state=RollState.NEUTRAL, 
                       hit=True)
    manager.emit("on_gda_modify", load2)
    
    assert "t1" in passive._tracked_targets
    assert "t2" in passive._tracked_targets
    assert len(passive._tracked_targets) == 2
    assert sum(len(subs) for subs in manager.listeners.values()) == baseline

def test_toggle_action_execution():
    char = create_dummy_character(char_id="c1")
    manager = create_test_battle_manager()
    manager.add_character(char, MagicMock())
    
    passive = MagicMock()
    passive.toggle.return_value = "POSTURA|c1|ON"
    manager.get_active_passive = MagicMock(return_value=passive)
    
    action = TogglePosturaDefensiva(char, [], manager)
    assert action.action_type == BattleActionType.FREE_ACTION
    
    result = action.execute()
    assert result.success is True
    assert "POSTURA|c1|ON" in result.history[0]
    manager.get_active_passive.assert_called_once_with("c1", "Postura Defensiva")

def test_postura_defensiva_on_roll_modify_no_target():
    char = create_dummy_character(char_id="owner")
    attacker = create_dummy_character(char_id="attacker")
    manager = create_test_battle_manager()
    manager.add_character(char, MagicMock())
    manager.add_character(attacker, MagicMock())
    
    passive = PosturaDefensiva(char, manager)
    passive.is_active = True
    passive._tracked_targets["attacker"] = False
    
    hooks = passive.get_hooks()
    for ev, cb in hooks.items():
        manager.subscribe(ev, cb)
    baseline = sum(len(subs) for subs in manager.listeners.values())
    
    # Attack with target=None (Master Roll scenario)
    load = AttackLoad(
        character=attacker,
        target=None,
        attack_type=AttackType.AREA,
        attack_state=RollState.NEUTRAL,
        defense_state=RollState.NEUTRAL
    )
    
    # This should NOT crash
    manager.emit("on_roll_modify", load)
    
    assert passive._tracked_targets["attacker"] is False
    assert sum(len(subs) for subs in manager.listeners.values()) == baseline
