from enum import Enum

# --- ENUMS ---
class RollState(Enum):
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disavantage"
    NEUTRAL = "neutral"

class ArmorType(Enum):
    ROBE = "robe"
    LIGHT = "light"
    HEAVY = "heavy"

class WeaponType(Enum):
    GREAT_WEAPON = "great_weapon"
    MEDIUM_WEAPON = "medium_weapon"
    LIGHT_WEAPON = "light_weapon"
    DOUBLE_WEAPON = "double_weapon"
    WEAPON_AND_SHIELD = "weapon_and_shield"
    RANGED_WEAPON = "ranged_weapon"
    MAGICAL_FOCUS = "magical_focus"

class AttributeType(Enum):
    FIS = "FIS"
    HAB = "HAB"
    MEN = "MEN"

class StatusEffectType(Enum):
    ATORDOADO = "Atordoado"
    ENVENENADO = "Envenenado"
    QUEIMADO = "Queimado"

class AttackType(Enum):
    BASIC_ATTACK = "basic_attack"
    SKILL = "skill"
    EXTRA_ATTACK = "extra_attack"

class BattleActionType(Enum):
    MOVE_ACTION = "move_action"
    STANDARD_ACTION = "standard_action"
    FREE_ACTION = "free_action"

class BattleState(Enum):
    VICTORY = "victory"
    DEFEAT = "defeat"
    DRAW = "draw"
    RUNNING = "runnig"
    ERROR = "error"
