import pytest
from tests.utils.entity_factory import create_dummy_character
from tests.utils.test_utils import create_test_battle_manager
from battle.BattleActions import AttackAction, GenerateManaAction
from core.Structs import CombatStyle
from core.Enums import AttributeType, ArmorType, WeaponType, BattleActionType

@pytest.fixture
def retalhador():
    style = CombatStyle(name="Retalhador", atq_die=10, def_die=8, main_stat=AttributeType.HAB, armor_type=ArmorType.LIGHT, weapon_type=WeaponType.LIGHT_WEAPON)
    char = create_dummy_character(char_id="retalhador1", name="Retalhador", attributes=[3,3,3], combat_style=style, equipped=True)
    char.passive_abilities.append("Ritmo Acelerado")
    char.current_mp = 10
    char.floating_mp = 0
    return char

@pytest.fixture
def target1():
    style = CombatStyle(name="Dummy", atq_die=8, def_die=8, main_stat=AttributeType.FIS, armor_type=ArmorType.LIGHT, weapon_type=WeaponType.MEDIUM_WEAPON)
    return create_dummy_character(char_id="target1", name="Target1", attributes=[3,3,3], combat_style=style, equipped=True)

@pytest.fixture
def target2():
    style = CombatStyle(name="Dummy", atq_die=8, def_die=8, main_stat=AttributeType.FIS, armor_type=ArmorType.LIGHT, weapon_type=WeaponType.MEDIUM_WEAPON)
    return create_dummy_character(char_id="target2", name="Target2", attributes=[3,3,3], combat_style=style, equipped=True)

def test_ritmo_acelerado_consistent_activation(retalhador, target1):
    bm = create_test_battle_manager()
    from controllers.CharacterController import CharacterController
    class DummyController(CharacterController):
        def choose_action(self, actor, context): pass
        def choose_reaction(self, actor, reaction_id, action_load, context): return True

    bm.add_character(retalhador, DummyController(), start_tick=100)
    bm.add_character(target1, DummyController(), start_tick=200)

    params = bm.data_service.get_passive_template("Ritmo Acelerado").parameters
    threshold = params.get("threshold_roll", 5)

    actor = bm.get_next_actor()

    # Attack: roll threshold -> MOVE_ACTION
    bm.dice_service.schedule_result(threshold) # Atk roll
    bm.dice_service.schedule_result(2) # Def roll
    action1 = AttackAction(None, actor, [target1], bm)
    load1 = bm.run_action(action1)
    
    assert action1.action_type == BattleActionType.MOVE_ACTION
    assert f"PASSIVE|Ritmo Acelerado|{actor.char_id}" in load1.history

def test_ritmo_acelerado_pre_bonus_accumulates(retalhador, target1):
    bm = create_test_battle_manager()
    from controllers.CharacterController import CharacterController
    class DummyController(CharacterController):
        def choose_action(self, actor, context): pass
        def choose_reaction(self, actor, reaction_id, action_load, context): return True

    bm.add_character(retalhador, DummyController(), start_tick=100)
    bm.add_character(target1, DummyController(), start_tick=200)

    actor = bm.get_next_actor()

    # Attack 1: Hits, no bonus yet, establishes target.
    bm.dice_service.schedule_result(6) # atk
    bm.dice_service.schedule_result(2) # def
    action1 = AttackAction(None, actor, [target1], bm)
    load1 = bm.run_action(action1)
    
    assert f"HIT|{target1.char_id}" in load1.history
    assert not any("ATK_LOAD|pre" in tag for tag in load1.history)

    # Re-fetch actor
    actor = bm.get_next_actor()

    # Attack 2: Has +1 pre bonus
    bm.dice_service.schedule_result(6)
    bm.dice_service.schedule_result(2)
    action2 = AttackAction(None, actor, [target1], bm)
    load2 = bm.run_action(action2)
    
    assert f"ATK_LOAD|pre|1|{actor.pre + 1}" in load2.history

    # Re-fetch actor
    actor = bm.get_next_actor()

    # Attack 3: Has +2 pre bonus
    bm.dice_service.schedule_result(6)
    bm.dice_service.schedule_result(2)
    action3 = AttackAction(None, actor, [target1], bm)
    load3 = bm.run_action(action3)
    
    assert f"ATK_LOAD|pre|2|{actor.pre + 2}" in load3.history

