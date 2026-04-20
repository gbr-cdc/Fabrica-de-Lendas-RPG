import pytest
from unittest.mock import MagicMock
from combat.Judges import BattleJudge
from core.Enums import BattleState

def test_battle_judge_running():
    judge = BattleJudge()
    context = MagicMock()
    
    char1 = MagicMock()
    char1.team = 1
    char1.is_alive.return_value = True
    
    char2 = MagicMock()
    char2.team = 2
    char2.is_alive.return_value = True
    
    context.get_characters.return_value = [char1, char2]
    
    assert judge.rule(context) == BattleState.RUNNING

def test_battle_judge_victory():
    judge = BattleJudge()
    context = MagicMock()
    
    char1 = MagicMock()
    char1.team = 1
    char1.is_alive.return_value = True
    
    char2 = MagicMock()
    char2.team = 2
    char2.is_alive.return_value = False # Team 2 is dead
    
    context.get_characters.return_value = [char1, char2]
    
    assert judge.rule(context) == BattleState.VICTORY

def test_battle_judge_draw():
    judge = BattleJudge()
    context = MagicMock()
    
    char1 = MagicMock()
    char1.team = 1
    char1.is_alive.return_value = False
    
    char2 = MagicMock()
    char2.team = 2
    char2.is_alive.return_value = False
    
    context.get_characters.return_value = [char1, char2]
    
    assert judge.rule(context) == BattleState.DRAW
