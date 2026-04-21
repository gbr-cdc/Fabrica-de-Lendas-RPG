import pytest
from unittest.mock import MagicMock
from core.BaseClasses import GameAction, BattleAction
from core.Events import ActionLoad

class DummyAction(GameAction):
    def __init__(self, can_exec=True):
        self._can_exec = can_exec
        self.executed = False
        self.actor = MagicMock()

    def can_execute(self):
        if self._can_exec:
            return True, ""
        return False, "Failed to execute"

    def execute(self):
        self.executed = True
        load = ActionLoad(character=MagicMock())
        load.success = True
        return load

def test_execute_if_possible_success():
    action = DummyAction(can_exec=True)
    load = action.execute_if_possible()
    
    assert action.executed is True
    assert load.success is True

def test_execute_if_possible_failure():
    action = DummyAction(can_exec=False)
    load = action.execute_if_possible()
    
    assert action.executed is False
    assert load.success is False
    assert "Failed to execute" in load.history

def test_battle_action_defaults():
    actor = MagicMock()
    target = MagicMock()
    context = MagicMock()
    action = BattleAction("Test", actor, target, context, MagicMock())
    
    can, msg = action.can_execute()
    assert can is True
    
    load = action.execute()
    assert load.success is False
    assert "não pode ser executada" in load.history[0]