def test_ritmo_acelerado_miss_clears_bonus(retalhador, target1):
    bm = create_test_battle_manager()
    from controllers.CharacterController import CharacterController
    class DummyController(CharacterController):
        def choose_action(self, actor, context): pass
        def choose_reaction(self, actor, reaction_id, action_load, context): return True

    bm.add_character(retalhador, DummyController(), start_tick=100)
    bm.add_character(target1, DummyController(), start_tick=200)

    actor = bm.get_next_actor()

    # Attack 1: Hits
    bm.dice_service.schedule_result(8)
    bm.dice_service.schedule_result(2)
    bm.run_action(AttackAction(None, actor, [target1], bm))
    
    actor = bm.get_next_actor()

    # Attack 2: Hits (bonus +1 applied)
    bm.dice_service.schedule_result(8)
    bm.dice_service.schedule_result(2)
    load2 = bm.run_action(AttackAction(None, actor, [target1], bm))
    assert f"ATK_LOAD|pre|1|{actor.pre + 1}" in load2.history

    actor = bm.get_next_actor()

    # Attack 3: Misses
    bm.dice_service.schedule_result(1) # Miss
    bm.dice_service.schedule_result(8)
    load3 = bm.run_action(AttackAction(None, actor, [target1], bm))
    assert f"MISS|{target1.char_id}" in load3.history
    assert f"ATK_LOAD|pre|2|{actor.pre + 2}" in load3.history # bonus applies before miss

    actor = bm.get_next_actor()

    # Attack 4: Bonus should be reset
    bm.dice_service.schedule_result(6)
    bm.dice_service.schedule_result(2)
    load4 = bm.run_action(AttackAction(None, actor, [target1], bm))
    assert not any("ATK_LOAD|pre" in tag for tag in load4.history)

def test_ritmo_acelerado_different_target_clears_bonus(retalhador, target1, target2):
    bm = create_test_battle_manager()
    from controllers.CharacterController import CharacterController
    class DummyController(CharacterController):
        def choose_action(self, actor, context): pass
        def choose_reaction(self, actor, reaction_id, action_load, context): return True

    bm.add_character(retalhador, DummyController(), start_tick=100)
    bm.add_character(target1, DummyController(), start_tick=200)
    bm.add_character(target2, DummyController(), start_tick=201)

    actor = bm.get_next_actor()

    # Attack 1 -> Target 1: Hits
    bm.dice_service.schedule_result(8)
    bm.dice_service.schedule_result(2)
    bm.run_action(AttackAction(None, actor, [target1], bm))

    actor = bm.get_next_actor()

    # Attack 2 -> Target 2: Bonus should be 0 because target changed
    bm.dice_service.schedule_result(8)
    bm.dice_service.schedule_result(2)
    load2 = bm.run_action(AttackAction(None, actor, [target2], bm))
    
    assert not any("ATK_LOAD|pre" in tag for tag in load2.history)

def test_ritmo_acelerado_non_attack_action_clears_bonus(retalhador, target1):
    bm = create_test_battle_manager()
    from controllers.CharacterController import CharacterController
    class DummyController(CharacterController):
        def choose_action(self, actor, context): pass
        def choose_reaction(self, actor, reaction_id, action_load, context): return True

    bm.add_character(retalhador, DummyController(), start_tick=100)
    bm.add_character(target1, DummyController(), start_tick=200)

    actor = bm.get_next_actor()

    # Attack 1: Hits
    bm.dice_service.schedule_result(8)
    bm.dice_service.schedule_result(2)
    bm.run_action(AttackAction(None, actor, [target1], bm))

    actor = bm.get_next_actor()

    # Non-attack action (Generate Mana)
    action_mana = GenerateManaAction(actor, [], bm)
    load_mana = bm.run_action(action_mana)
    assert load_mana.success

    actor = bm.get_next_actor()

    # Attack 2: Bonus should be cleared
    bm.dice_service.schedule_result(8)
    bm.dice_service.schedule_result(2)
    load3 = bm.run_action(AttackAction(None, actor, [target1], bm))
    
    assert not any("ATK_LOAD|pre" in tag for tag in load3.history)
