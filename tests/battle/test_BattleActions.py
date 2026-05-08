import pytest
from battle.BattleActions import AttackAction, GenerateManaAction, GenerateFocusAction, EFFECT_HOOK_BUILDERS
from core.Events import ActionLoad, AttackLoad
from core.Structs import AttackActionTemplate, AttackEffects, RollResult
from core.Enums import BattleActionType, RollState, AttackType
from tests.utils.entity_factory import create_dummy_character
from tests.utils.test_context import BattleTestContext
from core.DataManager import DataManager
from unittest.mock import MagicMock

@pytest.fixture
def data_manager():
    dm = DataManager()
    dm.load_action_templates('data/AttackActions.json')
    return dm

def test_generate_mana_action():
    actor = create_dummy_character()
    actor.current_mp = 5
    actor.rules.limite_mana = 2
    actor.men = 10 # MEN 10
    actor.floating_mp = 0
    
    context = BattleTestContext()
    action = GenerateManaAction(actor, targets=[actor], context=context)
    
    can_exec, msg = action.can_execute()
    assert can_exec is True
    
    load = action.execute()
    # Check for MANA_T (reduction) and MANA_F (generation)
    assert any("MANA_T|" in h for h in load.history)
    assert any("MANA_F|" in h for h in load.history)
    assert actor.current_mp == 0 
    assert actor.floating_mp == 5 

def test_generate_focus_action():
    actor = create_dummy_character()
    actor.rules.limite_foco = 3
    actor.men = 10 # MEN 10
    actor.floating_focus = 0
    
    context = BattleTestContext()
    action = GenerateFocusAction(actor, targets=[actor], context=context)
    
    can_exec, msg = action.can_execute()
    assert can_exec is True
    
    load = action.execute()
    assert any("FOCUS|" in h for h in load.history)
    assert actor.floating_focus == 10

def test_attack_action_execution_flow(data_manager):
    actor = create_dummy_character(char_id="actor", attributes=[10, 10, 10])
    actor.floating_focus = 10
    actor.hab = 10
    
    target = create_dummy_character(char_id="target", attributes=[10, 10, 10])
    target.current_hp = 100
    
    context = BattleTestContext()
    context.dice_service.schedule_result(10)
    context.dice_service.schedule_result(5)
    
    template = data_manager.get_action_template("SkillN1")
    
    action = AttackAction(template, actor, [target], context)
    
    hooks = action.get_hooks()
    assert "on_damage_calculation" in hooks
    
    can_exec, msg = action.can_execute()
    assert can_exec is True
    
    context.subscribe("on_damage_calculation", hooks["on_damage_calculation"])
    
    action_load = action.execute()

    history_str = "|".join(action_load.history)
    assert "EXEC|SkillN1|actor" in history_str
    assert "ROLL|ATK|10|6|actor" in history_str
    assert "ROLL|DEF|5|6|target" in history_str 
    assert "HIT|target" in history_str
    assert "DMG|target" in history_str
    assert "HP|target" in history_str

    assert target.current_hp < 100

def test_attack_action_can_execute_failures(data_manager):
    actor = create_dummy_character()
    actor.floating_focus = 0
    target = create_dummy_character()
    
    template = data_manager.get_action_template("SkillN1")
    action = AttackAction(template, actor, [target], BattleTestContext())
    
    can, msg = action.can_execute()
    assert can is False
    assert "insuficiente" in msg

    actor.floating_focus = 10
    target.current_hp = 0
    can, msg = action.can_execute()
    assert can is False
    assert "derrotado" in msg

def test_attack_action_gda_hook(data_manager):
    actor = create_dummy_character()
    template = data_manager.get_action_template("SkillN1")
    action = AttackAction(template, actor, [], BattleTestContext())
    hooks = action.get_hooks()
    
    load = ActionLoad(character=actor)
    load.gda = 0
    load.history = []
    
    hooks["on_damage_calculation"](load)
    assert load.gda == 5
    assert "MOD|Habilidade Nível 1|5|" in load.history[0]

def test_attack_action_execute_miss(data_manager):
    actor = create_dummy_character(attributes=[1, 1, 1])
    actor.floating_focus = 10
    
    target = create_dummy_character(char_id="target", attributes=[15, 15, 15])
    
    context = BattleTestContext()
    context.dice_service.schedule_result(1) # atk
    context.dice_service.schedule_result(20) # def
    
    template = data_manager.get_action_template("BasicAttack")
    action = AttackAction(template, actor, [target], context)
    
    action_load = action.execute()
    
    history_str = "|".join(action_load.history)
    assert "MISS|target" in history_str

