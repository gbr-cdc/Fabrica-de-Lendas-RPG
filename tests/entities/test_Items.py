import pytest
from entities.Items import Weapon, Armor
from core.Enums import WeaponType, ArmorType

def test_weapon_initialization():
    w = Weapon(name="Espada Longa", db=6, mda=2, type=WeaponType.MEDIUM_WEAPON)
    assert w.name == "Espada Longa"
    assert w.db == 6
    assert w.mda == 2
    assert w.type == WeaponType.MEDIUM_WEAPON

def test_armor_initialization():
    a = Armor(name="Armadura de Placas", hp_bonus=10, type=ArmorType.HEAVY)
    assert a.name == "Armadura de Placas"
    assert a.hp_bonus == 10
    assert a.type == ArmorType.HEAVY
