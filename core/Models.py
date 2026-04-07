
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any
from BattleManager import BattleManager
from controllers.CharacterController import CharacterController

# --- ENUMS ---
class RollState(Enum):
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disavantage"
    NEUTRAL = "neutral"

class ArmorType(Enum):
    ROBE = "robe"
    LIGHT = "light"
    HEAVY = "heavy"

class WeaponType(Enum):
    GREAT_WEAPON = "great_weapon",
    MEDIUM_WEAPON = "medium_weapon",
    LIGHT_WEAPON = "light_weapon",
    DOUBLE_WEAPON = "double_weapon",
    WEAPON_AND_SHIELD = "weapon_and_shield",
    RANGED_WEAPON = "ranged_weapon",
    MAGICAL_FOCUS = "magical_focus"

class AttributeType(Enum):
    FIS = "FIS"
    HAB = "HAB"
    MEN = "MEN"

class StatusEffectType(Enum):
    ATORDOADO = "Atordoado"
    ENVENENADO = "Envenenado"
    QUEIMADO = "Queimado"

class AttackType(Enum):
    BASIC_ATTACK = "basic_attack"
    SKILL = "skill"

class BattleActionType(Enum):
    MOVE_ACTION = "move_action"
    STANDARD_ACTION = "standard_action"

# --- MODELOS DE DADOS ---
@dataclass
class GameRules:
    hp_table: Dict[str, int]
    mp_table: Dict[str, int]
    action_cost_table: Dict[str, int]
    limite_foco: int  # Limite máximo de foco = limite_foco * MEN
    limite_mana: int  # Limite máximo de mana = limite_mana * MEN

@dataclass(kw_only=True)
class ActionLoad:
    """Objeto base para trafegar dados no Event Bus e retornar resultados para a View."""
    character: 'Character'
    history: List[str] = field(default_factory=list)
    success: bool = True  # Por padrão, assumimos que a ação vai dar certo

@dataclass(kw_only=True)
class AttackLoad(ActionLoad):
    """Objeto específico para resultados de ataques, com campos adicionais para dados relevantes de combate."""
    target: 'Character'
    battle_manager: 'BattleManager'
    attack_type: AttackType = AttackType.BASIC_ATTACK
    attack_state: RollState = RollState.NEUTRAL
    defense_state: RollState = RollState.NEUTRAL
    hit: bool = False
    gda: int = 0
    damage: int = 0

@dataclass
class RollResult:
    """Objeto para resultados de rolagens, usado principalmente para o Event Bus."""
    final_roll: int
    roll1: int
    roll2: int | None = None  # Em caso de vantagem/desvantagem
    rollstate: RollState = RollState.NEUTRAL
    scheduled: bool = False  # Indica se a rolagem veio de um valor agendado (para testes)

@dataclass
class CombatStyle:
    name: str
    atq_die: int
    def_die: int
    main_stat: AttributeType
    armor_type: ArmorType
    weapon_type: WeaponType

@dataclass
class BattleActionTemplate:
    id: str
    nome: str
    action_type: BattleActionType
    focus_cost: int
    command: type[BattleAction]

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

# --- CLASSES BASE ---
class GameAction:
    """
    Representação geral de comandos que podem ser gerados por Controllers
    """
    def __init__(self, name: str, actor: 'Character'):
        self.name = name
        self.actor = actor

    def can_execute(self) -> tuple[bool, str]:
        """
        Valida se a ação pode ser usada
        """        
        raise NotImplementedError("Chamou can_execute() sem implementação.")

    def execute(self) -> ActionLoad:
        """
        Executa a lógica da ação
        """
        raise NotImplementedError("Chamou execute() sem implementação.")
    
    def execute_if_possible(self) -> ActionLoad:
        """
        Wrapper para chamar can_execute antes de execute.
        """
        can, msg = self.can_execute()
        if not can:
            return ActionLoad(character=self.actor, history=[msg], success=False)
        return self.execute()

