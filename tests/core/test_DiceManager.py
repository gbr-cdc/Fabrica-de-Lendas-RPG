import pytest
from core.DiceManager import DiceManager
from core.Enums import RollState

def test_dice_manager_neutral_roll():
    # Seed 1 with sides=20: first randint is 5
    dm = DiceManager(seed=1)
    result = dm.roll_dice(20, RollState.NEUTRAL)
    assert result.final_roll == 5
    assert result.roll1 == 5
    assert result.roll2 is None

def test_dice_manager_advantage_roll():
    # Seed 1 with sides=20: rolls are 5 and 19
    dm = DiceManager(seed=1)
    result = dm.roll_dice(20, RollState.ADVANTAGE)
    assert result.final_roll == 19
    assert result.roll1 == 5
    assert result.roll2 == 19

def test_dice_manager_disadvantage_roll():
    # Seed 1 with sides=20: rolls are 5 and 19
    dm = DiceManager(seed=1)
    result = dm.roll_dice(20, RollState.DISADVANTAGE)
    assert result.final_roll == 5
    assert result.roll1 == 5
    assert result.roll2 == 19

def test_dice_manager_scheduled_roll():
    dm = DiceManager()
    dm.schedule_result(20)
    result = dm.roll_dice(20)
    assert result.final_roll == 20
    assert result.scheduled is True
