
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any
from BattleManager import BattleManager

# Enum para estado de rolagem (vantagem, desvantagem, neutro)
class RollState(Enum):
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disavantage"
    NEUTRAL = "neutral"

# Enums para tipos de armadura, armas, atributos e status
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

# --- MODELOS DE DADOS ---
# GameRules representa parâmetros de configuração do jogo (Atualmente apenas as tabelas de progressão)
@dataclass
class GameRules:
    hp_table: Dict[str, int]
    mp_table: Dict[str, int]
    action_cost_table: Dict[str, int]
    limite_foco: int  # Limite máximo de foco = limite_foco * MEN
    limite_mana: int  # Limite máximo de mana = limite_mana * MEN

# Estilos de Combate, Armas e Armaduras com seus parâmetros de acordo com as regras
@dataclass
class CombatStyle:
    name: str
    atq_die: int
    def_die: int
    main_stat: AttributeType
    armor_type: ArmorType
    weapon_type: WeaponType

@dataclass
class Weapon:
    name: str
    db: int
    mda: int
    type: WeaponType
    properties: List[Ability] = field(default_factory=list)

@dataclass
class Armor:
    name: str
    type: ArmorType
    hp_bonus: int
    properties: List[Ability] = field(default_factory=list)


class Ability:
    """
    Command Pattern: Cada habilidade (inclusive o ataque básico) é um objeto encapsulado.
    """
    def __init__(self, name: str, focus_cost: int, action_cost: int):
        self.name = name
        self.focus_cost = focus_cost
        self.action_cost = action_cost

    def register_listeners(self, caster: 'Character', battle_manager: 'BattleManager'):
        """
        Método sobrescrito por habilidades passivas para se inscreverem no Event Bus.
        Por padrão, não faz nada.
        """
        pass

    def can_execute(self, caster: 'Character', target: 'Character') -> tuple[bool, str]:
        """
        Valida se a habilidade pode ser usada ANTES de gastar o turno.
        Retorna (Pode Usar?, "Mensagem de Erro")
        """        
        return True, ""

    def execute(self, caster: 'Character', target: 'Character', battle_manager: 'BattleManager') -> Dict[str, Any]:
        """
        Executa a lógica da habilidade e retorna um dicionário de resultados para a View ler.
        Deve ser sobrescrito por subclasses.
        """
        # O campo history no dicionário retornado é usado por padrão para mostrar o histórico de execução
        # Se execute for chamado sem implementação, retorna uma mensagem de erro
        return {
            "history": f"Habilidade {self.name} não pode ser executada!",
            "executed": False
        }
    
    def execute_if_possible(self, caster: 'Character', target: 'Character', battle_manager: 'BattleManager') -> Dict[str, Any]:
        """
        Wrapper que garante que can_execute seja chamado antes de execute.
        Retorna o resultado de execute se permitido, ou um dicionário de erro se não.
        """
        can_use, msg = self.can_execute(caster, target)
        if not can_use:
            return {"history": msg, "executed": False}
        return self.execute(caster, target, battle_manager)

class Character:
    """
    A representação dos dados e status do personagem.
    """
    def __init__(self, char_id: str, name: str, attributes: List[int], combat_style: CombatStyle, rules: GameRules):
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
        self.abilities: List[Ability] = []
        self.status_effects: List[StatusEffect] = []
    
    def generate_focus(self) -> int:

        # Limite máximo de foco
        max_focus = self.rules.limite_foco * self.men
    
        self.floating_focus = min(self.floating_focus + self.men, max_focus)
    
        return self.floating_focus
    
    def generate_mana(self) -> int:

        # Limite máximo de mana engatilhada
        max_floating = self.rules.limite_mana * self.men
        
        space_available = max_floating - self.floating_mp
        
        mana_to_pull = min(self.men, space_available, self.current_mp)
        
        self.current_mp -= mana_to_pull
        self.floating_mp += mana_to_pull
        
        return self.floating_mp
    
    def take_damage(self, damage: int):
        self.current_hp = max(self.current_hp - damage, 0)

    def spend_focus(self, amount: int) -> bool:
        if self.floating_focus >= amount:
            self.floating_focus -= amount
            return True
        return False
    
    def spend_mana(self, amount: int) -> bool:
        if self.floating_mp >= amount:
            self.floating_mp -= amount
            return True
        return False

    def is_alive(self) -> bool:
        return self.current_hp > 0
    
    def equip_weapon(self, new_weapon: Weapon) -> tuple[bool, str, Weapon | None]:
        if new_weapon.type != self.combat_style.weapon_type:
            return False, f"{self.name} não pode equipar armas do tipo {new_weapon.type.value}.", None
            
        old_weapon = self.weapon
        self.weapon = new_weapon

        bonus = self.attribute_map[self.combat_style.main_stat]

        self.pda = new_weapon.db + bonus
        self.mda = new_weapon.mda

        return True, f"{new_weapon.name} equipada com sucesso!", old_weapon

    def equip_armor(self, new_armor: Armor) -> tuple[bool, str, Armor | None]:
        if new_armor.type != self.combat_style.armor_type:
            return False, f"{self.name} não pode equipar armaduras do tipo {new_armor.type.value}.", None
            
        old_armor = self.armor

        if self.armor is not None:
            self.max_hp -= self.armor.hp_bonus
            self.current_hp = max(self.current_hp - self.armor.hp_bonus, 1)
        
        self.armor = new_armor
        self.max_hp += new_armor.hp_bonus
        self.current_hp += new_armor.hp_bonus

        return True, f"{new_armor.name} equipada com sucesso!", old_armor
    
class StatusEffect:
    def __init__(self, name: str, duration: int, target: 'Character'):
        self.name = name
        self.duration = duration
        self.character = target
        self.battle_manager = None
        
    # --- MÉTODOS DO MOTOR ---
    def apply(self, battle_manager: 'BattleManager'):
        self.battle_manager = battle_manager
        self.character.status_effects.append(self)
        
        if self.battle_manager is not None:
            self.battle_manager.subscribe('on_turn_end', self._tick_duration)
        
        self.on_apply() 
        self.on_subscribe(self.battle_manager)

    def remove(self):
        if self.battle_manager is not None:
            self.battle_manager.unsubscribe('on_turn_end', self._tick_duration)
            self.on_unsubscribe(self.battle_manager)
        self.on_remove()

    def _tick_duration(self, event_data: dict) -> dict:
        if event_data.get('character') and event_data['character'].char_id == self.character.char_id:
            self.duration -= 1
            event_data = self.on_tick(event_data)
            
            if self.duration <= 0:
                self.remove()
                if self in self.character.status_effects:
                    self.character.status_effects.remove(self)
        return event_data

    # --- MÉTODOS DE GAME DESIGN ---
    # Agora você pode voltar a usar self.character livremente aqui dentro!
    def on_apply(self):
        pass

    def on_subscribe(self, battle_manager: 'BattleManager'):
        pass

    def on_remove(self):
        pass

    def on_unsubscribe(self, battle_manager: 'BattleManager'):
        pass

    def on_tick(self, event_data: dict) -> dict:
        return event_data
        

