import pytest
from battle.StatusEffects import Atordoado, StatusEffect
from core.Modifiers import EphemeralModifier
from core.Events import ActionLoad
from tests.utils.entity_factory import create_dummy_character
from unittest.mock import MagicMock
from tests.utils.test_context import BattleTestContext

def test_atordoado_apply():
    target = create_dummy_character()
    context = BattleTestContext()
    context.delay_character = MagicMock()
    
    baseline = context.subscriber_count
    
    # Applying Atordoado should add an EphemeralModifier to BDD with -1
    effect = Atordoado(duration=1, target=target, context=context)
    context.add_status_effect(effect)
    
    assert any(m.stat_name == "bdd" and m.value == -1 for m in target.modifiers)
    assert effect in target.status_effects
    
    # Should delay character by half action cost
    context.delay_character.assert_called_with(target, target.action_cost_base * 0.5)

def test_atordoado_hook_removal():
    target = create_dummy_character(char_id="target_1")
    context = BattleTestContext()
    
    baseline_subs = context.subscriber_count
    
    effect = Atordoado(duration=1, target=target, context=context)
    context.add_status_effect(effect)
        
    assert context.subscriber_count > baseline_subs
    
    # Simulate turn start for another character
    other_char = create_dummy_character(char_id="other_1")
    load_other = ActionLoad(character=other_char)
    context.emit("on_turn_start", load_other)
    
    # Effect should not be removed
    assert effect in target.status_effects
    assert context.subscriber_count > baseline_subs
    
    # Simulate turn start for target character
    load_target = ActionLoad(character=target)
    context.emit("on_turn_start", load_target)
    
    # Effect should be removed
    assert effect not in target.status_effects
    assert not any(m.stat_name == "bdd" for m in target.modifiers)
    
    # Baseline assertion (This fails because the engine leaks the subscription)
    assert context.subscriber_count == baseline_subs
