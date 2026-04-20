from __future__ import annotations
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from entities.Characters import Character
    from entities.Items import Weapon, Armor

class CharacterSystem:
    """
    Sistema sem estado que manipula os dados da entidade Character.
    Isola a lógica de domínio (verificação de mana, dano, equipamentos) do container de dados.
    """

    @staticmethod
    def generate_focus(character: 'Character') -> int:
        max_focus = character.rules.limite_foco * character.men
        character.floating_focus = min(character.floating_focus + character.men, max_focus)
        return character.floating_focus
    
    @staticmethod
    def generate_mana(character: 'Character') -> int:
        max_floating = character.rules.limite_mana * character.men
        space_available = max_floating - character.floating_mp
        mana_to_pull = min(character.men, space_available, character.current_mp)
        
        character.current_mp -= mana_to_pull
        character.floating_mp += mana_to_pull
        
        return character.floating_mp
    
    @staticmethod
    def take_damage(character: 'Character', damage: int):
        character.current_hp = max(character.current_hp - damage, 0)

    @staticmethod
    def spend_focus(character: 'Character', amount: int) -> bool:
        if character.floating_focus >= amount:
            character.floating_focus -= amount
            return True
        return False
    
    @staticmethod
    def spend_mana(character: 'Character', amount: int) -> bool:
        if character.floating_mp >= amount:
            character.floating_mp -= amount
            return True
        return False

    @staticmethod
    def is_alive(character: 'Character') -> bool:
        return character.current_hp > 0
    
    @staticmethod
    def equip_weapon(character: 'Character', new_weapon: 'Weapon') -> Tuple[bool, str, 'Weapon' | None]:
        if new_weapon.type != character.combat_style.weapon_type:
            return False, f"{character.name} não pode equipar armas do tipo {new_weapon.type.value}.", None
            
        old_weapon = character.weapon
        character.weapon = new_weapon

        bonus = character.attribute_map[character.combat_style.main_stat]

        character.base_pda = new_weapon.db + bonus
        character.base_mda = new_weapon.mda

        return True, f"{new_weapon.name} equipada com sucesso!", old_weapon

    @staticmethod
    def equip_armor(character: 'Character', new_armor: 'Armor') -> Tuple[bool, str, 'Armor' | None]:
        if new_armor.type != character.combat_style.armor_type:
            return False, f"{character.name} não pode equipar armaduras do tipo {new_armor.type.value}.", None
        
        old_armor = character.armor

        if character.armor is not None:
            character.max_hp -= character.armor.hp_bonus
            character.current_hp = max(character.current_hp - character.armor.hp_bonus, 1)
        
        character.armor = new_armor
        character.max_hp += new_armor.hp_bonus
        character.current_hp += new_armor.hp_bonus

        return True, f"{new_armor.name} equipada com sucesso!", old_armor
