from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from core.Enums import WeaponType, ArmorType

@dataclass
class Weapon:
    name: str
    db: int
    mda: int
    type: WeaponType
    properties: List[str] = field(default_factory=list)

@dataclass
class Armor:
    name: str
    type: ArmorType
    hp_bonus: int
    properties: List[str] = field(default_factory=list)
