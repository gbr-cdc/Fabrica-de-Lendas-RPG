import pytest
from unittest.mock import MagicMock
from battle.BattleManager import BattleManager
from battle.Judges import BattleJudge
from core.Enums import BattleState, RollState, BattleActionType
from core.Structs import BattleResult
from core.Events import ActionLoad
from core.BaseClasses import StatusEffect
from controllers.CharacterController import PvP1v1Controller
from tests.utils.entity_factory import create_dummy_character

def test_battle_judge_defeat():
    judge = BattleJudge()
    context = MagicMock()
    
    char1 = create_dummy_character(char_id="char1", team=1)
    char1.current_hp = 0
    
    char2 = create_dummy_character(char_id="char2", team=2)
    char2.current_hp = 10
    
    context.get_characters.return_value = [char2]
    context.get_graveyard.return_value = [char1]
    result = BattleResult()
    
    assert judge.rule(context, result) == BattleState.DEFEAT
    assert char2 in result.winners
    assert char1 in result.losers

def test_battle_judge_draw():
    judge = BattleJudge()
    context = MagicMock()
    
    char1 = create_dummy_character(char_id="char1", team=1)
    char1.current_hp = 0
    
    char2 = create_dummy_character(char_id="char2", team=2)
    char2.current_hp = 0
    
    context.get_characters.return_value = []
    context.get_graveyard.return_value = [char1, char2]
    result = BattleResult()
    
    assert judge.rule(context, result) == BattleState.DRAW
    assert len(result.winners) == 0
    assert char1 in result.losers
    assert char2 in result.losers

def test_battle_manager_get_controller():
    bm = BattleManager(MagicMock(), MagicMock(), MagicMock())
    ctrl = MagicMock()
    bm.controllers["test"] = ctrl
    assert bm.get_controller("test") == ctrl
    assert bm.get_controller("none") is None

def test_battle_manager_remove_non_existent():
    bm = BattleManager(MagicMock(), MagicMock(), MagicMock())
    bm.remove_character("none")

def test_battle_manager_run_battle_empty_timeline():
    judge = MagicMock()
    judge.rule.return_value = BattleState.RUNNING
    bm = BattleManager(MagicMock(), MagicMock(), judge)
    bm.timeline = []
    
    bm.run_battle()
    assert bm.battle_state == BattleState.ERROR
    assert "ERR|TIMELINE_EMPTY" in bm.battle_result.history[0]

def test_battle_manager_decision_loop():
    judge = MagicMock()
    judge.rule.side_effect = [BattleState.RUNNING, BattleState.VICTORY]
    bm = BattleManager(MagicMock(), MagicMock(), judge)
    
    actor = create_dummy_character(char_id="actor")
    
    controller = MagicMock()
    failed_action = MagicMock()
    failed_action.execute_if_possible.return_value = ActionLoad(character=actor, success=False)
    controller.choose_action.return_value = failed_action
    
    bm.add_character(actor, controller)
    bm.run_battle()
    
    assert bm.battle_state == BattleState.ERROR
    assert "ERR|DECISION_LOOP|actor" in bm.battle_result.history[1]

def test_battle_manager_resolve_deaths():
    judge = MagicMock()
    judge.rule.return_value = BattleState.VICTORY
    bm = BattleManager(MagicMock(), MagicMock(), judge)
    
    actor = create_dummy_character(char_id="dead")
    actor.current_hp = 0
    
    bm.characters["dead"] = actor
    bm.controllers["dead"] = MagicMock()
    
    bm.resolve_deaths()
    
    assert "dead" not in bm.characters
    assert "dead" in bm.graveyard
    assert "DEATH|dead" in bm.battle_result.history[0]

def test_battle_manager_passive_management():
    bm = BattleManager(MagicMock(), MagicMock(), MagicMock())
    actor = create_dummy_character(char_id="actor")
    actor.passive_abilities = ["GraçaDoDuelista"]
    
    bm.add_character(actor, MagicMock())
    assert "actor" in bm.active_passives
    
    bm.remove_character("actor")
    assert "actor" not in bm.active_passives

def test_pvp_controller_special_paths():
    ctrl = PvP1v1Controller()
    actor = create_dummy_character(char_id="actor")
    context = MagicMock()
    
    context.get_characters.return_value = [actor]
    with pytest.raises(RuntimeError):
        ctrl.choose_action(actor, context)
        
    assert ctrl.choose_reaction(actor, "any", MagicMock(), context) is True

def test_battle_manager_move_action_cost():
    judge = MagicMock()
    judge.rule.side_effect = [BattleState.RUNNING, BattleState.VICTORY]
    bm = BattleManager(MagicMock(), MagicMock(), judge)
    
    actor = create_dummy_character(char_id="actor")
    actor.action_cost_base = 100
    
    action = MagicMock()
    action.action_type = BattleActionType.MOVE_ACTION
    action.execute_if_possible.return_value = ActionLoad(character=actor, success=True)
    
    controller = MagicMock()
    controller.choose_action.return_value = action
    
    bm.add_character(actor, controller)
    bm.run_battle()
    
    assert bm.timeline[0][0] == 50

def test_battle_manager_get_methods():
    bm = BattleManager(MagicMock(), MagicMock(), MagicMock())
    bm.get_template("test")
    actor = create_dummy_character(char_id="actor")
    bm.characters["actor"] = actor
    chars = bm.get_characters()
    assert actor in chars

def test_battle_manager_decision_retry_loop():
    judge = MagicMock()
    judge.rule.side_effect = [BattleState.RUNNING, BattleState.VICTORY]
    bm = BattleManager(MagicMock(), MagicMock(), judge)
    
    actor = create_dummy_character(char_id="actor")
    
    controller = MagicMock()
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
