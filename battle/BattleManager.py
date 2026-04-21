from __future__ import annotations
import heapq
from typing import List, Callable, Dict, TYPE_CHECKING
from collections import defaultdict
from core.Enums import BattleState, BattleActionType
from core.Structs import BattleResult, AttackActionTemplate
from core.Events import ActionLoad
from battle.BattlePassives import registry
from core.CharacterSystem import CharacterSystem

if TYPE_CHECKING:
    from core.DataManager import DataManager
    from battle.Judges import BattleJudge
    from core.DiceManager import DiceManager
    from entities.Characters import Character
    from controllers.CharacterController import CharacterController

class BattleManager:
    """
    O Gerenciador Central. Controla o Relógio de Ticks e o Event Bus (Observer Pattern).
    """
    def __init__(self, dice_service: 'DiceManager', data_service: 'DataManager', judge: 'BattleJudge'):
        # Min-Heap para o Relógio de Ticks: (tick_number, char_id, character_object)
        self.timeline = []
        self.current_tick = 0

        # Injeção do serviço de dados
        self.dice_service = dice_service
        self.data_service = data_service
        self.judge = judge
        #Lista de personagens na batalha, acessível por char_id
        self.characters: Dict[str, Character] = {}
        self.controllers: Dict[str, CharacterController] = {}
        self.graveyard: Dict[str, Character] = {}
        self.active_passives = defaultdict(list)

        self.timeline_slots = set() # (tick, hab, roll) registry to ensure uniqueness

        self.battle_result = BattleResult()
        self.battle_state = BattleState.RUNNING
        
        # Event Bus (Observer Pattern) para comandos de habilidades
        self.listeners: Dict[str, List[Callable]] = {
            'on_turn_start': [], # Início do turno
            'on_roll_modify': [], # Para modificar rolagens com vantagem e desvantagem
            'on_defense_reaction': [], # Para reações defensivas (podem transformar um acerto em erro)
            'on_hit_check': [], # Após verificação de acerto para disparar o gatilho de certas passivas
            'on_gda_modify': [], # Modificação do GdA antes de calcular o dano final
            'on_damage_calculation': [], # Adição do dano de skills e magias
            'on_damage_taken': [], # Após o alvo efetivamente tomar dano
            'on_attack_end': [], # Fim do ataque
            'on_turn_end': [], # Fim do turno
            'on_character_death': [] # Quando um personagem morre
        }
    
    def get_template(self, template_id: str) -> AttackActionTemplate:
        return self.data_service.get_action_template(template_id)

    def _get_unique_roll(self, tick: int, hab: int) -> int:
        """Determina um valor de d10 único para a combinação de tick e HAB."""
        while True:
            roll = self.dice_service.roll_dice(10).final_roll
            if (tick, hab, roll) not in self.timeline_slots:
                return roll

    def add_character(self, character: 'Character', controller: 'CharacterController', start_tick: int = 0):
        """
        Adiciona um personagem à batalha e o agenda na fila de ação.
        """
        self.characters[character.char_id] = character
        self.controllers[character.char_id] = controller
        self.battle_result.action_per_character[character.char_id] = 0
        
        # Tie-break logic
        roll = self._get_unique_roll(start_tick, character.hab)
        self.timeline_slots.add((start_tick, character.hab, roll))
        
        # heapq.heappush adiciona a tupla mantendo a propriedade de Min-Heap
        # Estrutura: (tick, -hab, -roll, char_id, character)
        heapq.heappush(self.timeline, (start_tick, -character.hab, -roll, character.char_id, character))
        
        # Permite que as habilidades inscrevam seus comandos no Event Bus
        for passive in character.passive_abilities:
            if passive in registry:
                passive_instance = registry[passive](character, self)
                hooks = passive_instance.get_hooks()
                for event_name, callback in hooks.items():
                    self.subscribe(event_name, callback)
                self.active_passives[character.char_id].append((passive_instance, hooks))
    
    def remove_character(self, char_id: str):
        character = self.characters.pop(char_id, None)
        self.controllers.pop(char_id, None)
        if character is None:
            return
        for passive_instance, hooks in self.active_passives[char_id]:
            for event_name, callback in hooks.items():
                self.unsubscribe(event_name, callback)
        self.active_passives.pop(char_id)
    
    def get_characters(self) -> List[Character]:
        characters = []
        for key, character in self.characters.items():
            characters.append(character)
        return characters
        
    def get_controller(self, char_id: str) -> 'CharacterController':
        return self.controllers.get(char_id)

    def get_active_passive(self, char_id: str, name: str) -> 'BattlePassive' | None:
        if char_id in self.active_passives:
            for passive_instance, hooks in self.active_passives[char_id]:
                if passive_instance.name == name:
                    return passive_instance
        return None

    def subscribe(self, event_name: str, callback: Callable):
        """
        Inscreve um callback como listener de um event
        """
        if event_name in self.listeners:
            self.listeners[event_name].append(callback)
    
    def unsubscribe(self, event_name: str, callback: Callable):
        """
        Desinscreve um callback como listener de um event
        """
        if event_name in self.listeners:
            self.listeners[event_name].remove(callback)

    def emit(self, event_name: str, payload: 'ActionLoad'):
        """
        Avisa os ouvintes que o evento ocorreu. 
        Os ouvintes modificam o payload original por referência.
        """
        if event_name in self.listeners:
            for callback in self.listeners[event_name]:
                callback(payload)

    def get_next_actor(self) -> 'Character | None':
        """
        Avança o tempo para o próximo personagem na fila.
        Ignora personagens mortos ou que foram removidos da batalha.
        """
        while self.timeline:
            tick, neg_hab, neg_roll, char_id, character = heapq.heappop(self.timeline)
            hab, roll = -neg_hab, -neg_roll
            
            # Remove o slot ocupado do registro
            if (tick, hab, roll) in self.timeline_slots:
                self.timeline_slots.remove((tick, hab, roll))
            
            if char_id in self.characters and CharacterSystem.is_alive(character):
                self.current_tick = tick
                return character
                
        return None

    def schedule_next_action(self, character: Character, action_cost: int):
        """
        Reinsere o personagem na fila de tempo após ele agir.
        """
        next_tick = self.current_tick + action_cost
        roll = self._get_unique_roll(next_tick, character.hab)
        self.timeline_slots.add((next_tick, character.hab, roll))
        
        heapq.heappush(self.timeline, (next_tick, -character.hab, -roll, character.char_id, character))
    
    def delay_character(self, character: 'Character', extra_ticks: int):
        """
        Encontra o personagem na linha do tempo e empurra a ação dele mais para o futuro.
        """
        for i, entry in enumerate(self.timeline):
            tick, neg_hab, neg_roll, char_id, char = entry 
            hab, roll = -neg_hab, -neg_roll
            
            if char_id == character.char_id:
                # 1. Libera o slot antigo
                if (tick, hab, roll) in self.timeline_slots:
                    self.timeline_slots.remove((tick, hab, roll))
                
                # 2. Calcula o novo tempo e roll
                novo_tick = tick + extra_ticks
                novo_roll = self._get_unique_roll(novo_tick, hab)
                self.timeline_slots.add((novo_tick, hab, novo_roll))
                
                # 3. Sobrescreve a tupla na mesma posição do vetor
                self.timeline[i] = (novo_tick, -hab, -novo_roll, char_id, char)
                
                # 4. Reconstrói a árvore de prioridades com o novo valor
                heapq.heapify(self.timeline)
                
                break # Achou e atualizou, pode sair do laço
  
    def resolve_deaths(self):
        """Varre o campo de batalha em busca de personagens caídos e os move para o cemitério."""
        mortos_neste_turno = []
        
        # Iteramos sobre uma cópia das chaves (list) porque vamos deletar itens do dicionário original
        for char_id in list(self.characters.keys()):
            personagem = self.characters[char_id]
            
            if not CharacterSystem.is_alive(personagem):
                mortos_neste_turno.append(personagem)
                # Remove do dicionário de vivos
                self.remove_character(char_id)
                # Salva no cemitério
                self.graveyard[char_id] = personagem
                
                # Dispara o evento de morte (útil para passivas como "Ganhe +10 de Ataque quando um aliado morrer")
                self.emit("on_character_death", ActionLoad(character=personagem))
                
                # Registra no histórico global
                self.battle_result.history.append(f"[MORTE] {personagem.name} foi derrotado!")

    def run_battle(self):
        while True:
            self.battle_state = self.judge.rule(self)
            if self.battle_state is not BattleState.RUNNING:
                break
            actor = self.get_next_actor()
            if actor is None:
                self.battle_state = BattleState.ERROR
                self.battle_result.history.append("[ERRO] Timeline se tornou vazia antes da batalha acabar")
                break
            
            self.emit("on_turn_start", ActionLoad(character = actor))
            self.resolve_deaths()

            last_action_load = None
            final_action = None

            # Free Action Loop
            while True:
                if not CharacterSystem.is_alive(actor) or self.battle_state != BattleState.RUNNING:
                    break

                action = self.controllers[actor.char_id].choose_action(actor, self)
                final_action = action

                # Pega os hooks da ação
                action_hooks = {}
                if hasattr(action, 'get_hooks'):
                    action_hooks = action.get_hooks()
                    
                try:
                    for event_name, callback in action_hooks.items():
                        self.subscribe(event_name, callback)
                        
                    action_load = action.execute_if_possible()

                    decision_attempts = 0
                    max_attempts = 1000

                    while not action_load.success:
                        decision_attempts += 1
                        if decision_attempts >= max_attempts:
                            self.battle_state = BattleState.ERROR
                            self.battle_result.history.append(f"[ERRO CRÍTICO] Controller de {actor.name} entrou em decision loop!")
                            break 
                        
                        for event_name, callback in action_hooks.items():
                            self.unsubscribe(event_name, callback)
                        
                        action = self.controllers[actor.char_id].choose_action(actor, self, action_load)
                        final_action = action
                        
                        action_hooks = {}
                        if hasattr(action, 'get_hooks'):
                            action_hooks = action.get_hooks()
                        for event_name, callback in action_hooks.items():
                            self.subscribe(event_name, callback)
                            
                        action_load = action.execute_if_possible()
                    
                    if self.battle_state == BattleState.ERROR:
                        break
                    
                    self.battle_result.history.extend(action_load.history)
                    last_action_load = action_load

                    if action.action_type != BattleActionType.FREE_ACTION:
                        break
                    
                    self.resolve_deaths()
                    self.battle_state = self.judge.rule(self)

                finally:
                    for event_name, callback in action_hooks.items():
                        self.unsubscribe(event_name, callback)

            if self.battle_state == BattleState.ERROR:
                break
            
            if last_action_load:
                self.emit("on_turn_end", last_action_load)
            
            self.resolve_deaths()
            
            if final_action:
                action_cost = actor.action_cost_base
                if final_action.action_type == BattleActionType.MOVE_ACTION:
                    action_cost = action_cost//2
                self.schedule_next_action(actor, action_cost)
            
            self.battle_result.duration += 1
            self.battle_result.action_per_character[actor.char_id] += 1