class BattleAction(GameAction):
    """
    Comandos executados no contexto de batalha.
    """
    # Parâmetros relevantes recebidos através do construtor, de forma que os métodos não possuam parâmetros em conformidade com o Command Pattern
    def __init__(self, template: 'BattleActionTemplate', actor: 'Character', target: 'Character', battle_manager: 'BattleManager'):
        super().__init__(name=template.nome, actor=actor)
        self.action_type = template.action_type
        self.focus_cost = template.focus_cost
        self.target = target
        self.battle_manager = battle_manager

    def can_execute(self) -> tuple[bool, str]:
        """
        Valida se a ação pode ser usada, retorna uma tupla (Sucesso?, "Mensagem de Erro ou Sucesso").
        Por padrão, retorna true, mas habilidades ativas devem sobrescrever para validar custo de foco, alcance, etc.
        """        
        return True, ""

    def execute(self) -> ActionLoad:
        """
        Executa a lógica da ação e retorna um ActionLoad com um histórico do resultado.
        Por padrão, retorna um ActionLoad indicando que a habilidade não pode ser executada, mas habilidades ativas devem sobrescrever para implementar sua lógica.
        """
        return ActionLoad(character=self.actor, history=[f"A abilidade {self.name} não pode ser executada!"], success=False)

class PassiveAbility:
    """
    Representa características estáticas ou passivas que não podem ser conjuradas.
    Elas apenas alteram regras do motor através do Event Bus.
    """
    def __init__(self, name: str, owner: 'Character', battle_manager: 'BattleManager'):
        self.name = name
        self.owner = owner
        self.battle_manager = battle_manager
        self.active_hooks = [] # Guarda os recibos para limpar automaticamente depois!

    def register_listeners(self):
        """Deve ser implementado pelas classes filhas para criar e inscrever os hooks."""
        raise NotImplementedError

    def unregister_listeners(self):
        """
        Limpa todos os hooks automaticamente.
        """
        for event_name, hook in self.active_hooks:
            self.battle_manager.unsubscribe(event_name, hook)
        self.active_hooks.clear()

