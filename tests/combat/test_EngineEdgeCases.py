
import pytest
from unittest.mock import MagicMock
from combat.BattleManager import BattleManager
from combat.Judges import BattleJudge
from core.Enums import BattleState, RollState, BattleActionType
from core.Events import ActionLoad
from combat.StatusEffects import StatusEffect
from controllers.CharacterController import PvP1v1Controller

def test_battle_judge_defeat():
    judge = BattleJudge()
    context = MagicMock()
    
    char1 = MagicMock()
    char1.team = 1
    char1.current_hp = 0
    
    char2 = MagicMock()
    char2.team = 2
    char2.current_hp = 10
    
    context.get_characters.return_value = [char1, char2]
    
    assert judge.rule(context) == BattleState.DEFEAT

def test_battle_judge_draw():
    judge = BattleJudge()
    context = MagicMock()
    
    char1 = MagicMock()
    char1.team = 1
    char1.current_hp = 0
    
    char2 = MagicMock()
    char2.team = 2
    char2.current_hp = 0
    
    context.get_characters.return_value = [char1, char2]
    
    assert judge.rule(context) == BattleState.DRAW

def test_battle_manager_get_controller():
    bm = BattleManager(MagicMock(), MagicMock(), MagicMock())
    ctrl = MagicMock()
    bm.controllers["test"] = ctrl
    assert bm.get_controller("test") == ctrl
    assert bm.get_controller("none") is None

def test_battle_manager_remove_non_existent():
    bm = BattleManager(MagicMock(), MagicMock(), MagicMock())
    # Should not raise error
    bm.remove_character("none")

def test_battle_manager_run_battle_empty_timeline():
    judge = MagicMock()
    judge.rule.return_value = BattleState.RUNNING
    bm = BattleManager(MagicMock(), MagicMock(), judge)
    bm.timeline = [] # Empty
    
    bm.run_battle()
    assert bm.battle_state == BattleState.ERROR
    assert "Timeline se tornou vazia" in bm.battle_result.history[0]

def test_battle_manager_decision_loop():
    judge = MagicMock()
    judge.rule.side_effect = [BattleState.RUNNING, BattleState.VICTORY]
    bm = BattleManager(MagicMock(), MagicMock(), judge)
    
    actor = MagicMock()
    actor.char_id = "actor"
    actor.name = "Actor"
    actor.current_hp = 50
    actor.current_hp = 100
    actor.action_cost_base = 10
    
    controller = MagicMock()
    # Return a failed action repeatedly
    failed_action = MagicMock()
    failed_action.execute_if_possible.return_value = ActionLoad(character=actor, success=False)
    controller.choose_action.return_value = failed_action
    
    bm.add_character(actor, controller)
    
    # We need to mock the timeline since add_character adds it
    bm.run_battle()
    
    assert bm.battle_state == BattleState.ERROR
    assert "decision loop" in bm.battle_result.history[0]

def test_battle_manager_resolve_deaths():
    judge = MagicMock()
    judge.rule.return_value = BattleState.VICTORY
    bm = BattleManager(MagicMock(), MagicMock(), judge)
    
    actor = MagicMock()
    actor.char_id = "dead"
    actor.name = "DeadActor"
    actor.current_hp = 0
    actor.current_hp = 0
    
    bm.characters["dead"] = actor
    bm.controllers["dead"] = MagicMock()
    
    bm.resolve_deaths()
    
    assert "dead" not in bm.characters
    assert "dead" in bm.graveyard
    assert "[MORTE]" in bm.battle_result.history[0]

def test_battle_manager_passive_management():
    bm = BattleManager(MagicMock(), MagicMock(), MagicMock())
    actor = MagicMock()
    actor.char_id = "actor"
    actor.passive_abilities = ["GraçaDoDuelista"]
    
    # We need the registry to have it
    bm.add_character(actor, MagicMock())
    assert "actor" in bm.active_passives
    
    bm.remove_character("actor")
    assert "actor" not in bm.active_passives

def test_status_effect_base():
    target = MagicMock()
    context = MagicMock()
    effect = StatusEffect("Base", 1, target, context)
    assert effect.on_get_hooks() == {}
    effect.on_remove() # Coverage for pass

def test_pvp_controller_special_paths():
    ctrl = PvP1v1Controller()
    actor = MagicMock()
    context = MagicMock()
    
    # No targets
    context.get_characters.return_value = [actor]
    with pytest.raises(RuntimeError):
        ctrl.choose_action(actor, context)
        
    # Reaction always True
    assert ctrl.choose_reaction(actor, "any", MagicMock(), context) is True

def test_battle_manager_move_action_cost():
    judge = MagicMock()
    judge.rule.side_effect = [BattleState.RUNNING, BattleState.VICTORY]
    bm = BattleManager(MagicMock(), MagicMock(), judge)
    
    actor = MagicMock()
    actor.char_id = "actor"
    actor.current_hp = 100
    actor.current_hp = 100
    actor.action_cost_base = 100
    
    action = MagicMock()
    action.action_type = BattleActionType.MOVE_ACTION
    action.execute_if_possible.return_value = ActionLoad(character=actor, success=True)
    
    controller = MagicMock()
    controller.choose_action.return_value = action
    
    bm.add_character(actor, controller)
    bm.run_battle()
    
    # Check next tick in timeline. Should be 50 (100 // 2)
    # Timeline contains (tick, char_id, char)
    assert bm.timeline[0][0] == 50

def test_battle_manager_get_methods():
    bm = BattleManager(MagicMock(), MagicMock(), MagicMock())
    bm.get_template("test")
    actor = MagicMock()
    actor.char_id = "actor"
    bm.characters["actor"] = actor
    chars = bm.get_characters()
    assert actor in chars

def test_battle_manager_decision_retry_loop():
    judge = MagicMock()
    judge.rule.side_effect = [BattleState.RUNNING, BattleState.VICTORY]
    bm = BattleManager(MagicMock(), MagicMock(), judge)
    
    actor = MagicMock()
    actor.char_id = "actor"
    actor.current_hp = 100
    actor.current_hp = 100
    actor.action_cost_base = 10
    
    controller = MagicMock()
    # 1. Fail first, 2. Succeed second
    fail_action = MagicMock()
    fail_action.get_hooks.return_value = {"on_turn_start": lambda x: None}
    fail_action.execute_if_possible.return_value = ActionLoad(character=actor, success=False)
    success_action = MagicMock()
    success_action.get_hooks.return_value = {"on_turn_end": lambda x: None}
    success_action.execute_if_possible.return_value = ActionLoad(character=actor, success=True)
    
    controller.choose_action.side_effect = [fail_action, success_action]
    
    bm.add_character(actor, controller)
    bm.run_battle()
    assert controller.choose_action.call_count == 2
