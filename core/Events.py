from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from core.Enums import BattleInteractionType, RollState
from combat.BattleManager import BattleManager
from entities.Characters import Character

@dataclass(kw_only=True)
class ActionLoad:
    """Objeto base para trafegar dados no Event Bus e retornar resultados para a View."""
    character: 'Character'
    history: List[str] = field(default_factory=list)
    success: bool = True  # Por padrão, assumimos que a ação vai dar certo

@dataclass(kw_only=True)
class AttackLoad(ActionLoad):
    target: 'Character'
    battle_manager: 'BattleManager'
    interaction_type: BattleInteractionType
    attack_state: RollState
    defense_state: RollState
    gda: int = 0
    damage: int = 0
    hit: bool = False