class Character:
    """
    A representação dos dados e status do personagem.
    """
    def __init__(self, char_id: str, name: str, attributes: List[int], combat_style: CombatStyle, rules: GameRules, controller: CharacterController):
        self.controller = controller
        
        # Identificação
        self.char_id = char_id
        self.name = name
        
        # Atributos base
        self.rules = rules
        self.fis, self.hab, self.men = attributes
        self.max_hp = rules.hp_table[str(self.fis)]
        self.max_mp = rules.mp_table[str(self.men)]
        self.action_cost_base = rules.action_cost_table[str(self.hab)]
        self.current_mp = self.max_mp
        self.current_hp = self.max_hp
        self.floating_mp = 0  
        self.floating_focus = 0

        self.attribute_map = {
            AttributeType.FIS: self.fis,
            AttributeType.HAB: self.hab,
            AttributeType.MEN: self.men
        }
        
        
        # Estilo de Combate e Equipamentos
        self.weapon = None
        self.armor = None
        self.atk_die = combat_style.atq_die
        self.def_die = combat_style.def_die
        self.combat_style = combat_style
        # Bônus de Rank
        self.rank = 0
        # Bônus de Ataque e Defesa
        self.bda = 0
        self.bdd = 0
        # Bônus de Precisão e Guarda
        self.pre = 0
        self.grd = 0
        # Dano
        self.pda = self.attribute_map[combat_style.main_stat]
        self.mda = 1
        
        # Habilidades e Efeitos
        self.active_abilities: List[str] = []
        self.passive_abilities: List[str] = []
        self.active_passives: List[PassiveAbility] = []
        self.status_effects: List[StatusEffect] = []
    
    def generate_focus(self) -> int:
        """
        Gasta MP para gerar Floating Focus, respeitando o limite máximo. Retorna a quantidade atual de Floating Focus.
        """

        # Limite máximo de foco
        max_focus = self.rules.limite_foco * self.men
    
        self.floating_focus = min(self.floating_focus + self.men, max_focus)
    
        return self.floating_focus
    
    def generate_mana(self) -> int:
        """ 
        Gasta MP para gerar Floating MP, respeitando o limite máximo. Retorna a quantidade atual de Floating MP. 
        """

        # Limite máximo de mana manifestada
        max_floating = self.rules.limite_mana * self.men
        
        # Espaço disponível para manifestar mais mana
        space_available = max_floating - self.floating_mp

        # Determina quanta mana pode ser manifestada
        mana_to_pull = min(self.men, space_available, self.current_mp)
        
        self.current_mp -= mana_to_pull
        self.floating_mp += mana_to_pull
        
        return self.floating_mp
    
    def take_damage(self, damage: int):
        """
        Aplica dano ao personagem, reduzindo seu HP. Garante que o HP não fique negativo.
        """
        # Futuramente deve mandar um sinal para o BattleManager caso o personagem morra (current_hp <= 0) para ele ser removido da batalha
        self.current_hp = max(self.current_hp - damage, 0)

    def spend_focus(self, amount: int) -> bool:
        """
        Tenta gastar a quantidade especificada de Floating Focus. Retorna True se conseguiu gastar, ou False se não tinha foco suficiente.
        """
        if self.floating_focus >= amount:
            self.floating_focus -= amount
            return True
        return False
    
    def spend_mana(self, amount: int) -> bool:
        """ 
        Tenta gastar a quantidade especificada de Floating MP. Retorna True se conseguiu gastar, ou False se não tinha mana suficiente.
        """
        if self.floating_mp >= amount:
            self.floating_mp -= amount
            return True
        return False

    def is_alive(self) -> bool:
        """ 
        Verifica se o personagem ainda está vivo (HP > 0).
        """
        return self.current_hp > 0
    
    def equip_weapon(self, new_weapon: Weapon) -> tuple[bool, str, Weapon | None]:
        """
        Tenta equipar a nova arma. Retorna (Sucesso?, "Mensagem", Arma Antiga ou None)
        """
        # Verifica se o tipo da arma é compatível com o estilo de combate do personagem
        if new_weapon.type != self.combat_style.weapon_type:
            return False, f"{self.name} não pode equipar armas do tipo {new_weapon.type.value}.", None
            
        # Guarda a arma antiga para devolver no retorno
        old_weapon = self.weapon
        self.weapon = new_weapon

        # Pega o valor do atributo principal do personagem para calcular o bônus de ataque
        bonus = self.attribute_map[self.combat_style.main_stat]

        # Atualiza os valores de PDA e MDA do personagem com base na nova arma
        self.pda = new_weapon.db + bonus
        self.mda = new_weapon.mda

        return True, f"{new_weapon.name} equipada com sucesso!", old_weapon

    def equip_armor(self, new_armor: Armor) -> tuple[bool, str, Armor | None]:
        """
        Tenta equipar a nova armadura. Retorna (Sucesso?, "Mensagem", Armadura Antiga ou None)
        """
        # Verifica se o tipo da armadura é compatível com o estilo de combate do personagem
        if new_armor.type != self.combat_style.armor_type:
            return False, f"{self.name} não pode equipar armaduras do tipo {new_armor.type.value}.", None
        
        # Guarda a armadura antiga para devolver no retorno
        old_armor = self.armor

        # Se já estiver usando uma armadura, remove o bônus de HP dela antes de equipar a nova
        if self.armor is not None:
            self.max_hp -= self.armor.hp_bonus
            self.current_hp = max(self.current_hp - self.armor.hp_bonus, 1)
        
        # Equipa a nova armadura e aplica o bônus de HP dela
        self.armor = new_armor
        self.max_hp += new_armor.hp_bonus
        self.current_hp += new_armor.hp_bonus

        return True, f"{new_armor.name} equipada com sucesso!", old_armor
    
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
        

