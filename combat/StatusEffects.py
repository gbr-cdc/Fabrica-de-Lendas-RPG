from core.Events import ActionLoad
from entities.Characters import Character
from combat.BattleManager import BattleManager

class StatusEffect:
    """ 
    Representa um efeito de status aplicado a um personagem, com duração em turnos. Pode ser usado para coisas como Atordoado, Envenenado, etc. 
    """
    def __init__(self, name: str, duration: int, target: 'Character', battle_manager: 'BattleManager | None' = None):
        self.name = name
        self.duration = duration
        self.character = target
        self.battle_manager = battle_manager
        self.apply(battle_manager)
        
    # --- MÉTODOS DO MOTOR --- (Não devem ser sobrescritos)

    def apply(self, battle_manager: 'BattleManager | None' = None):
        """ 
        Aplica o efeito ao personagem. Se BattleManager for fornecido, registra o efeito para receber ticks de duração. 
        """
        self.battle_manager = battle_manager
        self.character.status_effects.append(self)
        self.on_apply()
        
        if self.battle_manager is not None:
            self.battle_manager.subscribe('on_turn_end', self._tick_duration) 
            self.on_subscribe(self.battle_manager)

    def remove(self):
        """ 
        Remove o efeito do personagem e cancela a inscrição no BattleManager. 
        """
        self.on_remove()

        if self.battle_manager is not None:
            self.battle_manager.unsubscribe('on_turn_end', self._tick_duration)
            self.on_unsubscribe(self.battle_manager)

    def _tick_duration(self, action_load: 'ActionLoad') -> ActionLoad:
        """
        Recebe o sinal do BattleManager no fim do turno para acionar o on_tick
        """
        if action_load.character.char_id == self.character.char_id:
            # A responsabilidade de reduzir a duração do efeito fica a cargo do on_tick
            action_load = self.on_tick(action_load)

            # Se a duração for menor ou igual a 0, remove o efeito
            if self.duration <= 0:
                self.remove()
                if self in self.character.status_effects:
                    self.character.status_effects.remove(self)
            
        return action_load

    # --- MÉTODOS DE GAME DESIGN --- (Devem ser sobrescritos por cada efeito específico)
    
    # Quando é adicionado
    def on_apply(self):
        pass
    
    # Ao se inscrever no BattleManager
    def on_subscribe(self, battle_manager: 'BattleManager'):
        pass
    
    # Quando é removido
    def on_remove(self):
        pass

    # Ao se desinscrever do BattleManager
    def on_unsubscribe(self, battle_manager: 'BattleManager'):
        pass

    # A cada tick
    def on_tick(self, action_load: 'ActionLoad') -> ActionLoad:
        return action_load

class Atordoado(StatusEffect):
    def __init__(self, duration: int, target: 'Character', battle_manager: 'BattleManager'):
        super().__init__(name="Atordoado", duration=duration, target=target, battle_manager=battle_manager)

    def on_apply(self):
        self.character.bdd -= 1
        if self.battle_manager is not None:
            battle_manager = self.battle_manager
            battle_manager.delay_character(self.character, self.character.action_cost_base * 0.5)

    def on_remove(self):
        self.character.bdd += 1
    
    def on_subscribe(self, battle_manager: BattleManager):
        battle_manager.subscribe('on_turn_start', self.effect_end)
    
    def effect_end(self, action_load: 'ActionLoad'):
        if action_load.character.char_id == self.character.char_id:
            self.remove()
    
    def on_unsubscribe(self, battle_manager: 'BattleManager'):
        battle_manager.unsubscribe('on_turn_start', self.effect_end)
