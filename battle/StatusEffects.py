from __future__ import annotations
from typing import Callable, Dict, TYPE_CHECKING
from core.Events import ActionLoad
from core.BaseClasses import IBattleContext, BattlePassive
from core.Modifiers import EphemeralModifier

if TYPE_CHECKING:
    from entities.Characters import Character
    from battle.BattleManager import BattleManager

class StatusEffect(BattlePassive):
    """ 
    Representa um efeito de status aplicado a um personagem, com duração em turnos.
    Pode ser usado para coisas como Atordoado, Envenenado, etc. 
    """
    def __init__(self, name: str, duration: int, target: 'Character', context: 'IBattleContext'):
        super().__init__(name=name, owner=target, context=context)
        self.name = name
        self.duration = duration
        self.character = target
        self.context = context
        self.modifiers: list['EphemeralModifier'] = []
        self.apply(context)

    def get_hooks(self) -> Dict[str, 'Callable']:
        return self.on_get_hooks()
        
    def on_get_hooks(self) -> Dict[str, 'Callable']:
        return {}
    
    def apply(self, context: 'IBattleContext'):
        self.character.add_status_effect(self)
        self.on_apply()
    
    def remove(self):
        for mod in self.modifiers:
            self.character.remove_modifier(mod)
        self.modifiers.clear()
        self.character.remove_status_effect(self)
        self.on_remove()
        
    def on_apply(self):
        pass
        
    def on_remove(self):
        pass

class Atordoado(StatusEffect):
    def __init__(self, duration: int, target: 'Character', context: 'IBattleContext'):
        super().__init__(name="Atordoado", duration=duration, target=target, context=context)

    def on_apply(self):
        mod = EphemeralModifier(stat_name='bdd', value=-1, source=self.name)
        self.modifiers.append(mod)
        self.character.add_modifier(mod)
        
        # Delay the character
        if hasattr(self.context, 'delay_character'):
            self.context.delay_character(self.character, self.character.action_cost_base * 0.5)

    def on_get_hooks(self) -> Dict[str, 'Callable']:
        def check_stun_end(action_load: 'ActionLoad'):
            if action_load.character.char_id == self.character.char_id:
                # CQRS: Efeito expira e manda a ordem de remoção
                self.remove()
        
        return {'on_turn_start': check_stun_end}

