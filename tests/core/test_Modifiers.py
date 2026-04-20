import pytest
from core.Modifiers import StatModifier, EphemeralModifier, PersistentModifier

def test_modifier_unique_id():
    mod1 = StatModifier("bdd", 1, "test")
    mod2 = StatModifier("bdd", 1, "test")
    assert mod1.id != mod2.id

def test_modifier_inheritance():
    e_mod = EphemeralModifier("bda", 2, "test_e")
    p_mod = PersistentModifier("bda", 2, "test_p")
    
    assert isinstance(e_mod, StatModifier)
    assert isinstance(p_mod, StatModifier)
    assert not isinstance(e_mod, PersistentModifier)

def test_modifier_apply_remove():
    mod = StatModifier("bdd", 1, "test")
    mod.apply(None)
    mod.remove(None)
