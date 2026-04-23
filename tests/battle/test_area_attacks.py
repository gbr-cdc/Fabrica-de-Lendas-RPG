import pytest
from unittest.mock import MagicMock, patch
from battle.BattleActions import AttackAction
from core.Structs import AttackActionTemplate, RollResult
from core.Enums import BattleActionType, AttackType, RollState

def test_area_attack_one_roll_multiple_targets():
    actor = MagicMock()
    actor.char_id = "actor"
    actor.name = "Actor"
    actor.floating_focus = 10
    actor.atk_die = 10
    actor.rank = 2
    actor.bda = 0
    actor.pre = 0
    actor.pda = 10
    actor.mda = 1
    actor.men = 10
    actor.rules.limite_foco = 3
    
    target1 = MagicMock()
    target1.char_id = "target1"
    target1.name = "Target 1"
    target1.current_hp = 10
    target1.def_die = 8
    target1.rank = 2
    target1.bdd = 0
    target1.grd = 0
    
    target2 = MagicMock()
    target2.char_id = "target2"
    target2.name = "Target 2"
    target2.current_hp = 10
    target2.def_die = 8
    target2.rank = 2
    target2.bdd = 0
    target2.grd = 0
    
    context = MagicMock()
    # Mock dice rolls: 
    # 1. Actor's attack roll (10)
    # 2. Targets' defense rolls (8)
    def mock_roll_dice(die, state):
        if die == actor.atk_die:
            return RollResult(final_roll=10, roll1=10, roll2=None)
        return RollResult(final_roll=5, roll1=5, roll2=None)
    
    context.dice_service.roll_dice.side_effect = mock_roll_dice
    
    template = AttackActionTemplate(
        id="AreaAtk", nome="Area Atk", 
        action_type=BattleActionType.STANDARD_ACTION, 
        attack_type=AttackType.AREA, 
        focus_cost=5,
        effects=[]
    )
    
    action = AttackAction(template, actor, [target1, target2], context)
    
    with patch('battle.BattleActions.CharacterSystem.spend_focus'), \
         patch('battle.BattleActions.CharacterSystem.is_alive', return_value=True), \
         patch('battle.BattleActions.CharacterSystem.take_damage'):
        
        action.execute()
        
        # Verify roll_dice calls for actor's attack die
        actor_rolls = [call for call in context.dice_service.roll_dice.call_args_list if call.args[0] == actor.atk_die]
        # In current implementation, this should be 2, but we want it to be 1.
        assert len(actor_rolls) == 1, f"Expected 1 actor roll, got {len(actor_rolls)}"

def test_standard_attack_multiple_rolls_multiple_targets():
    actor = MagicMock()
    actor.char_id = "actor"
    actor.name = "Actor"
    actor.floating_focus = 10
    actor.atk_die = 10
    actor.rank = 2
    actor.bda = 0
    actor.pre = 0
    actor.pda = 10
    actor.mda = 1
    actor.men = 10
    actor.rules.limite_foco = 3
    
    target1 = MagicMock()
    target1.char_id = "target1"
    target1.name = "T1"
    target1.def_die = 8
    target1.rank = 2
    target1.bdd = 0
    target1.grd = 0
    
    target2 = MagicMock()
    target2.char_id = "target2"
    target2.name = "T2"
    target2.def_die = 8
    target2.rank = 2
    target2.bdd = 0
    target2.grd = 0
    
    context = MagicMock()
    def mock_roll_dice(die, state):
        return RollResult(final_roll=10, roll1=10, roll2=None)
    context.dice_service.roll_dice.side_effect = mock_roll_dice
    
    template = AttackActionTemplate(
        id="StdAtk", nome="Std Atk", 
        action_type=BattleActionType.STANDARD_ACTION, 
        attack_type=AttackType.BASIC_ATTACK, 
        focus_cost=0,
        effects=[]
    )
    
    action = AttackAction(template, actor, [target1, target2], context)
    
    with patch('battle.BattleActions.CharacterSystem.spend_focus'), \
         patch('battle.BattleActions.CharacterSystem.is_alive', return_value=True), \
         patch('battle.BattleActions.CharacterSystem.take_damage'), \
         patch('battle.BattleActions.CharacterSystem.generate_focus'):
        
        action.execute()
        
        # In standard attack, actor rolls for EACH target
        actor_rolls = [call for call in context.dice_service.roll_dice.call_args_list if call.args[0] == actor.atk_die]
        assert len(actor_rolls) == 2, f"Expected 2 actor rolls for standard attack, got {len(actor_rolls)}"

def test_area_attack_postura_defensiva_no_crash():
    from battle.BattlePassives import PosturaDefensiva
    
    actor = MagicMock(char_id="actor", name="Actor", atk_die=10, rank=2, bda=0, pre=0, pda=10, mda=1, floating_focus=10, men=10)
    actor.rules.limite_foco = 3
    
    owner = MagicMock(char_id="owner", name="Owner", def_die=8, rank=2, bdd=0, grd=0)
    
    context = MagicMock()
    context.dice_service.roll_dice.return_value = RollResult(final_roll=10, roll1=10, roll2=None)
    context.get_characters.return_value = [actor, owner]
    
    passive = PosturaDefensiva(owner, context)
    passive.is_active = True
    passive._tracked_targets["actor"] = False # Owner is watching actor
    
    # Register passive hooks in context mock
    hooks = passive.get_hooks()
    # We need to simulate the emit calling the hook
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
    
    with patch('battle.BattleActions.CharacterSystem.spend_focus'), \
         patch('battle.BattleActions.CharacterSystem.is_alive', return_value=True), \
         patch('battle.BattleActions.CharacterSystem.take_damage'):
        
        # This should NOT crash when master roll emits 'on_roll_modify' with target=None
        action.execute()
        # If it reaches here without crash, it passed.
