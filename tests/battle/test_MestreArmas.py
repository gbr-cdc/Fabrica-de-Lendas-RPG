import pytest
from tests.utils.entity_factory import create_dummy_character
from tests.utils.test_utils import create_test_battle_manager
from battle.BattleActions import AttackAction, MudarPosturaBatalha
from core.Structs import CombatStyle
from core.Enums import AttributeType, ArmorType, WeaponType

@pytest.fixture
def mestre_armas():
    style = CombatStyle(name="Mestre_das_Armas", atq_die=10, def_die=10, main_stat=AttributeType.FIS, armor_type=ArmorType.HEAVY, weapon_type=WeaponType.MEDIUM_WEAPON)
    char = create_dummy_character(char_id="mestre1", name="Mestre", attributes=[5,5,5], combat_style=style, equipped=True)
    char.passive_abilities.append("Postura de Batalha")
    return char

@pytest.fixture
def target():
    style = CombatStyle(name="Dummy", atq_die=8, def_die=8, main_stat=AttributeType.FIS, armor_type=ArmorType.LIGHT, weapon_type=WeaponType.MEDIUM_WEAPON)
    char = create_dummy_character(char_id="target1", name="Target", attributes=[3,3,3], combat_style=style, equipped=True)
    return char

def test_mudar_postura_batalha_cycle(mestre_armas, target):
    bm = create_test_battle_manager()
    from controllers.CharacterController import CharacterController
    class DummyController(CharacterController):
        def choose_action(self, actor, context, action_load=None): pass
        def choose_reaction(self, actor, reaction_id, action_load, context): return True

    bm.add_character(mestre_armas, DummyController(), start_tick=100)

    # Initial state should be None
    mestre_armas = bm.get_next_actor()
    passive = bm.get_active_passive(mestre_armas.char_id, "Postura de Batalha")
    assert passive.current_postura is None

    # Cycle to OFFENSIVE
    action = MudarPosturaBatalha(actor=mestre_armas, targets=[], context=bm)
    load = bm.run_action(action)
    assert passive.current_postura == "OFFENSIVE"
    assert "POSTURA|mestre1|OFFENSIVE" in load.history
    
    # Cycle to DEFENSIVE
    action = MudarPosturaBatalha(actor=mestre_armas, targets=[], context=bm)
    load = bm.run_action(action)
    assert passive.current_postura == "DEFENSIVE"
    assert "POSTURA|mestre1|DEFENSIVE" in load.history

    # Cycle to None
    action = MudarPosturaBatalha(actor=mestre_armas, targets=[], context=bm)
    load = bm.run_action(action)
    assert passive.current_postura is None
    assert "POSTURA|mestre1|NONE" in load.history

def test_postura_batalha_offensive_bonus(mestre_armas, target):
    bm = create_test_battle_manager()
    from controllers.CharacterController import CharacterController
    class DummyController(CharacterController):
        def choose_action(self, actor, context, action_load=None): pass
        def choose_reaction(self, actor, reaction_id, action_load, context): return True
    
    bm.add_character(mestre_armas, DummyController(), start_tick=100)
    bm.add_character(target, DummyController(), start_tick=200)
    mestre_armas = bm.get_next_actor()
    
    # Activate Offensive Posture
    action = MudarPosturaBatalha(actor=mestre_armas, targets=[], context=bm)
    bm.run_action(action)
    
    # Simulate attack roll > 7 (schedule 8)
    bm.dice_service.schedule_result(8) # Atk roll
    bm.dice_service.schedule_result(2) # Def roll
    
    atk_action = AttackAction(None, mestre_armas, [target], bm)
    load = bm.run_action(atk_action)
    
    assert "MOD|Postura de Batalha_OFF|4|mestre1" in load.history

    # Now test with roll <= 7
    bm.dice_service.schedule_result(5) # Atk roll
    bm.dice_service.schedule_result(2) # Def roll
    
    atk_action = AttackAction(None, mestre_armas, [target], bm)
    load = bm.run_action(atk_action)
    
    assert "MOD|Postura de Batalha_OFF|2|mestre1" in load.history

def test_postura_batalha_defensive_reroll(mestre_armas, target):
    bm = create_test_battle_manager()
    from controllers.CharacterController import CharacterController
    class DummyController(CharacterController):
        def choose_action(self, actor, context, action_load=None): pass
        def choose_reaction(self, actor, reaction_id, action_load, context):
            if "REROLL" in reaction_id:
                return True
            return False
            
    bm.add_character(mestre_armas, DummyController(), start_tick=100)
    bm.add_character(target, DummyController(), start_tick=200)
    mestre_armas = bm.get_next_actor()
    
    # Give mestre focus to pay for reroll
    mestre_armas.floating_focus = 5

    # Activate Offensive then Defensive
    action = MudarPosturaBatalha(actor=mestre_armas, targets=[], context=bm)
    bm.run_action(action)
    action = MudarPosturaBatalha(actor=mestre_armas, targets=[], context=bm)
    bm.run_action(action)

    # Re-insert target so target can attack
    target = bm.get_next_actor()

    # Target attacks mestre_armas
    bm.dice_service.schedule_result(10) # Target atk roll
    bm.dice_service.schedule_result(1)  # Mestre first def roll (will trigger reroll)
    bm.dice_service.schedule_result(8)  # Mestre new def roll
    
    atk_action = AttackAction(None, target, [mestre_armas], bm)
    load = bm.run_action(atk_action)
    
    assert "FOCUS|mestre1|-2|3" in load.history
    assert "ROLL|DEF_REROLL|8|10|mestre1" in load.history
    
    # Diff should be new - old = 8 - 1 = 7
    # Mod should be -diff = -7
    assert "MOD|Postura de Batalha_DEF|-7|mestre1" in load.history
