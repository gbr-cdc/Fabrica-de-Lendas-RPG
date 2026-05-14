import pytest
from battle.BattleActions import AttackAction, GenerateManaAction, GenerateFocusAction, EFFECT_HOOK_BUILDERS
from core.Events import ActionLoad, AttackLoad
from core.Structs import AttackActionTemplate, AttackEffects
from core.Enums import BattleActionType, AttackType, RollState
from tests.utils.entity_factory import create_dummy_character
from tests.utils.test_utils import create_test_battle_manager
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_template(effect_id: str, params: dict, name: str = "Test Action") -> AttackActionTemplate:
    """Build a minimal AttackActionTemplate containing a single effect."""
    return AttackActionTemplate(
        nome=name,
        action_type=BattleActionType.STANDARD_ACTION,
        attack_type=AttackType.BASIC_ATTACK,
        focus_cost=0,
        effects=[AttackEffects(effect_id, params)],
    )


def _make_attack_load(actor, target=None) -> AttackLoad:
    """Construct a minimal AttackLoad for direct hook invocation tests."""
    return AttackLoad(
        character=actor,
        target=target,
        attack_type=AttackType.BASIC_ATTACK,
        attack_state=RollState.NEUTRAL,
        defense_state=RollState.NEUTRAL,
    )


# ---------------------------------------------------------------------------
# GenerateManaAction
# ---------------------------------------------------------------------------

def test_generate_mana_action():
    actor = create_dummy_character()
    actor.current_mp = 5
    actor.rules.limite_mana = 2
    actor.men = 10
    actor.floating_mp = 0

    manager = create_test_battle_manager()
    manager.add_character(actor, MagicMock())
    manager.get_next_actor()

    action = GenerateManaAction(actor, targets=[actor], context=manager)

    can_exec, msg = action.can_execute()
    assert can_exec is True

    load = manager.run_action(action)

    assert any("MANA_T|" in h for h in load.history)
    assert any("MANA_F|" in h for h in load.history)
    assert actor.current_mp == 0
    assert actor.floating_mp == 5


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


# ---------------------------------------------------------------------------
# GenerateFocusAction
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# AttackAction – can_execute validation
# ---------------------------------------------------------------------------

def test_attack_action_can_execute_no_target():
    manager = create_test_battle_manager()
    actor = create_dummy_character()
    actor.floating_focus = 10
    action = AttackAction(None, actor, [], manager)

    can, msg = action.can_execute()
    assert can is False


def test_attack_action_can_execute_focus_insufficient():
    manager = create_test_battle_manager()
    actor = create_dummy_character()
    actor.floating_focus = 0
    target = create_dummy_character()

    template = _make_template("add_bda", {"amount": 2})
    template.focus_cost = 5
    action = AttackAction(template, actor, [target], manager)

    can, msg = action.can_execute()
    assert can is False
    assert "insuficiente" in msg


def test_attack_action_can_execute_all_dead():
    manager = create_test_battle_manager()
    actor = create_dummy_character()
    actor.floating_focus = 10
    target = create_dummy_character()
    target.current_hp = 0

    action = AttackAction(None, actor, [target], manager)
    can, msg = action.can_execute()
    assert can is False
    assert "derrotado" in msg


# ---------------------------------------------------------------------------
# Effect Hook: add_bda  [ARCH.TEST_QUALITY.EFFECT_HOOKS]
# ---------------------------------------------------------------------------

def test_add_bda_hook_registered():
    assert "add_bda" in EFFECT_HOOK_BUILDERS


def test_add_bda_hook_modifies_bda():
    """add_bda hook increments attack_load.bda by the configured amount."""
    manager = create_test_battle_manager()
    actor = create_dummy_character(char_id="actor")

    template = _make_template("add_bda", {"amount": 3})
    action = AttackAction(template, actor, [], manager)
    hooks = action.get_hooks()

    assert "on_roll_modify" in hooks

    load = _make_attack_load(actor)
    load.bda = 0
    hooks["on_roll_modify"](load)

    assert load.bda == 3
    assert any("ATK_LOAD|bda|3|3" in h for h in load.history)


def test_add_bda_hook_only_affects_own_actor():
    """add_bda hook must not fire for a different character's load."""
    manager = create_test_battle_manager()
    actor = create_dummy_character(char_id="actor")
    other = create_dummy_character(char_id="other")

    template = _make_template("add_bda", {"amount": 3})
    action = AttackAction(template, actor, [], manager)
    hooks = action.get_hooks()

    load = _make_attack_load(other)  # different actor
    load.bda = 0
    hooks["on_roll_modify"](load)

    assert load.bda == 0  # untouched


