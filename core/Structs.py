from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, TYPE_CHECKING, Any
from core.Enums import RollState, AttributeType, ArmorType, WeaponType, BattleActionType, AttackType
from core.Bases import BattleAction
if TYPE_CHECKING:
    from entities.Characters import Character

# --- MODELOS DE DADOS ---
@dataclass
class GameRules:
    hp_table: Dict[str, int]
    mp_table: Dict[str, int]
    action_cost_table: Dict[str, int]
    limite_foco: int  # Limite máximo de foco = limite_foco * MEN
    limite_mana: int  # Limite máximo de mana = limite_mana * MEN

@dataclass
class RollResult:
    """Objeto para resultados de rolagens, usado principalmente para o Event Bus."""
    final_roll: int
    roll1: int
    roll2: int | None = None  # Em caso de vantagem/desvantagem
    rollstate: RollState = RollState.NEUTRAL
    scheduled: bool = False

@dataclass
class BattleResult:
    history: List[str] = field(default_factory=list)
    winners: List[Character] = field(default_factory=list)
    losers: List[Character] = field(default_factory=list)
    duration: int = 0
    action_per_character: dict[str, int] = field(default_factory=dict)

@dataclass
class CombatStyle:
    name: str
    atq_die: int
    def_die: int
    main_stat: AttributeType
    armor_type: ArmorType
    weapon_type: WeaponType

@dataclass
class AttackEffects:
    id: str
    parameters: Dict[str, Any]

@dataclass
class AttackActionTemplate:
    id: str
    nome: str
    action_type: type['BattleActionType']
    attack_type: type['AttackType']
    focus_cost: int
    effects: List[AttackEffects] = field(default_factory=list)