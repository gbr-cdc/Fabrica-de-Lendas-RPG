from battle.StatusEffects import Atordoado
from core.BaseClasses import StatusEffect
from core.Modifiers import EphemeralModifier
from core.Events import ActionLoad
from tests.utils.entity_factory import create_dummy_character
from unittest.mock import MagicMock
from tests.utils.test_utils import create_test_battle_manager

def test_atordoado_apply():
    target = create_dummy_character()
    manager = create_test_battle_manager()
    manager.add_character(target, MagicMock())
    
    # Applying Atordoado should add an EphemeralModifier to BDD with -1
    effect = Atordoado(duration=1, target=target, context=manager)
    manager.add_status_effect(effect)
    
    assert any(m.stat_name == "bdd" and m.value == -1 for m in target.modifiers)
    active_effects = [e[0] for e in manager.active_status_effects[target.char_id]]
    assert effect in active_effects
    
    target_tick = None
    for tick, neg_hab, neg_roll, char_id, char in manager.timeline:
            if char_id == target.char_id:
                target_tick = tick

    # Should delay character by half action cost
    assert target_tick > 0

def test_atordoado_hook_removal():
    target = create_dummy_character(char_id="target_1")
    manager = create_test_battle_manager()
    manager.add_character(target, MagicMock())
    
    baseline_subs = sum(len(subs) for subs in manager.listeners.values())
    
    effect = Atordoado(duration=1, target=target, context=manager)
    manager.add_status_effect(effect)
        
    current_subs = sum(len(subs) for subs in manager.listeners.values())
    assert current_subs > baseline_subs
    
    char = create_dummy_character(char_id="target_2")
    # Simulate turn start for another character
    manager.emit("on_turn_start", ActionLoad(character=char))
    
    # Effect should not be removed
    active_effects = [e[0] for e in manager.active_status_effects[target.char_id]]
    assert effect in active_effects
    current_subs = sum(len(subs) for subs in manager.listeners.values())
    assert current_subs > baseline_subs
    
    # Simulate turn start for target character
    load_target = ActionLoad(character=target)
    manager.emit("on_turn_start", load_target)
    
    # Effect should be removed
    active_effects = [e[0] for e in manager.active_status_effects[target.char_id]]
    assert effect not in active_effects
    assert not any(m.stat_name == "bdd" for m in target.modifiers)
    
    final_subs = sum(len(subs) for subs in manager.listeners.values())
    assert final_subs == baseline_subs
