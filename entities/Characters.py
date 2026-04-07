
from __future__ import annotations
from typing import List
from controllers.CharacterController import CharacterController
from core.Enums import AttributeType
from core.Structs import CombatStyle, GameRules
from entities.Items import Armor, Weapon
from combat.PassiveAbilities import PassiveAbility
from combat.StatusEffects import StatusEffect

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
    