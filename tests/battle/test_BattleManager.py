import pytest
from battle.BattleManager import BattleManager
from battle.Judges import BattleJudge
from core.DiceManager import DiceManager
from tests.utils.entity_factory import create_dummy_character
from core.Enums import BattleState, BattleActionType
from core.Events import ActionLoad
from unittest.mock import MagicMock
from core.CharacterSystem import CharacterSystem

def test_battle_manager_add_and_get_actor():
    dice = DiceManager(seed=42)
    # schedule a roll for tie-break in add_character
    dice.schedule_result(5) 
    
    bm = BattleManager(dice_service=dice, data_service=MagicMock(), judge=BattleJudge())
    
    char = create_dummy_character(char_id="c1", attributes=[10, 10, 10])
    
    bm.add_character(char, controller=MagicMock(), start_tick=10)
    
    # get_next_actor should return char and update current_tick to 10
    actor = bm.get_next_actor()
    assert actor == char
    assert bm.current_tick == 10

def test_battle_manager_delay_character():
    dice = DiceManager(seed=42)
    # schedule rolls for tie-breaks
    dice.schedule_result(5) # char1
    dice.schedule_result(6) # char2
    
    bm = BattleManager(dice_service=dice, data_service=MagicMock(), judge=BattleJudge())
    
    char1 = create_dummy_character(char_id="c1")
    char2 = create_dummy_character(char_id="c2")
    
    bm.add_character(char1, controller=MagicMock(), start_tick=10)
    bm.add_character(char2, controller=MagicMock(), start_tick=20)
    
    # schedule roll for delay_character
    dice.schedule_result(7)
    
    # Delay char1 by 15 ticks, so char1 goes to tick 25
    bm.delay_character(char1, 15)
    
    actor = bm.get_next_actor()
    # Now char2 should be first at tick 20
    assert actor == char2
    assert bm.current_tick == 20

def test_battle_manager_pub_sub():
    bm = BattleManager(dice_service=MagicMock(), data_service=MagicMock(), judge=BattleJudge())
    
    callback_called = False
    def my_callback(payload):
        nonlocal callback_called
        callback_called = True
        
    bm.subscribe("on_turn_start", my_callback)
    bm.emit("on_turn_start", ActionLoad(character=MagicMock()))
    assert callback_called is True
    
    callback_called = False
    bm.unsubscribe("on_turn_start", my_callback)
    bm.emit("on_turn_start", ActionLoad(character=MagicMock()))
    assert callback_called is False

def test_battle_manager_try_finally_hooks():
    dice = DiceManager(seed=42)
    dice.schedule_result(5) # char1 add
    dice.schedule_result(6) # char2 add
    
    char1 = create_dummy_character(char_id="c1", team=1)
    char2 = create_dummy_character(char_id="c2", team=2)
    
    bm = BattleManager(dice_service=dice, data_service=MagicMock(), judge=BattleJudge())
    
    controller_mock = MagicMock()
    # Mock controller to return an action
    action = MagicMock()
    action.action_type = BattleActionType.STANDARD_ACTION
    action_load = ActionLoad(character=char1)
    action_load.success = True
    action.execute_if_possible.return_value = action_load
    
    # Provide hooks for the action
    action_hook_called = False
    def action_hook(payload):
        nonlocal action_hook_called
        action_hook_called = True
    
    action.get_hooks.return_value = {"on_turn_end": action_hook}
    
    # When choose_action is called, we kill char2 to end the battle after one turn
    def side_effect(*args, **kwargs):
        CharacterSystem.take_damage(char2, 9999)
        return action
    
    controller_mock.choose_action.side_effect = side_effect
    
    bm.add_character(char1, controller=controller_mock, start_tick=10)
    bm.add_character(char2, controller=MagicMock(), start_tick=100) 
    
    bm.run_battle()
    
    # Ensure hook is not permanently in listeners after battle completes
    assert action_hook not in bm.listeners["on_turn_end"]

