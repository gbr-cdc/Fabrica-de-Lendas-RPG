import pytest
from core.DataManager import DataManager
from core.Modifiers import StatModifier, EphemeralModifier, PersistentModifier

@pytest.fixture
def character():
    """Returns a real Character instance loaded from data files."""
    dm = DataManager()
    dm.load_game_rules("data/Rules.json")
    dm.load_combat_styles("data/CombatStyles.json")
    dm.load_characters("data/Characters.json")
    return dm.get_character("Cavaleiro")

def test_modifier_unique_id():
    """Technical: IDs must be unique even for identical data."""
    mod1 = StatModifier("bdd", 1, "test")
    mod2 = StatModifier("bdd", 1, "test")
    assert mod1.id != mod2.id

def test_modifier_inheritance():
    """Technical: Proper class hierarchy."""
    e_mod = EphemeralModifier("bda", 2, "test_e")
    p_mod = PersistentModifier("bda", 2, "test_p")
    
    assert isinstance(e_mod, StatModifier)
    assert isinstance(p_mod, StatModifier)
    assert not isinstance(e_mod, PersistentModifier)

def test_modifier_application_behavior(character):
    """Behavioral: Applying a modifier must update the calculated stat total."""
    base_bdd = character.bdd
    mod = StatModifier("bdd", 5, "test_source")
    character.add_modifier(mod)
    
    assert character.bdd == base_bdd + 5
    assert any(m.id == mod.id for m in character.modifiers)

def test_multiple_modifiers_stacking(character):
    """Behavioral: Multiple modifiers to the same stat must stack additively."""
    base_bda = character.bda
    mod1 = StatModifier("bda", 2, "source1")
    mod2 = StatModifier("bda", 3, "source2")
    
    character.add_modifier(mod1)
    character.add_modifier(mod2)
    
    assert character.bda == base_bda + 5

def test_modifier_removal_behavior(character):
    """Behavioral: Removing a modifier must revert the stat total."""
    mod = StatModifier("pre", 10, "test")
    character.add_modifier(mod)
    initial_total = character.pre
    
    character.remove_modifier(mod)
    assert character.pre == initial_total - 10
    assert mod not in character.modifiers

def test_ephemeral_modifier_cleanup(character):
    """Behavioral: Ephemeral modifiers are cleared while persistent ones remain."""
    e_mod = EphemeralModifier("bdd", 5, "combat")
    p_mod = PersistentModifier("bdd", 2, "gear")
    
    character.add_modifier(e_mod)
    character.add_modifier(p_mod)
    
    character.clear_ephemeral_modifiers()
    
    assert e_mod not in character.modifiers
    assert p_mod in character.modifiers
