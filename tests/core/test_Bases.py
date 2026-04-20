import pytest
from unittest.mock import MagicMock
from core.Bases import GameAction
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