def test_generate_mana_action_failures():
    actor = create_dummy_character()
    actor.current_mp = 0
    action = GenerateManaAction(actor, targets=[actor], context=BattleTestContext())
    
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
    actor = create_dummy_character()
    actor.rules.limite_foco = 1
    actor.men = 5
    actor.floating_focus = 5
    action = GenerateFocusAction(actor, targets=[actor], context=BattleTestContext())
    
    can, msg = action.can_execute()
    assert can is False
    assert "limite" in msg

def test_attack_action_uses_registry(data_manager):
    def dummy_builder(effect, action):
        def dummy_hook(load):
            load.dummy_triggered = True
        return {"on_hit_check": dummy_hook}
    
    EFFECT_HOOK_BUILDERS["dummy_effect"] = dummy_builder
    
    try:
        actor = create_dummy_character()
        template = AttackActionTemplate(
            id="T", nome="T", action_type=BattleActionType.STANDARD_ACTION, 
            attack_type=AttackType.BASIC_ATTACK, focus_cost=0, 
            effects=[AttackEffects("dummy_effect", {})]
        )
        action = AttackAction(template, actor, [], BattleTestContext())
        
        hooks = action.get_hooks()
        assert "on_hit_check" in hooks
        load = MagicMock()
        hooks["on_hit_check"](load)
        assert load.dummy_triggered is True
    finally:
        del EFFECT_HOOK_BUILDERS["dummy_effect"]

def test_attack_action_multi_target(data_manager):
    actor = create_dummy_character(char_id="Attacker")
    actor.floating_focus = 10
    t1 = create_dummy_character(char_id="T1")
    t2 = create_dummy_character(char_id="T2")
    
    context = BattleTestContext()
    context.dice_service.schedule_result(10)
    context.dice_service.schedule_result(5)
    context.dice_service.schedule_result(10)
    context.dice_service.schedule_result(5)
    
    template = data_manager.get_action_template("BasicAttack")
    action = AttackAction(template, actor, [t1, t2], context)
    
    result = action.execute()
    
    history_str = "\n".join(result.history)
    assert "HIT|T1" in history_str
    assert "HIT|T2" in history_str

def test_attack_action_one_dead(data_manager):
    actor = create_dummy_character(char_id="Attacker")
    actor.floating_focus = 10
    
    t_dead = create_dummy_character(char_id="dead")
    t_dead.current_hp = 0
    t_alive = create_dummy_character(char_id="alive")
    
    context = BattleTestContext()
    context.dice_service.schedule_result(10)
    context.dice_service.schedule_result(5)
    
    template = data_manager.get_action_template("BasicAttack")
    action = AttackAction(template, actor, [t_dead, t_alive], context)
    
    result = action.execute()
    
    history_str = "\n".join(result.history)
    assert "HIT|alive" in history_str
    assert "dead" not in history_str

def test_area_attack_one_roll_multiple_targets(data_manager):
    actor = create_dummy_character(char_id="actor")
    actor.floating_focus = 10
    target1 = create_dummy_character(char_id="target1")
    target2 = create_dummy_character(char_id="target2")
    
    context = BattleTestContext()
    context.dice_service.schedule_result(10) # actor roll
    context.dice_service.schedule_result(5)  # target1 roll
    context.dice_service.schedule_result(5)  # target2 roll
    
    template = data_manager.get_action_template("AreaAttack")
    action = AttackAction(template, actor, [target1, target2], context)
    
    action.execute()
    
    # In AREA attack, dice_service should be called only once for the attacker
    assert len(context.dice_service.queue) == 0

def test_area_attack_postura_defensiva_no_crash(data_manager):
    from battle.BattlePassives import PosturaDefensiva
    
    actor = create_dummy_character(char_id="actor")
    owner = create_dummy_character(char_id="owner")
    
    context = BattleTestContext([actor, owner])
    context.dice_service.schedule_result(10) # master roll
    context.dice_service.schedule_result(5)  # owner def
    
    passive = PosturaDefensiva(owner, context)
    passive.is_active = True
    passive._tracked_targets["actor"] = False # Owner is watching actor
    
    # Register passive hooks in context
    hooks = passive.get_hooks()
    for ev, func in hooks.items():
        context.subscribe(ev, func)
    
    template = data_manager.get_action_template("AreaAttack")
    action = AttackAction(template, actor, [owner], context)
    # This should NOT crash when master roll emits 'on_roll_modify' with target=None
    action.execute()
