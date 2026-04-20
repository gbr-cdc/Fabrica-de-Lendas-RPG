import pytest
from unittest.mock import MagicMock
from combat.StatusEffects import Atordoado
from core.Modifiers import EphemeralModifier
from core.Events import ActionLoad

def test_atordoado_apply():
    target = MagicMock()
    context = MagicMock()
    context.delay_character = MagicMock()
    
    # Applying Atordoado should add an EphemeralModifier to BDD with -1
    effect = Atordoado(duration=1, target=target, context=context)
    
    assert len(effect.modifiers) == 1
    assert isinstance(effect.modifiers[0], EphemeralModifier)
    assert effect.modifiers[0].stat_name == "bdd"
    assert effect.modifiers[0].value == -1
    
    target.add_status_effect.assert_called_with(effect)
    target.add_modifier.assert_called_with(effect.modifiers[0])
    
    # Should delay character by half action cost
    context.delay_character.assert_called_with(target, target.action_cost_base * 0.5)

def test_atordoado_hook_removal():
    target = MagicMock()
    target.char_id = "target_1"
    context = MagicMock()
    context.delay_character = MagicMock()
    
    effect = Atordoado(duration=1, target=target, context=context)
    
    hooks = effect.get_hooks()
    assert "on_turn_start" in hooks
    
    # Simulate turn start for another character
    other_char = MagicMock()
    other_char.char_id = "other_1"
    load_other = ActionLoad(character=other_char)
    hooks["on_turn_start"](load_other)
    
    # Effect should not be removed
    target.remove_status_effect.assert_not_called()
    
    # Simulate turn start for target character
    load_target = ActionLoad(character=target)
    hooks["on_turn_start"](load_target)
    
    # Effect should be removed
    target.remove_status_effect.assert_called_with(effect)
    assert target.remove_modifier.called
