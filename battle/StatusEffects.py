from __future__ import annotations
from typing import Callable, Dict, TYPE_CHECKING
from core.Events import ActionLoad, HistoryEmitter
from core.BaseClasses import IPassiveContext, BattlePassive, StatusEffect
from core.Modifiers import EphemeralModifier

if TYPE_CHECKING:
    from entities.Characters import Character
    from battle.BattleManager import BattleManager

class Atordoado(StatusEffect):
    def __init__(self, duration: int, target: 'Character', context: 'IPassiveContext'):
        super().__init__(name="Atordoado", duration=duration, target=target, context=context)

    def apply(self):
        mod = EphemeralModifier(stat_name='bdd', value=-1, source=self.name)
        self._add_modifier(mod)
        
        # Delay the character
        if hasattr(self.context, 'delay_character'):
            self.context.delay_character(self.character, self.character.action_cost_base * 0.5)

    def get_hooks(self) -> Dict[str, 'Callable']:
        def check_stun_end(action_load: 'ActionLoad'):
            if action_load.character.char_id == self.character.char_id:
                # Efeito expira e manda a ordem de remoção
                action_load.history.append(HistoryEmitter.status_hook(self.name, self.character.char_id))
                action_load.history.append(HistoryEmitter.status(self.character.char_id, self.name, 0, "REMOVED"))
                self.remove()
        
        return {'on_turn_start': check_stun_end}
