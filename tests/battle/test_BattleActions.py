import pytest
from battle.BattleActions import AttackAction, GenerateManaAction, GenerateFocusAction, EFFECT_HOOK_BUILDERS
from core.Events import ActionLoad, AttackLoad
from core.Structs import AttackActionTemplate, AttackEffects
from core.Enums import BattleActionType, AttackType
from tests.utils.entity_factory import create_dummy_character
from tests.utils.test_utils import create_test_battle_manager
from unittest.mock import MagicMock

def test_generate_mana_action():
    actor = create_dummy_character()
    actor.current_mp = 5
    actor.rules.limite_mana = 2
    actor.men = 10 
    actor.floating_mp = 0
    
    manager = create_test_battle_manager()
    manager.add_character(actor, MagicMock())
    
    # Setup for run_action: actor must be out of timeline
    manager.get_next_actor()
    
    action = GenerateManaAction(actor, targets=[actor], context=manager)
    
    can_exec, msg = action.can_execute()
    assert can_exec is True
    
    load = manager.run_action(action)
    
    assert any("MANA_T|" in h for h in load.history)
    assert any("MANA_F|" in h for h in load.history)
    assert actor.current_mp == 0 
    assert actor.floating_mp == 5 

def test_generate_focus_action():
    actor = create_dummy_character()
    actor.rules.limite_foco = 3
    actor.men = 10 
    actor.floating_focus = 0
    
    manager = create_test_battle_manager()
    manager.add_character(actor, MagicMock())
    manager.get_next_actor()
    
    action = GenerateFocusAction(actor, targets=[actor], context=manager)
    
    can_exec, msg = action.can_execute()
    assert can_exec is True
    
    load = manager.run_action(action)
    assert any("FOCUS|" in h for h in load.history)
    assert actor.floating_focus == 10

def test_attack_action_execution_flow():
    manager = create_test_battle_manager()
    actor = create_dummy_character(char_id="actor", attributes=[10, 10, 10])
    actor.floating_focus = 10
    
    target = create_dummy_character(char_id="target", attributes=[10, 10, 10])
    target.current_hp = 100
    
    manager.add_character(actor, MagicMock())
    manager.add_character(target, MagicMock())
    
    # Ensure actor is first
    manager.set_tick(actor, 0)
    manager.set_tick(target, 10)
    
    manager.dice_service.schedule_result(10) # atk
    manager.dice_service.schedule_result(5)  # def
    
    template = manager.get_template("SkillN1")
    
    actor = manager.get_next_actor()
    action = AttackAction(template, actor, [target], manager)
    
    hooks = action.get_hooks()
    assert "on_damage_calculation" in hooks
    
    action_load = manager.run_action(action)
    
    atk_die = actor.atk_die
    def_die = target.def_die
    history_str = "|".join(action_load.history)
    assert "EXEC|Habilidade Nível 1|actor" in history_str
    assert f"ROLL|ATK|10|{atk_die}|actor" in history_str
    assert f"ROLL|DEF|5|{def_die}|target" in history_str 
    assert "HIT|target" in history_str
    assert "DMG|target" in history_str
    assert "HP|target" in history_str

    assert target.current_hp < 100

def test_attack_action_can_execute_failures():
    manager = create_test_battle_manager()
    actor = create_dummy_character()
    actor.floating_focus = 0
    target = create_dummy_character()
    
    template = manager.get_template("SkillN1")
    action = AttackAction(template, actor, [target], manager)
    
    can, msg = action.can_execute()
    assert can is False
    assert "insuficiente" in msg

    actor.floating_focus = 10
    target.current_hp = 0
    can, msg = action.can_execute()
    assert can is False
    assert "derrotado" in msg

def test_attack_action_gda_hook():
    manager = create_test_battle_manager()
    actor = create_dummy_character()
    template = manager.get_template("SkillN1")
    action = AttackAction(template, actor, [], manager)
    hooks = action.get_hooks()
    
    load = ActionLoad(character=actor)
    load.gda = 0
    load.history = []
    
    hooks["on_damage_calculation"](load)
    assert load.gda == 5
    assert "ACTION_HOOK|Habilidade Nível 1|dummy_01" in load.history[0]
    assert "ATK_LOAD|gda|5|5" in load.history[1]

def test_attack_action_execute_miss():
    manager = create_test_battle_manager()
    actor = create_dummy_character(attributes=[1, 1, 1])
    actor.floating_focus = 10
    
    target = create_dummy_character(char_id="target", attributes=[15, 15, 15])
    
    manager.add_character(actor, MagicMock())
    manager.add_character(target, MagicMock())
    manager.get_next_actor()
    
    manager.dice_service.schedule_result(1) # atk
    manager.dice_service.schedule_result(20) # def
    
    action = AttackAction(None, actor, [target], manager)
    
    action_load = manager.run_action(action)
    
    history_str = "|".join(action_load.history)
    assert "MISS|target" in history_str

