import pytest
from core.Structs import BattleResult, RollResult, GameRules
from core.Events import AttackLoad
from unittest.mock import MagicMock

def test_battle_result_initialization():
    br = BattleResult()
    assert br.duration == 0
    assert isinstance(br.history, list)
    assert isinstance(br.action_per_character, dict)

def test_roll_result_initialization():
    rr = RollResult(final_roll=15, roll1=15, roll2=None)
    assert rr.final_roll == 15
    assert rr.roll1 == 15

def test_game_rules_initialization():
    rules = GameRules(
        hp_table=[10, 20],
        mp_table=[5, 10],
        action_cost_table=[1],
        limite_foco=3,
        limite_mana=2
    )
    assert rules.limite_foco == 3
    assert rules.limite_mana == 2
