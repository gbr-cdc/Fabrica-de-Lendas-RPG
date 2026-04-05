from core.Models import StatusEffect, Character
from core.BattleManager import BattleManager


class Atordoado(StatusEffect):
    def __init__(self, duration: int, target: 'Character'):
        super().__init__(name="Atordoado", duration=duration, target=target)

    def on_apply(self):
        self.character.bdd -= 1
        if self.battle_manager is not None:
            battle_manager = self.battle_manager
            battle_manager.delay_character(self.character, self.character.action_cost_base * 0.5)

    def on_remove(self):
        self.character.bdd += 1
    
    def on_subscribe(self, battle_manager: BattleManager):
        battle_manager.subscribe('on_turn_start', self.effect_end)
    
    def effect_end(self, event_data: dict) -> dict:
        if event_data.get('character') and event_data['character'].char_id == self.character.char_id:
            self.remove()
        return event_data
    
    def on_unsubscribe(self, battle_manager: 'BattleManager'):
        battle_manager.unsubscribe('on_turn_start', self.effect_end)
