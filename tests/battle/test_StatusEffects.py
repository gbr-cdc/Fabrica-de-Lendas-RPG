import pytest
from battle.StatusEffects import Atordoado
from core.Modifiers import EphemeralModifier
from core.Events import ActionLoad
from tests.utils.entity_factory import create_dummy_character
from unittest.mock import MagicMock

def test_atordoado_apply():
    target = create_dummy_character()
    context = MagicMock()
    
    # Applying Atordoado should add an EphemeralModifier to BDD with -1
    effect = Atordoado(duration=1, target=target, context=context)
    
    assert any(m.stat_name == "bdd" and m.value == -1 for m in target.modifiers)
    assert effect in target.status_effects
    
    # Should delay character by half action cost
    context.delay_character.assert_called_with(target, target.action_cost_base * 0.5)

def test_atordoado_hook_removal():
    target = create_dummy_character(char_id="target_1")
    context = MagicMock()
    
    effect = Atordoado(duration=1, target=target, context=context)
    
    hooks = effect.get_hooks()
    assert "on_turn_start" in hooks
    
    # Simulate turn start for another character
    other_char = create_dummy_character(char_id="other_1")
    load_other = ActionLoad(character=other_char)
    hooks["on_turn_start"](load_other)
    
    # Effect should not be removed
    assert effect in target.status_effects
    
    # Simulate turn start for target character
    load_target = ActionLoad(character=target)
    hooks["on_turn_start"](load_target)
    
    # Effect should be removed
    assert effect not in target.status_effects
    assert not any(m.stat_name == "bdd" for m in target.modifiers)

