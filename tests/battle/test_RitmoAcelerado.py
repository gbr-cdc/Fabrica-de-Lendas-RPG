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

def test_ritmo_acelerado_consistent_activation(retalhador, target):
    bm = create_test_battle_manager()
    from controllers.CharacterController import CharacterController
    class DummyController(CharacterController):
        def choose_action(self, actor, context, action_load=None): pass
        def choose_reaction(self, actor, reaction_id, action_load, context): return True

    bm.add_character(retalhador, DummyController(), start_tick=100)
    bm.add_character(target, DummyController(), start_tick=200)

    # Fetch data-driven parameters [ARCH.TEST_QUALITY.DATA_INTEGRITY]
    params = bm.data_service.get_passive_template("Ritmo Acelerado").parameters
    threshold = params.get("threshold_roll", 5)

    actor = bm.get_next_actor() # should be retalhador
    assert actor.char_id == "retalhador1"

    # 1st Attack: roll threshold -> MOVE_ACTION
    bm.dice_service.schedule_result(threshold) # Atk roll
    bm.dice_service.schedule_result(2) # Def roll
    action1 = AttackAction(None, actor, [target], bm)
    load1 = bm.run_action(action1)
    
    assert action1.action_type == BattleActionType.MOVE_ACTION
    assert f"PASSIVE|Ritmo Acelerado|{actor.char_id}" in load1.history
    
    # 2nd Attack: roll threshold + 1 -> MOVE_ACTION
    bm.dice_service.schedule_result(threshold + 1) # Atk roll
    bm.dice_service.schedule_result(2) # Def roll
    action2 = AttackAction(None, actor, [target], bm)
    load2 = bm.run_action(action2)
    
    assert action2.action_type == BattleActionType.MOVE_ACTION
    assert f"PASSIVE|Ritmo Acelerado|{actor.char_id}" in load2.history

    # 3rd Attack: roll threshold -> MOVE_ACTION (No limit!)
    bm.dice_service.schedule_result(threshold) # Atk roll
    bm.dice_service.schedule_result(2) # Def roll
    action3 = AttackAction(None, actor, [target], bm)
    load3 = bm.run_action(action3)

    assert action3.action_type == BattleActionType.MOVE_ACTION
    assert f"PASSIVE|Ritmo Acelerado|{actor.char_id}" in load3.history
    
    # Verify no precision bonus tag exists
    assert not any("pre" in tag for tag in load3.history if "PASSIVE" not in tag)

def test_ritmo_acelerado_no_activation_below_threshold(retalhador, target):
    bm = create_test_battle_manager()
    from controllers.CharacterController import CharacterController
    class DummyController(CharacterController):
        def choose_action(self, actor, context, action_load=None): pass
        def choose_reaction(self, actor, reaction_id, action_load, context): return True

    bm.add_character(retalhador, DummyController(), start_tick=100)
    bm.add_character(target, DummyController(), start_tick=200)

    actor = bm.get_next_actor()
    params = bm.data_service.get_passive_template("Ritmo Acelerado").parameters
    threshold = params.get("threshold_roll", 5)

    # 1st Attack: roll below threshold
    bm.dice_service.schedule_result(threshold - 1)
    bm.dice_service.schedule_result(2)
    action1 = AttackAction(None, actor, [target], bm)
    load1 = bm.run_action(action1)
    
    assert action1.action_type == BattleActionType.STANDARD_ACTION
    assert f"PASSIVE|Ritmo Acelerado|{actor.char_id}" not in load1.history

