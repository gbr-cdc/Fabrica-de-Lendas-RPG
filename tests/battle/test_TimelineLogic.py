import pytest
from unittest.mock import MagicMock
from battle.BattleManager import BattleManager
from core.Enums import RollState
from core.Structs import RollResult

def test_timeline_tie_break_by_hab():
    dice_service = MagicMock()
    # Ensure rolls don't cause infinite loop if logic is broken, but they should be unique anyway
    dice_service.roll_dice.return_value = RollResult(5, 5) 
    bm = BattleManager(dice_service=dice_service, data_service=MagicMock(), judge=MagicMock())
    
    char_high_hab = MagicMock()
    char_high_hab.char_id = "high_hab"
    char_high_hab.hab = 15
    char_high_hab.current_hp = 10
    char_high_hab.passive_abilities = []
    
    char_low_hab = MagicMock()
    char_low_hab.char_id = "low_hab"
    char_low_hab.hab = 10
    char_low_hab.current_hp = 10
    char_low_hab.passive_abilities = []
    
    # Add them both to the same tick
    bm.add_character(char_low_hab, controller=MagicMock(), start_tick=0)
    bm.add_character(char_high_hab, controller=MagicMock(), start_tick=0)
    
    # High HAB should act first
    first = bm.get_next_actor()
    second = bm.get_next_actor()
    
    assert first.char_id == "high_hab"
    assert second.char_id == "low_hab"

def test_timeline_tie_break_by_roll():
    dice_service = MagicMock()
    # Mock rolls: char1 gets 3, char2 gets 7
    dice_service.roll_dice.side_effect = [RollResult(3, 3), RollResult(7, 7)]
    
    bm = BattleManager(dice_service=dice_service, data_service=MagicMock(), judge=MagicMock())
    
    char1 = MagicMock()
    char1.char_id = "c1"
    char1.hab = 10
    char1.current_hp = 10
    char1.passive_abilities = []
    
    char2 = MagicMock()
    char2.char_id = "c2"
    char2.hab = 10
    char2.current_hp = 10
    char2.passive_abilities = []
    
    bm.add_character(char1, controller=MagicMock(), start_tick=0)
    bm.add_character(char2, controller=MagicMock(), start_tick=0)
    
    # Char2 should act first because of higher roll
    first = bm.get_next_actor()
    second = bm.get_next_actor()
    
    assert first.char_id == "c2"
    assert second.char_id == "c1"

def test_timeline_continuous_draw_resolution():
    dice_service = MagicMock()
    # First char rolls 5. 
    # Second char rolls 5 (draw), then rolls 5 (draw), then rolls 8 (unique).
    dice_service.roll_dice.side_effect = [
        RollResult(5, 5), # char1 roll
        RollResult(5, 5), # char2 roll 1 (tie)
        RollResult(5, 5), # char2 roll 2 (tie)
        RollResult(8, 8)  # char2 roll 3 (unique)
    ]
    
    bm = BattleManager(dice_service=dice_service, data_service=MagicMock(), judge=MagicMock())
    
    char1 = MagicMock()
    char1.char_id = "c1"
    char1.hab = 10
    char1.current_hp = 10
    char1.passive_abilities = []
    
    char2 = MagicMock()
    char2.char_id = "c2"
    char2.hab = 10
    char2.current_hp = 10
    char2.passive_abilities = []
    
    bm.add_character(char1, controller=MagicMock(), start_tick=0)
    bm.add_character(char2, controller=MagicMock(), start_tick=0)
    
    # Char2 should act first because 8 > 5
    first = bm.get_next_actor()
    second = bm.get_next_actor()
    
    assert first.char_id == "c2"
    assert second.char_id == "c1"

def test_delay_character_updates_tie_break():
    dice_service = MagicMock()
    # Initial rolls: c1: 5, c2: 8 (c2 first)
    # After delay: c1 at tick 10.
    dice_service.roll_dice.side_effect = [RollResult(5, 5), RollResult(8, 8), RollResult(3, 3)]
    
    bm = BattleManager(dice_service=dice_service, data_service=MagicMock(), judge=MagicMock())
    
    char1 = MagicMock()
    char1.char_id = "c1"
    char1.hab = 10
    char1.current_hp = 10
    char1.passive_abilities = []
    
    char2 = MagicMock()
    char2.char_id = "c2"
    char2.hab = 10
    char2.current_hp = 10
    char2.passive_abilities = []
    
    bm.add_character(char1, controller=MagicMock(), start_tick=0)
    bm.add_character(char2, controller=MagicMock(), start_tick=0)
    
    bm.delay_character(char1, 10)
    
    first = bm.get_next_actor()
    assert first.char_id == "c2"
    assert bm.current_tick == 0
    
    second = bm.get_next_actor()
    assert second.char_id == "c1"
    assert bm.current_tick == 10
