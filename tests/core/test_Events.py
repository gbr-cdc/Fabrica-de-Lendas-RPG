import pytest
from unittest.mock import MagicMock
from core.Events import AttackLoad
from core.Enums import AttackType, RollState

def test_attack_load_optional_target():
    char = MagicMock()
    context = MagicMock()
    
    # Test with target=None (Master Roll scenario)
    load = AttackLoad(
        character=char,
        battle_context=context,
        attack_type=AttackType.AREA,
        attack_state=RollState.NEUTRAL,
        defense_state=RollState.NEUTRAL,
        target=None
    )
    
    assert load.target is None
    assert load.character == char
    assert load.attack_type == AttackType.AREA
    assert load.gda == 0

def test_attack_load_with_target():
    char = MagicMock()
    target = MagicMock()
    context = MagicMock()
    
    # Test with explicit target (Standard Attack scenario)
    load = AttackLoad(
        character=char,
        target=target,
        battle_context=context,
        attack_type=AttackType.BASIC_ATTACK,
        attack_state=RollState.NEUTRAL,
        defense_state=RollState.NEUTRAL
    )
    
    assert load.target == target
    assert load.character == char
    assert load.attack_type == AttackType.BASIC_ATTACK