def test_add_bda_affects_final_attack_roll():
    """Integration: add_bda hook increases the effective attack during a real combat resolution."""
    manager = create_test_battle_manager()
    # High attributes -> base bda from character stats; we just verify the hook contribution.
    actor = create_dummy_character(char_id="actor", attributes=[10, 10, 10])
    actor.floating_focus = 10

    target = create_dummy_character(char_id="target", attributes=[1, 1, 1])
    target.current_hp = 100

    manager.add_character(actor, MagicMock())
    manager.add_character(target, MagicMock())
    manager.set_tick(actor, 0)
    manager.set_tick(target, 100)
    actor = manager.get_next_actor()

    # Roll of 1 but +10 bda from hook; target has very low stats so should always hit.
    manager.dice_service.schedule_result(1)   # atk
    manager.dice_service.schedule_result(1)   # def

    template = _make_template("add_bda", {"amount": 10})
    action = AttackAction(template, actor, [target], manager)
    load = manager.run_action(action)

    history_str = "|".join(load.history)
    assert "HIT|target" in history_str
    assert "ATK_LOAD|bda|10" in history_str


# ---------------------------------------------------------------------------
# Effect Hook: add_gda  [ARCH.TEST_QUALITY.EFFECT_HOOKS]
# ---------------------------------------------------------------------------

def test_add_gda_hook_modifies_gda():
    """add_gda hook increments attack_load.gda during on_damage_calculation."""
    manager = create_test_battle_manager()
    actor = create_dummy_character(char_id="actor")

    template = _make_template("add_gda", {"amount": 5})
    action = AttackAction(template, actor, [], manager)
    hooks = action.get_hooks()

    assert "on_damage_calculation" in hooks

    load = _make_attack_load(actor)
    load.gda = 0
    hooks["on_damage_calculation"](load)

    assert load.gda == 5
    assert any("ATK_LOAD|gda|5|5" in h for h in load.history)


def test_add_gda_hook_only_affects_own_actor():
    manager = create_test_battle_manager()
    actor = create_dummy_character(char_id="actor")
    other = create_dummy_character(char_id="other")

    template = _make_template("add_gda", {"amount": 5})
    action = AttackAction(template, actor, [], manager)
    hooks = action.get_hooks()

    load = _make_attack_load(other)
    load.gda = 0
    hooks["on_damage_calculation"](load)
    assert load.gda == 0


# ---------------------------------------------------------------------------
# Effect Hook: swap_atk_def_die  [ARCH.TEST_QUALITY.EFFECT_HOOKS]
# ---------------------------------------------------------------------------

def test_swap_atk_def_die_hook():
    """swap_atk_def_die hook sets attack_load.atk_die to actor's def_die."""
    manager = create_test_battle_manager()
    actor = create_dummy_character(char_id="actor")
    original_atk_die = actor.atk_die
    expected_die = actor.def_die  # hook sets atk_die to this

    template = _make_template("swap_atk_def_die", {})
    action = AttackAction(template, actor, [], manager)
    hooks = action.get_hooks()

    assert "on_roll_modify" in hooks

    load = _make_attack_load(actor)
    load.atk_die = original_atk_die
    hooks["on_roll_modify"](load)

    assert load.atk_die == expected_die
    assert any("ATK_LOAD|atk_die" in h for h in load.history)


# ---------------------------------------------------------------------------
# Effect Hook: set_gda_zero_on_dmg  [ARCH.TEST_QUALITY.EFFECT_HOOKS]
# ---------------------------------------------------------------------------

def test_set_gda_zero_on_dmg_hook():
    """set_gda_zero_on_dmg forces gda=0 during on_damage_calculation."""
    manager = create_test_battle_manager()
    actor = create_dummy_character(char_id="actor")

    template = _make_template("set_gda_zero_on_dmg", {})
    action = AttackAction(template, actor, [], manager)
    hooks = action.get_hooks()

    assert "on_damage_calculation" in hooks

    load = _make_attack_load(actor)
    load.gda = 99
    hooks["on_damage_calculation"](load)

    assert load.gda == 0
    assert any("ATK_LOAD|gda|0|0" in h for h in load.history)


# ---------------------------------------------------------------------------
# Effect Hook: apply_status_on_hit_threshold  [ARCH.TEST_QUALITY.EFFECT_HOOKS]
# ---------------------------------------------------------------------------

def test_apply_status_hook_triggers_on_hit_above_threshold():
    """apply_status_on_hit_threshold applies status when hit=True and gda > threshold."""
    manager = create_test_battle_manager()
    actor = create_dummy_character(char_id="actor")
    target = create_dummy_character(char_id="target")

    manager.add_character(actor, MagicMock())
    manager.add_character(target, MagicMock())

    template = _make_template("apply_status_on_hit_threshold", {
        "status": "Atordoado", "threshold": 3, "duration": 2
    })
    action = AttackAction(template, actor, [target], manager)
    hooks = action.get_hooks()

    assert "on_hit_check" in hooks

    load = _make_attack_load(actor, target)
    load.hit = True
    load.gda = 5  # > threshold=3
    hooks["on_hit_check"](load)

    assert any("STATUS|target|Atordoado|2|APPLIED" in h for h in load.history)


