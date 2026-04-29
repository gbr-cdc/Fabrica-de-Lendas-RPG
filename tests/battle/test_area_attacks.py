import pytest
from battle.BattleActions import AttackAction
from core.Structs import AttackActionTemplate, RollResult
from core.Enums import BattleActionType, AttackType, RollState
from tests.utils.entity_factory import create_dummy_character
from core.DiceManager import DiceManager
from unittest.mock import MagicMock

def test_area_attack_one_roll_multiple_targets():
    actor = create_dummy_character(char_id="actor", attributes=[10, 10, 10]) # Rank 2
    actor.floating_focus = 10
    
    target1 = create_dummy_character(char_id="target1", attributes=[10, 10, 10]) # Rank 2
    target2 = create_dummy_character(char_id="target2", attributes=[10, 10, 10]) # Rank 2
    
    dice = DiceManager(seed=42)
    dice.schedule_result(10) # actor roll
    dice.schedule_result(5)  # target1 roll
    dice.schedule_result(5)  # target2 roll
    
    context = MagicMock()
    context.dice_service = dice
    
    template = AttackActionTemplate(
        id="AreaAtk", nome="Area Atk", 
        action_type=BattleActionType.STANDARD_ACTION, 
        attack_type=AttackType.AREA, 
        focus_cost=5,
        effects=[]
    )
    
    action = AttackAction(template, actor, [target1, target2], context)
    action.execute()
    
    # In AREA attack, dice_service should be called only once for the attacker
    # However, DiceManager.roll_dice was called 3 times total (1 atk, 2 def)
    assert len(dice.queue) == 0

def test_standard_attack_multiple_rolls_multiple_targets():
    actor = create_dummy_character(char_id="actor")
    target1 = create_dummy_character(char_id="target1")
    target2 = create_dummy_character(char_id="target2")
    
    dice = DiceManager(seed=42)
    dice.schedule_result(10) # actor roll for t1
    dice.schedule_result(10) # t1 roll
    dice.schedule_result(10) # actor roll for t2
    dice.schedule_result(10) # t2 roll
    
    context = MagicMock()
    context.dice_service = dice
    
    template = AttackActionTemplate(
        id="StdAtk", nome="Std Atk", 
        action_type=BattleActionType.STANDARD_ACTION, 
        attack_type=AttackType.BASIC_ATTACK, 
        focus_cost=0,
        effects=[]
    )
    
    action = AttackAction(template, actor, [target1, target2], context)
    action.execute()
    
    assert len(dice.queue) == 0

def test_area_attack_postura_defensiva_no_crash():
    from battle.BattlePassives import PosturaDefensiva
    
    actor = create_dummy_character(char_id="actor")
    owner = create_dummy_character(char_id="owner")
    
    dice = DiceManager(seed=42)
    dice.schedule_result(10) # master roll
    dice.schedule_result(5)  # owner def
    
    context = MagicMock()
    context.dice_service = dice
    context.get_characters.return_value = [actor, owner]
    
    passive = PosturaDefensiva(owner, context)
    passive.is_active = True
    passive._tracked_targets["actor"] = False # Owner is watching actor
    
    # Register passive hooks in context mock
    hooks = passive.get_hooks()
    def mock_emit(event, load):
        if event in hooks:
            hooks[event](load)
    context.emit.side_effect = mock_emit
    
    template = AttackActionTemplate(
        id="AreaAtk", nome="Area Atk", 
        action_type=BattleActionType.STANDARD_ACTION, 
        attack_type=AttackType.AREA, 
        focus_cost=0,
        effects=[]
    )
    
    action = AttackAction(template, actor, [owner], context)
    # This should NOT crash when master roll emits 'on_roll_modify' with target=None
    action.execute()

