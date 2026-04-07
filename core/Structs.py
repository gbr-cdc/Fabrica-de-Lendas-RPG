from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
from combat.BattleManager import BattleManager
from core.Enums import RollState, AttributeType, ArmorType, WeaponType
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
    history: List[str] = []
    winners: List[Character] = []
    losers: List[Character] = []
    duration: int = 0
    action_per_character: dict[str, int] = {}

@dataclass
class CombatStyle:
    name: str
    atq_die: int
    def_die: int
    main_stat: AttributeType
    armor_type: ArmorType
    weapon_type: WeaponType
 

