import pytest
from unittest.mock import MagicMock
from core.DiceManager import DiceManager
from core.Enums import RollState

def test_dice_manager_neutral_roll():
    dm = DiceManager()
    dm.random.randint = MagicMock(return_value=15)
    result = dm.roll_dice(20, RollState.NEUTRAL)
    assert result.final_roll == 15
    assert result.roll1 == 15
    assert result.roll2 is None
    assert dm.random.randint.call_count == 1

def test_dice_manager_advantage_roll():
    dm = DiceManager()
    dm.random.randint = MagicMock(side_effect=[10, 18])
    result = dm.roll_dice(20, RollState.ADVANTAGE)
    assert result.final_roll == 18
    assert result.roll1 == 10
    assert result.roll2 == 18
    assert dm.random.randint.call_count == 2

def test_dice_manager_disadvantage_roll():
    dm = DiceManager()
    dm.random.randint = MagicMock(side_effect=[18, 10])
    result = dm.roll_dice(20, RollState.DISADVANTAGE)
    assert result.final_roll == 10
    assert result.roll1 == 18
    assert result.roll2 == 10
    assert dm.random.randint.call_count == 2