def test_apply_status_hook_does_not_trigger_below_threshold():
    manager = create_test_battle_manager()
    actor = create_dummy_character(char_id="actor")
    target = create_dummy_character(char_id="target")

    manager.add_character(actor, MagicMock())
    manager.add_character(target, MagicMock())

    template = _make_template("apply_status_on_hit_threshold", {
        "status": "Atordoado", "threshold": 3, "duration": 2
    })
    action = AttackAction(template, actor, [target], manager)
    hooks = action.get_hooks()

    load = _make_attack_load(actor, target)
    load.hit = True
    load.gda = 2  # <= threshold=3
    hooks["on_hit_check"](load)

    assert not any("STATUS" in h for h in load.history)


# ---------------------------------------------------------------------------
# AttackAction – registry / integration
# ---------------------------------------------------------------------------

def test_attack_action_uses_registry():
    """Verify an arbitrary hook builder registered in EFFECT_HOOK_BUILDERS is invoked."""
    manager = create_test_battle_manager()

    def dummy_builder(effect, action):
        def dummy_hook(load):
            load.dummy_triggered = True
        return {"on_hit_check": dummy_hook}

    EFFECT_HOOK_BUILDERS["dummy_effect"] = dummy_builder

    try:
        actor = create_dummy_character()
        template = _make_template("dummy_effect", {})
        action = AttackAction(template, actor, [], manager)

        hooks = action.get_hooks()
        assert "on_hit_check" in hooks
        load = MagicMock()
        hooks["on_hit_check"](load)
        assert load.dummy_triggered is True
    finally:
        del EFFECT_HOOK_BUILDERS["dummy_effect"]


def test_attack_action_execution_flow():
    """Integration: full attack resolution emits expected structured history events."""
    manager = create_test_battle_manager()
    actor = create_dummy_character(char_id="actor", attributes=[10, 10, 10])
    actor.floating_focus = 10

    target = create_dummy_character(char_id="target", attributes=[10, 10, 10])
    target.current_hp = 100

    manager.add_character(actor, MagicMock())
    manager.add_character(target, MagicMock())
    manager.set_tick(actor, 0)
    manager.set_tick(target, 10)

    manager.dice_service.schedule_result(10)  # atk
    manager.dice_service.schedule_result(5)   # def

    template = _make_template("add_gda", {"amount": 1}, name="Test Skill")
    actor = manager.get_next_actor()
    action = AttackAction(template, actor, [target], manager)

    action_load = manager.run_action(action)

    atk_die = actor.atk_die
    def_die = target.def_die
    history_str = "|".join(action_load.history)
    assert "EXEC|Test Skill|actor" in history_str
    assert f"ROLL|ATK|10|{atk_die}|actor" in history_str
    assert f"ROLL|DEF|5|{def_die}|target" in history_str
    assert "HIT|target" in history_str
    assert "DMG|target" in history_str
    assert "HP|target" in history_str
    assert target.current_hp < 100


def test_attack_action_execute_miss():
    manager = create_test_battle_manager()
    actor = create_dummy_character(attributes=[1, 1, 1])
    actor.floating_focus = 10

    target = create_dummy_character(char_id="target", attributes=[15, 15, 15])

    manager.add_character(actor, MagicMock())
    manager.add_character(target, MagicMock())
    manager.get_next_actor()

    manager.dice_service.schedule_result(1)   # atk
    manager.dice_service.schedule_result(20)  # def

    action = AttackAction(None, actor, [target], manager)
    action_load = manager.run_action(action)

    history_str = "|".join(action_load.history)
    assert "MISS|target" in history_str


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

    manager.dice_service.schedule_result(10)  # area master roll
    manager.dice_service.schedule_result(5)   # target1 def
    manager.dice_service.schedule_result(5)   # target2 def

    template = manager.data_service.get_action_template("AreaAttack")
    action = AttackAction(template, actor, [target1, target2], manager)
    manager.run_action(action)

    assert len(manager.dice_service.queue) == 0


def test_area_attack_postura_defensiva_no_crash():
    from battle.BattlePassives import PosturaDefensiva

    manager = create_test_battle_manager()
    actor = create_dummy_character(char_id="actor")
    owner = create_dummy_character(char_id="owner")

    manager.add_character(actor, MagicMock())
    manager.add_character(owner, MagicMock())
    manager.get_next_actor()

    manager.dice_service.schedule_result(10)  # master roll
    manager.dice_service.schedule_result(5)   # owner def

    passive = PosturaDefensiva(owner, manager)
    passive.is_active = True
    passive._tracked_targets["actor"] = False

    hooks = passive.get_hooks()
    for ev, func in hooks.items():
        manager.subscribe(ev, func)

    template = manager.data_service.get_action_template("AreaAttack")
    action = AttackAction(template, actor, [owner], manager)
    manager.run_action(action)
