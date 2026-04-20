from __future__ import annotations
from typing import TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from entities.Characters import Character

class StatModifier:
    """Base class for any statistical modifier."""
    def __init__(self, stat_name: str, value: int, source: str):
        self.id = str(uuid.uuid4())
        self.stat_name = stat_name
        self.value = value
        self.source = source

    def apply(self, character: 'Character') -> None:
        pass # The attribute computation pulls from the modifier stack, no need to apply directly
        
    def remove(self, character: 'Character') -> None:
        pass

class EphemeralModifier(StatModifier):
    """Modifier applied during combat that should be cleared at the end of the combat or effect duration."""
    pass

class PersistentModifier(StatModifier):
    """Modifier applied outside of combat, such as equipment bonuses or permanent curses."""
    pass
