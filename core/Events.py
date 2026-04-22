from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING
from core.Enums import AttackType, RollState

if TYPE_CHECKING:
    from core.BaseClasses import IBattleContext
    from entities.Characters import Character

@dataclass(kw_only=True)
class ActionLoad:
    """Objeto base para trafegar dados no Event Bus e retornar resultados para a View."""
    character: 'Character'
    history: List[str] = field(default_factory=list)
    success: bool = True  # Por padrão, assumimos que a ação vai dar certo

@dataclass(kw_only=True)
class AttackLoad(ActionLoad):
    target: Character | None = None
    battle_context: 'IBattleContext'
    attack_type: AttackType
    attack_state: RollState
    defense_state: RollState
    gda: int = 0
    damage: int = 0
    hit: bool = False