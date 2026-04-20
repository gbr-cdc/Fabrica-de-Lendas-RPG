
from __future__ import annotations
from typing import List, TYPE_CHECKING
from core.Enums import AttributeType
from core.Structs import CombatStyle, GameRules
from entities.Items import Armor, Weapon

if TYPE_CHECKING:
    from core.Modifiers import StatModifier
    from combat.StatusEffects import StatusEffect

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
        self.base_rank = 0
        # Bônus de Ataque e Defesa
        self.base_bda = 0
        self.base_bdd = 0
        # Bônus de Precisão e Guarda
        self.base_pre = 0
        self.base_grd = 0
        # Dano
        self.base_pda = self.attribute_map[combat_style.main_stat]
        self.base_mda = 1
        
        # Habilidades e Efeitos
        self.active_abilities: List[str] = []
        self.passive_abilities: List[str] = []
        self.status_effects: List['StatusEffect'] = []
        self.modifiers: List['StatModifier'] = []
    
    def get_stat_total(self, stat_name: str, base_value: int) -> int:
        total = base_value
        for mod in self.modifiers:
            if mod.stat_name == stat_name:
                total += mod.value
        return total

    @property
    def rank(self) -> int:
        return self.get_stat_total('rank', self.base_rank)

    @property
    def bda(self) -> int:
        return self.get_stat_total('bda', self.base_bda)

    @property
    def bdd(self) -> int:
        return self.get_stat_total('bdd', self.base_bdd)

    @property
    def pre(self) -> int:
        return self.get_stat_total('pre', self.base_pre)

    @property
    def grd(self) -> int:
        return self.get_stat_total('grd', self.base_grd)

    @property
    def pda(self) -> int:
        return self.get_stat_total('pda', self.base_pda)

    @property
    def mda(self) -> int:
        return self.get_stat_total('mda', self.base_mda)

    def add_modifier(self, modifier: 'StatModifier'):
        self.modifiers.append(modifier)
        
    def remove_modifier(self, modifier: 'StatModifier'):
        if modifier in self.modifiers:
            self.modifiers.remove(modifier)
            
    def clear_ephemeral_modifiers(self):
        from core.Modifiers import EphemeralModifier
        self.modifiers = [m for m in self.modifiers if not isinstance(m, EphemeralModifier)]

    def add_status_effect(self, effect: 'StatusEffect'):
        self.status_effects.append(effect)

    def remove_status_effect(self, effect: 'StatusEffect'):
        if effect in self.status_effects:
            self.status_effects.remove(effect)


    