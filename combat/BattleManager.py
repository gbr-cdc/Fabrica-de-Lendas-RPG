from __future__ import annotations
import heapq
from typing import List, Callable, Dict, TYPE_CHECKING
from collections import defaultdict
from core.Enums import BattleState, BattleActionType
from core.Structs import BattleResult, AttackActionTemplate
from core.Events import ActionLoad
from combat.BattlePassives import registry
from core.CharacterSystem import CharacterSystem

if TYPE_CHECKING:
    from core.DataManager import DataManager
    from combat.Judges import BattleJudge
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

    def add_character(self, character: 'Character', controller: 'CharacterController', start_tick: int = 0):
        """
        Adiciona um personagem à batalha e o agenda na fila de ação.
        """
        self.characters[character.char_id] = character
        self.controllers[character.char_id] = controller
        self.battle_result.action_per_character[character.char_id] = 0
        # heapq.heappush adiciona a tupla (start_tick, char_id, character) mantendo a propriedade de Min-Heap
        heapq.heappush(self.timeline, (start_tick, character.char_id, character))
        
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
            tick, char_id, character = heapq.heappop(self.timeline)
            
            if char_id in self.characters and CharacterSystem.is_alive(character):
                self.current_tick = tick
                return character
                
        return None

    def schedule_next_action(self, character: Character, action_cost: int):
        """
        Reinsere o personagem na fila de tempo após ele agir.
        """
        next_tick = self.current_tick + action_cost
        heapq.heappush(self.timeline, (next_tick, character.char_id, character))
    
    def delay_character(self, character: 'Character', extra_ticks: int):
        """
        Encontra o personagem na linha do tempo e empurra a ação dele mais para o futuro.
        """
        for i, entry in enumerate(self.timeline):
            tick, char_id, char = entry 
            
            if char_id == character.char_id:
                # 1. Calcula o novo tempo
                novo_tick = tick + extra_ticks
                
                # 2. Sobrescreve a tupla na mesma posição do vetor (Evita o shift de memória do pop)
                self.timeline[i] = (novo_tick, char_id, char)
                
                # 3. Reconstrói a árvore de prioridades com o novo valor
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

            action = self.controllers[actor.char_id].choose_action(actor, self)

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
                        break # Quebra o while interno
                    
                    # Se falhou, temos que limpar os antigos hooks antes de tentar uma nova ação
                    for event_name, callback in action_hooks.items():
                        self.unsubscribe(event_name, callback)
                    
                    action = self.controllers[actor.char_id].choose_action(actor, self, action_load)
                    
                    action_hooks = {}
                    if hasattr(action, 'get_hooks'):
                        action_hooks = action.get_hooks()
                    for event_name, callback in action_hooks.items():
                        self.subscribe(event_name, callback)
                        
                    action_load = action.execute_if_possible()
            finally:
                for event_name, callback in action_hooks.items():
                    self.unsubscribe(event_name, callback)
            
            if self.battle_state == BattleState.ERROR:
                break
            
            self.emit("on_turn_end", action_load)
            self.resolve_deaths()
            self.battle_result.history.extend(action_load.history)
            action_cost = actor.action_cost_base
            if action.action_type == BattleActionType.MOVE_ACTION:
                action_cost = action_cost//2
            self.schedule_next_action(actor, action_cost)
            self.battle_result.duration += 1
            self.battle_result.action_per_character[actor.char_id] += 1

