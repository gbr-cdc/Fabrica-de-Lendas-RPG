import heapq
from Models import Character
from typing import List, Callable, Dict, Any
from core.DiceService import DiceService


class BattleManager:
    """
    O Gerenciador Central. Controla o Relógio de Ticks e o Event Bus (Observer Pattern).
    """
    def __init__(self, dice_service: 'DiceService'):
        # Min-Heap para o Relógio de Ticks: (tick_number, char_id, character_object)
        self.timeline = []
        self.current_tick = 0

        # Injeção do serviço de dados
        self.dice_service = dice_service
        
        #Lista de personagens na batalha, acessível por char_id
        self.characters: Dict[str, Character] = {}
        
        # Event Bus (Observer Pattern) para passivas e aprimoramentos
        self.listeners: Dict[str, List[Callable]] = {
            'on_turn_start': [],
            'on_roll_modify': [],
            'on_defense_reaction': [],
            'on_hit_check': [],
            'on_gda_modify': [],
            'on_damage_calculation': [],
            'on_damage_taken': [],
            'on_attack_end': [],
            'on_turn_end': []
        }

    def add_character(self, character: 'Character', start_tick: int = 0):
        """
        Adiciona um personagem à batalha e o agenda na fila de ação.
        """
        self.characters[character.char_id] = character
        # heapq.heappush adiciona a tupla (start_tick, char_id, character) mantendo a propriedade de Min-Heap
        heapq.heappush(self.timeline, (start_tick, character.char_id, character))
        
        # Permite que as habilidades inscrevam seus comandos no Event Bus
        for ability in character.abilities:
            ability.register_listeners(character, self)

    # Métodos para manipular o Event Bus
    def subscribe(self, event_name: str, callback: Callable):
        if event_name in self.listeners:
            self.listeners[event_name].append(callback)
    
    def unsubscribe(self, event_name: str, callback: Callable):
        if event_name in self.listeners:
            self.listeners[event_name].remove(callback)
    

    def emit(self, event_name: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispara um evento para todos os ouvintes. Os ouvintes podem modificar o event_data (ex: dobrar GdA).
        """
        if event_name in self.listeners:
            for callback in self.listeners[event_name]:
                callback(event_data)
        return event_data

    def get_next_actor(self) -> 'None | Character':
        """
        Avança o tempo para o próximo personagem na fila.
        """
        if not self.timeline:
            return None
            
        tick, char_id, character = heapq.heappop(self.timeline)
        self.current_tick = tick
        return character

    def schedule_next_action(self, character: Character, action_cost: int):
        """
        Reinsere o personagem na fila de tempo após ele agir.
        """
        next_tick = self.current_tick + action_cost
        heapq.heappush(self.timeline, (next_tick, character.char_id, character))
    
    def delay_character(self, character: 'Character', extra_ticks: int | float):
        """
        Encontra o personagem na linha do tempo e empurra a ação dele mais para o futuro.
        """
        for i, entry in enumerate(self.timeline):
            tick, char_id, char = entry 
            
            if char_id == character.char_id:
                # 1. Remove a "senha" antiga da fila
                self.timeline.pop(i)
                
                # 2. Calcula o novo tempo (empurrando pro futuro)
                novo_tick = tick + extra_ticks
                
                # 3. Insere a nova "senha" usando heappush para manter a propriedade de heap
                heapq.heappush(self.timeline, (novo_tick, char_id, char))
                
                break # Achou o personagem, não precisa continuar procurando