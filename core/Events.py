from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING, Any
from core.Enums import AttackType, RollState

if TYPE_CHECKING:
    from core.BaseClasses import IBattleContext
    from entities.Characters import Character

@dataclass(kw_only=True)
class ActionLoad:
    """Objeto base para trafegar dados no Event Bus e retornar resultados para a View."""
    character: Character
    history: List[str] = field(default_factory=list)
    success: bool = True

    def add_event(self, tag: str, *params: Any):
        """Standardizes event insertion into history."""
        event_str = "|".join([tag] + [str(p) for p in params])
        self.history.append(event_str)

@dataclass(kw_only=True)
class AttackLoad(ActionLoad):
    target: Character | None = None
    attack_type: AttackType
    attack_state: RollState
    defense_state: RollState
    gda: int = 0
    damage: int = 0
    hit: bool = False
    attack_roll: int = 0
    defense_roll: int = 0
    pre: int = 0
    bda: int = 0
    bdd: int = 0
    grd: int = 0
    atk_die: int = 0
    def_die: int = 0

class HistoryEmitter:
    """Utility to generate structured event tags."""
    @staticmethod
    def exec(action_id: str, actor_id: str) -> str:
        return f"EXEC|{action_id}|{actor_id}"

    @staticmethod
    def roll(type: str, value: int, die_size: int, actor_id: str) -> str:
        return f"ROLL|{type}|{value}|{die_size}|{actor_id}"

    @staticmethod
    def mod(source_id: str, value: int, target_id: str) -> str:
        return f"MOD|{source_id}|{value}|{target_id}"

    @staticmethod
    def hit(target_id: str) -> str:
        return f"HIT|{target_id}"

    @staticmethod
    def miss(target_id: str) -> str:
        return f"MISS|{target_id}"

    @staticmethod
    def dmg(target_id: str, amount: int, type: str) -> str:
        return f"DMG|{target_id}|{amount}|{type}"

    @staticmethod
    def hp(entity_id: str, delta: int, current: int) -> str:
        return f"HP|{entity_id}|{delta}|{current}"

    @staticmethod
    def focus(entity_id: str, delta: int, current: int) -> str:
        return f"FOCUS|{entity_id}|{delta}|{current}"

    @staticmethod
    def mana_f(entity_id: str, delta: int, current: int) -> str:
        return f"MANA_F|{entity_id}|{delta}|{current}"

    @staticmethod
    def mana_t(entity_id: str, delta: int, current: int) -> str:
        return f"MANA_T|{entity_id}|{delta}|{current}"

    @staticmethod
    def msg(message: str) -> str:
        return f"MSG|{message}"

    @staticmethod
    def death(entity_id: str) -> str:
        return f"DEATH|{entity_id}"

    @staticmethod
    def status(entity_id: str, name: str, duration: int, state: str) -> str:
        return f"STATUS|{entity_id}|{name}|{duration}|{state}"

    @staticmethod
    def turn_start(actor_id: str, hp: int, max_hp: int, mp: int, max_mp: int, focus: int, mana: int) -> str:
        return f"TURN_START|{actor_id}|{hp}|{max_hp}|{mp}|{max_mp}|{focus}|{mana}"

    @staticmethod
    def passive(passive_name: str, owner_id: str) -> str:
        return f"PASSIVE|{passive_name}|{owner_id}"

    @staticmethod
    def action_hook(action_name: str, actor_id: str) -> str:
        return f"ACTION_HOOK|{action_name}|{actor_id}"

    @staticmethod
    def status_hook(status_name: str, target_id: str) -> str:
        return f"STATUS_HOOK|{status_name}|{target_id}"

    @staticmethod
    def atk_load(attribute: str, delta: int, current: int) -> str:
        return f"ATK_LOAD|{attribute}|{delta}|{current}"

    @staticmethod
    def atk_calc(actor_id: str, roll: int, rank: int, bda: int, final: int) -> str:
        return f"ATK_CALC|{actor_id}|{roll}|{rank}|{bda}|{final}"

    @staticmethod
    def dmg_calc(target_id: str, pda: int, gda: int, mda: int, modifier: int, final: int) -> str:
        return f"DMG_CALC|{target_id}|{pda}|{gda}|{mda}|{modifier}|{final}"

    @staticmethod
    def def_calc(target_id: str, roll: int, rank: int, bdd: int, final: int) -> str:
        return f"DEF_CALC|{target_id}|{roll}|{rank}|{bdd}|{final}"