import random
from typing import List, Optional
from core.Enums import AttributeType, WeaponType, ArmorType
from core.Structs import GameRules, CombatStyle
from entities.Characters import Character
from entities.Items import Weapon, Armor

# GDD values based on [GDD.CORE.PROG]
HP_TABLE = {str(i): v for i, v in enumerate([10, 20, 30, 40, 50, 65, 80, 95, 115, 135, 155, 180, 205, 230, 270, 310])}
ACTION_COST_TABLE = {str(i): v for i, v in enumerate([60, 50, 40, 36, 32, 28, 25, 22, 20, 18, 16, 14, 13, 12, 11, 10])}
MP_TABLE = {str(i): v for i, v in enumerate([0, 10, 40, 60, 70, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 300])}

# GDD values based on [GDD.EQUIP.TIERS]
WEAPON_DB_TABLE = {1: 3, 2: 5, 3: 7, 4: 10, 5: 15}
WEAPON_MDA_TABLE = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3}

ARMOR_HP_TABLE = {
    ArmorType.ROBE: {1: 10, 2: 15, 3: 25, 4: 35, 5: 55},
    ArmorType.LIGHT: {1: 15, 2: 25, 3: 45, 4: 70, 5: 110},
    ArmorType.HEAVY: {1: 25, 2: 40, 3: 70, 4: 110, 5: 160}
}

def get_default_rules() -> GameRules:
    """Returns a GameRules object populated with GDD progression values."""
    return GameRules(
        hp_table=HP_TABLE,
        mp_table=MP_TABLE,
        action_cost_table=ACTION_COST_TABLE,
        limite_foco=5,
        limite_mana=5
    )

def create_dummy_weapon(tier: int = 1, weapon_type: WeaponType = WeaponType.MEDIUM_WEAPON, name: str = "Dummy Weapon") -> Weapon:
    """Creates a Weapon instance with stats scaled by Tier according to [GDD.EQUIP.TIERS.WEAPONS]."""
    return Weapon(
        name=name,
        db=WEAPON_DB_TABLE.get(tier, 3),
        mda=WEAPON_MDA_TABLE.get(tier, 1),
        type=weapon_type
    )

def create_dummy_armor(tier: int = 1, armor_type: ArmorType = ArmorType.LIGHT, name: str = "Dummy Armor") -> Armor:
    """Creates an Armor instance with HP bonus scaled by Tier and Type according to [GDD.EQUIP.TIERS.ARMOR]."""
    hp_bonus = ARMOR_HP_TABLE.get(armor_type, ARMOR_HP_TABLE[ArmorType.LIGHT]).get(tier, 10)
    return Armor(
        name=name,
        type=armor_type,
        hp_bonus=hp_bonus
    )

def create_dummy_character(
    char_id: str = "dummy_01",
    name: str = "Dummy Hero",
    attributes: Optional[List[int]] = None,
    combat_style: Optional[CombatStyle] = None,
    rules: Optional[GameRules] = None,
    team: int = 0
) -> Character:
    """
    Creates a Character instance for testing. 
    If attributes are not provided, they are randomized between 0-15 [GDD.CORE.ATTR].
    If rules are not provided, GDD defaults are used.
    """
    if attributes is None:
        attributes = [random.randint(0, 15) for _ in range(3)]
    
    if rules is None:
        rules = get_default_rules()
        
    if combat_style is None:
        # Default balanced style
        combat_style = CombatStyle(
            name="Balanced",
            atq_die=6,
            def_die=6,
            main_stat=AttributeType.FIS,
            armor_type=ArmorType.LIGHT,
            weapon_type=WeaponType.MEDIUM_WEAPON
        )
        
    char = Character(char_id, name, attributes, combat_style, rules, team)
    return char
