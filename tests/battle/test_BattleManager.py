import pytest
from unittest.mock import MagicMock
from battle.BattleManager import BattleManager
from core.Enums import BattleState, BattleActionType
from core.Events import ActionLoad

def test_battle_manager_add_and_get_actor():
    dm = MagicMock()
    judge = MagicMock()
    bm = BattleManager(dice_service=MagicMock(), data_service=dm, judge=judge)
    
    char = MagicMock()
    char.char_id = "c1"
    char.current_hp = 10
    char.passive_abilities = []
    
    bm.add_character(char, controller=MagicMock(), start_tick=10)
    
    # get_next_actor should return char and update current_tick to 10
    actor = bm.get_next_actor()
    assert actor == char
    assert bm.current_tick == 10

def test_battle_manager_delay_character():
    bm = BattleManager(dice_service=MagicMock(), data_service=MagicMock(), judge=MagicMock())
    
    char1 = MagicMock()
    char1.char_id = "c1"
    char1.current_hp = 10
    char1.passive_abilities = []
    
    char2 = MagicMock()
    char2.char_id = "c2"
    char2.current_hp = 10
    char2.passive_abilities = []
    
    bm.add_character(char1, controller=MagicMock(), start_tick=10)
    bm.add_character(char2, controller=MagicMock(), start_tick=20)
    
    # Delay char1 by 15 ticks, so char1 goes to tick 25
    bm.delay_character(char1, 15)
    
    actor = bm.get_next_actor()
    # Now char2 should be first at tick 20
    assert actor == char2
    assert bm.current_tick == 20

def test_battle_manager_pub_sub():
    bm = BattleManager(dice_service=MagicMock(), data_service=MagicMock(), judge=MagicMock())
    
    callback_called = False
    def my_callback(payload):
        nonlocal callback_called
        callback_called = True
        
    bm.subscribe("on_turn_start", my_callback)
    bm.emit("on_turn_start", MagicMock())
    assert callback_called is True
    
    callback_called = False
    bm.unsubscribe("on_turn_start", my_callback)
    bm.emit("on_turn_start", MagicMock())
    assert callback_called is False

def test_battle_manager_try_finally_hooks():
    judge = MagicMock()
    judge.rule.side_effect = [BattleState.RUNNING, BattleState.VICTORY]
    
    bm = BattleManager(dice_service=MagicMock(), data_service=MagicMock(), judge=judge)
    
    actor = MagicMock()
    actor.char_id = "c1"
    actor.current_hp = 10
    actor.passive_abilities = []
    
    controller_mock = MagicMock()
    # Mock controller to return an action
    action = MagicMock()
    action_load = MagicMock()
    action_load.success = True
    action.execute_if_possible.return_value = action_load
    
    # Provide hooks for the action
    hook_called = False
    def action_hook(payload):
        pass
    action.get_hooks.return_value = {"on_turn_end": action_hook}
    
    controller_mock.choose_action.return_value = action
    
    bm.add_character(actor, controller=controller_mock, start_tick=10)
    
    bm.run_battle()
    
    # Ensure hook is not permanently in listeners after battle completes
    assert action_hook not in bm.listeners["on_turn_end"]
