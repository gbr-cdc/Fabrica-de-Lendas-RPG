import pytest
from tests.utils.entity_factory import create_dummy_character
from tests.utils.test_utils import create_test_battle_manager
from battle.BattleActions import AttackAction
from core.Structs import CombatStyle
from core.Enums import AttributeType, ArmorType, WeaponType, BattleActionType

@pytest.fixture
def retalhador():
    style = CombatStyle(name="Retalhador", atq_die=10, def_die=8, main_stat=AttributeType.HAB, armor_type=ArmorType.LIGHT, weapon_type=WeaponType.LIGHT_WEAPON)
    char = create_dummy_character(char_id="retalhador1", name="Retalhador", attributes=[3,3,3], combat_style=style, equipped=True)
    char.passive_abilities.append("Ritmo Acelerado")
    # Set high focus for attacks if needed, though basic attacks don't cost focus
    return char

@pytest.fixture
def target():
    style = CombatStyle(name="Dummy", atq_die=8, def_die=8, main_stat=AttributeType.FIS, armor_type=ArmorType.LIGHT, weapon_type=WeaponType.MEDIUM_WEAPON)
    char = create_dummy_character(char_id="target1", name="Target", attributes=[3,3,3], combat_style=style, equipped=True)
    return char

def test_ritmo_acelerado_triple_attack(retalhador, target):
    bm = create_test_battle_manager()
    from controllers.CharacterController import CharacterController
    class DummyController(CharacterController):
        def choose_action(self, actor, context, action_load=None): pass
        def choose_reaction(self, actor, reaction_id, action_load, context): return True

    bm.add_character(retalhador, DummyController(), start_tick=100)
    bm.add_character(target, DummyController(), start_tick=200)

    # Fetch data-driven parameters [ARCH.TEST_QUALITY.DATA_INTEGRITY]
    params = bm.data_service.get_passive_template("Ritmo Acelerado").parameters
    threshold = params.get("threshold_roll", 7)
    pre_bonus = params.get("pre_bonus", 2)

    # Need to simulate 3 attacks with specific rolls: threshold, threshold+1, threshold-2
    actor = bm.get_next_actor() # should be retalhador
    assert actor.char_id == "retalhador1"

    # 1st Attack: roll threshold
    bm.dice_service.schedule_result(threshold) # Atk roll
    bm.dice_service.schedule_result(2) # Def roll
    action1 = AttackAction(None, actor, [target], bm)
    load1 = bm.run_action(action1)
    
    assert action1.action_type == BattleActionType.MOVE_ACTION
    assert f"PASSIVE|Ritmo Acelerado|{actor.char_id}" in load1.history
    
    # 2nd Attack: roll threshold + 1
    bm.dice_service.schedule_result(threshold + 1) # Atk roll
    bm.dice_service.schedule_result(2) # Def roll
    action2 = AttackAction(None, actor, [target], bm)
    load2 = bm.run_action(action2)
    
    assert action2.action_type == BattleActionType.MOVE_ACTION
    assert f"PASSIVE|Ritmo Acelerado|{actor.char_id}" in load2.history

    # 3rd Attack: roll below threshold
    bm.dice_service.schedule_result(threshold - 2) # Atk roll
    bm.dice_service.schedule_result(2) # Def roll
    action3 = AttackAction(None, actor, [target], bm)
    load3 = bm.run_action(action3)

    assert action3.action_type == BattleActionType.STANDARD_ACTION
    assert f"PASSIVE|Ritmo Acelerado|{actor.char_id}" in load3.history
    assert f"ATK_LOAD|pre|{pre_bonus}|{actor.pre + pre_bonus}" in load3.history



def test_ritmo_acelerado_break(retalhador, target):
    bm = create_test_battle_manager()
    from controllers.CharacterController import CharacterController
    class DummyController(CharacterController):
        def choose_action(self, actor, context, action_load=None): pass
        def choose_reaction(self, actor, reaction_id, action_load, context): return True

    bm.add_character(retalhador, DummyController(), start_tick=100)
    bm.add_character(target, DummyController(), start_tick=200)

    actor = bm.get_next_actor()
    params = bm.data_service.get_passive_template("Ritmo Acelerado").parameters
    threshold = params.get("threshold_roll", 7)

    # 1st Attack: roll threshold
    bm.dice_service.schedule_result(threshold)
    bm.dice_service.schedule_result(2)
    action1 = AttackAction(None, actor, [target], bm)
    load1 = bm.run_action(action1)
    
    assert action1.action_type == BattleActionType.MOVE_ACTION

    # 2nd Attack: roll below threshold (break rhythm)
    bm.dice_service.schedule_result(threshold - 5)
    bm.dice_service.schedule_result(2)
    action2 = AttackAction(None, actor, [target], bm)
    load2 = bm.run_action(action2)
    
    assert action2.action_type == BattleActionType.STANDARD_ACTION

    # 3rd Attack: roll threshold + 2 (starts over)
    bm.dice_service.schedule_result(threshold + 2)
    bm.dice_service.schedule_result(2)
    action3 = AttackAction(None, actor, [target], bm)
    load3 = bm.run_action(action3)
    
    assert action3.action_type == BattleActionType.MOVE_ACTION

