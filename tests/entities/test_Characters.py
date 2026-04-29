import pytest
from core.Enums import AttributeType, ArmorType, WeaponType
from entities.Items import Weapon, Armor
from core.Modifiers import EphemeralModifier, PersistentModifier
from core.CharacterSystem import CharacterSystem
from core.Structs import CombatStyle
from tests.utils.entity_factory import create_dummy_character, create_dummy_weapon, create_dummy_armor, get_default_rules

@pytest.fixture
def dummy_char():
    """Returns a controlled Character instance for testing core systems."""
    style = CombatStyle(
        name="Guerreiro",
        atq_die=20,
        def_die=20,
        main_stat=AttributeType.FIS,
        armor_type=ArmorType.HEAVY,
        weapon_type=WeaponType.GREAT_WEAPON
    )
    # Using fixed attributes for predictable tests
    return create_dummy_character(
        name="Arthur",
        attributes=[10, 10, 10], # FIS, HAB, MEN
        combat_style=style
    )

def test_character_starts_alive_with_max_hp(dummy_char):
    assert CharacterSystem.is_alive(dummy_char) is True
    assert dummy_char.current_hp == dummy_char.max_hp
    assert dummy_char.current_hp > 0

def test_character_take_damage_reduces_hp(dummy_char):
    initial_hp = dummy_char.current_hp
    CharacterSystem.take_damage(dummy_char, 30)
    assert dummy_char.current_hp == initial_hp - 30
    assert CharacterSystem.is_alive(dummy_char) is True

def test_character_death(dummy_char):
    CharacterSystem.take_damage(dummy_char, dummy_char.max_hp + 10)
    assert dummy_char.current_hp == 0
    assert CharacterSystem.is_alive(dummy_char) is False

def test_character_equip_weapon(dummy_char):
    w = Weapon(name="Espada", db=6, mda=2, type=WeaponType.GREAT_WEAPON)
    CharacterSystem.equip_weapon(dummy_char, w)
    assert dummy_char.weapon == w
    assert dummy_char.base_pda == 16 # 10 (fis) + 6 (db)
    assert dummy_char.base_mda == 2 # 10 (hab) + 2 (mda)

def test_character_equip_weapon_invalid_type(dummy_char):
    w = Weapon(name="Adaga", db=4, mda=1, type=WeaponType.LIGHT_WEAPON)
    return_value = CharacterSystem.equip_weapon(dummy_char, w)
    assert dummy_char.weapon == None
    assert return_value[0] == False

def test_character_equip_armor(dummy_char):
    initial_hp = dummy_char.max_hp
    a = Armor(name="Placas", hp_bonus=10, type=ArmorType.HEAVY)
    CharacterSystem.equip_armor(dummy_char, a)
    assert dummy_char.armor == a
    assert dummy_char.max_hp == initial_hp + 10
    
    a2 = Armor(name="Placas Mágicas", hp_bonus=20, type=ArmorType.HEAVY)
    CharacterSystem.equip_armor(dummy_char, a2)
    assert dummy_char.max_hp == initial_hp + 20 # replaced 10

def test_character_equip_armor_invalid_type(dummy_char):
    a = Armor(name="Farrapos", hp_bonus=0, type=ArmorType.LIGHT)
    success, msg, old = CharacterSystem.equip_armor(dummy_char, a)
    assert success is False
    assert "não pode equipar" in msg

def test_character_generate_focus(dummy_char):
    max_focus = dummy_char.rules.limite_foco * dummy_char.men
    assert dummy_char.floating_focus == 0
    
    generated = CharacterSystem.generate_focus(dummy_char)
    assert generated > 0
    assert dummy_char.floating_focus == generated
    
    # Fill to max
    for _ in range(20):
        CharacterSystem.generate_focus(dummy_char)
    assert dummy_char.floating_focus == max_focus

def test_character_generate_mana(dummy_char):
    # Prepare current mp
    dummy_char.current_mp = 10
    max_floating = dummy_char.rules.limite_mana * dummy_char.men
    
    CharacterSystem.generate_mana(dummy_char)
    # It drains from current_mp to add to floating_mp
    assert dummy_char.floating_mp > 0
    assert dummy_char.current_mp < 10

def test_character_spend_focus(dummy_char):
    dummy_char.floating_focus = 10
    assert CharacterSystem.spend_focus(dummy_char, 5) is True
    assert dummy_char.floating_focus == 5
    assert CharacterSystem.spend_focus(dummy_char, 10) is False
    assert dummy_char.floating_focus == 5

def test_character_spend_mana(dummy_char):
    dummy_char.floating_mp = 10
    assert CharacterSystem.spend_mana(dummy_char, 5) is True
    assert dummy_char.floating_mp == 5
    assert CharacterSystem.spend_mana(dummy_char, 10) is False
    assert dummy_char.floating_mp == 5

def test_character_stat_properties_with_modifiers(dummy_char):
    assert dummy_char.bda == dummy_char.base_bda
    assert dummy_char.bdd == dummy_char.base_bdd
    assert dummy_char.pre == dummy_char.base_pre
    assert dummy_char.grd == dummy_char.base_grd
    assert dummy_char.pda == dummy_char.base_pda
    assert dummy_char.mda == dummy_char.base_mda
    assert dummy_char.rank == dummy_char.base_rank
    
    mod1 = PersistentModifier("bda", 2, "Test")
    mod2 = EphemeralModifier("bda", 3, "Test2")
    mod3 = EphemeralModifier("rank", 1, "Test3")
    
    dummy_char.add_modifier(mod1)
    dummy_char.add_modifier(mod2)
    dummy_char.add_modifier(mod3)
    
    assert dummy_char.bda == dummy_char.base_bda + 5
    assert dummy_char.rank == dummy_char.base_rank + 1
    
    dummy_char.remove_modifier(mod1)
    assert dummy_char.bda == dummy_char.base_bda + 3

def test_character_status_effects(dummy_char):
    from tests.utils.test_context import BattleTestContext
    from battle.StatusEffects import StatusEffect
    
    context = BattleTestContext()
    effect = StatusEffect("TestEffect", 1, dummy_char, context)
    
    assert effect in dummy_char.status_effects
    effect.remove()
    assert effect not in dummy_char.status_effects

def test_character_clear_ephemeral_modifiers(dummy_char):
    mod1 = PersistentModifier("bdd", 2, "Test")
    mod2 = EphemeralModifier("bdd", 3, "Test2")
    
    dummy_char.add_modifier(mod1)
    dummy_char.add_modifier(mod2)
    
    dummy_char.clear_ephemeral_modifiers()
    
    assert mod1 in dummy_char.modifiers
    assert mod2 not in dummy_char.modifiers