def test_generate_mana_action_failures():
    manager = create_test_battle_manager()
    actor = create_dummy_character()
    actor.current_mp = 0
    action = GenerateManaAction(actor, targets=[actor], context=manager)
    
    can, msg = action.can_execute()
    assert can is False
    assert "esgotou" in msg
    
    actor.current_mp = 10
    actor.rules.limite_mana = 1
    actor.men = 5
    actor.floating_mp = 5
    can, msg = action.can_execute()
    assert can is False
    assert "limite" in msg

def test_generate_focus_action_failures():
    manager = create_test_battle_manager()
    actor = create_dummy_character()
    actor.rules.limite_foco = 1
    actor.men = 5
    actor.floating_focus = 5
    action = GenerateFocusAction(actor, targets=[actor], context=manager)
    
    can, msg = action.can_execute()
    assert can is False
    assert "limite" in msg

def test_attack_action_uses_registry():
    manager = create_test_battle_manager()
    def dummy_builder(effect, action):
        def dummy_hook(load):
            load.dummy_triggered = True
        return {"on_hit_check": dummy_hook}
    
    EFFECT_HOOK_BUILDERS["dummy_effect"] = dummy_builder
    
    try:
        actor = create_dummy_character()
        template = AttackActionTemplate(
            nome="T", action_type=BattleActionType.STANDARD_ACTION, 
            attack_type=AttackType.BASIC_ATTACK, focus_cost=0, 
            effects=[AttackEffects("dummy_effect", {})]
        )
        action = AttackAction(template, actor, [], manager)
        
        hooks = action.get_hooks()
        assert "on_hit_check" in hooks
        load = MagicMock()
        hooks["on_hit_check"](load)
        assert load.dummy_triggered is True
    finally:
        del EFFECT_HOOK_BUILDERS["dummy_effect"]

def test_attack_action_multi_target():
    manager = create_test_battle_manager()
    actor = create_dummy_character(char_id="Attacker")
    actor.floating_focus = 10
    t1 = create_dummy_character(char_id="T1")
    t2 = create_dummy_character(char_id="T2")
    
    manager.add_character(actor, MagicMock())
    manager.add_character(t1, MagicMock())
    manager.add_character(t2, MagicMock())
    manager.get_next_actor()
    
    manager.dice_service.schedule_result(10)
    manager.dice_service.schedule_result(5)
    manager.dice_service.schedule_result(10)
    manager.dice_service.schedule_result(5)
    
    action = AttackAction(None, actor, [t1, t2], manager)
    
    result = manager.run_action(action)
    
    history_str = "\n".join(result.history)
    assert "HIT|T1" in history_str
    assert "HIT|T2" in history_str

def test_attack_action_one_dead():
    manager = create_test_battle_manager()
    actor = create_dummy_character(char_id="Attacker")
    actor.floating_focus = 10
    
    t_dead = create_dummy_character(char_id="dead")
    t_dead.current_hp = 0
    t_alive = create_dummy_character(char_id="alive")
    
    manager.add_character(actor, MagicMock())
    manager.add_character(t_dead, MagicMock())
    manager.add_character(t_alive, MagicMock())
    manager.get_next_actor()
    
    manager.dice_service.schedule_result(10)
    manager.dice_service.schedule_result(5)
    
    action = AttackAction(None, actor, [t_dead, t_alive], manager)
    
    result = manager.run_action(action)
    
    history_str = "\n".join(result.history)
    assert "HIT|alive" in history_str
    assert "dead" not in history_str

def test_area_attack_one_roll_multiple_targets():
    manager = create_test_battle_manager()
    actor = create_dummy_character(char_id="actor")
    actor.floating_focus = 10
    target1 = create_dummy_character(char_id="target1")
    target2 = create_dummy_character(char_id="target2")
    
    manager.add_character(actor, MagicMock())
    manager.add_character(target1, MagicMock())
    manager.add_character(target2, MagicMock())
    manager.get_next_actor()
    
    manager.dice_service.schedule_result(10) # actor roll
    manager.dice_service.schedule_result(5)  # target1 roll
    manager.dice_service.schedule_result(5)  # target2 roll
    
    template = manager.get_template("AreaAttack")
    action = AttackAction(template, actor, [target1, target2], manager)
    
    manager.run_action(action)
    
    # In AREA attack, dice_service should be called only once for the attacker
    assert len(manager.dice_service.queue) == 0

def test_area_attack_postura_defensiva_no_crash():
    from battle.BattlePassives import PosturaDefensiva
    
    manager = create_test_battle_manager()
    actor = create_dummy_character(char_id="actor")
    owner = create_dummy_character(char_id="owner")
    
    manager.add_character(actor, MagicMock())
    manager.add_character(owner, MagicMock())
    manager.get_next_actor()
    
    manager.dice_service.schedule_result(10) # master roll
    manager.dice_service.schedule_result(5)  # owner def
    
    passive = PosturaDefensiva(owner, manager)
    passive.is_active = True
    passive._tracked_targets["actor"] = False # Owner is watching actor
    
    # Register passive hooks
    hooks = passive.get_hooks()
    for ev, func in hooks.items():
        manager.subscribe(ev, func)
    
    template = manager.get_template("AreaAttack")
    action = AttackAction(template, actor, [owner], manager)
    manager.run_action(action)
