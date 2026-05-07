import pytest
from unittest.mock import MagicMock
from battle.Judges import BattleJudge
from core.Enums import BattleState
from core.Structs import BattleResult

def test_battle_judge_running():
    judge = BattleJudge()
    context = MagicMock()
    result = BattleResult()
    
    char1 = MagicMock()
    char1.team = 1
    char1.current_hp = 10
    
    char2 = MagicMock()
    char2.team = 2
    char2.current_hp = 10
    
    context.get_characters.return_value = [char1, char2]
    context.get_graveyard.return_value = []
    
    assert judge.rule(context, result) == BattleState.RUNNING
    assert len(result.winners) == 0
    assert len(result.losers) == 0

def test_battle_judge_victory():
    judge = BattleJudge()
    context = MagicMock()
    result = BattleResult()
    
    char1 = MagicMock()
    char1.team = 1
    char1.current_hp = 10
    
    char2 = MagicMock()
    char2.team = 2
    char2.current_hp = 0 # Team 2 is dead
    
    # In reality, dead characters are moved to graveyard
    context.get_characters.return_value = [char1]
    context.get_graveyard.return_value = [char2]
    
    assert judge.rule(context, result) == BattleState.VICTORY
    assert char1 in result.winners
    assert char2 in result.losers

def test_battle_judge_draw():
    judge = BattleJudge()
    context = MagicMock()
    result = BattleResult()
    
    char1 = MagicMock()
    char1.team = 1
    char1.current_hp = 0
    
    char2 = MagicMock()
    char2.team = 2
    char2.current_hp = 0
    
    context.get_characters.return_value = []
    context.get_graveyard.return_value = [char1, char2]
    
    assert judge.rule(context, result) == BattleState.DRAW
    assert len(result.winners) == 0
    assert char1 in result.losers
    assert char2 in result.losers
