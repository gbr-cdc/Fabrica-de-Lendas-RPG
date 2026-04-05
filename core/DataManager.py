import json

from core.Models import Armor, ArmorType, AttributeType, CombatStyle, Character, GameRules, Weapon, WeaponType
from implementation.Registry import ability_registry

def load_combat_styles(filepath: str) -> dict[str, CombatStyle]:
    """
    Carrega os estilos de combate a partir de um arquivo JSON e converte as strings para os Enums correspondentes.
    """
    #Abre o JSON
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    #Monta o dicionário de CombatStyles, convertendo as strings para os Enums
    styles = {}
    for key, val in data.items():
        styles[key] = CombatStyle(
            name=val["name"],
            atq_die=val["atq_die"],
            def_die=val["def_die"],
            # Converte strings para Enums para manter consistência
            main_stat=AttributeType(val["main_stat"]),
            armor_type=ArmorType(val["armor_type"]),
            weapon_type=WeaponType(val["weapon_type"])
        )
    
    # Retorna o dicionário de estilos de combate
    return styles

def load_game_rules(filepath: str) -> GameRules:
    """
    Carrega as regras do jogo (atualmente apenas as tabelas de progressão) a partir de um arquivo JSON e retorna um objeto GameRules.
    """
    # Abre o JSON
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Carrega as tabelas de progressão e retorna um objeto GameRules
    regras = data["regras_progressao"]
    return GameRules(
        hp_table=regras["tabela_hp"],
        mp_table=regras["tabela_mp"],
        action_cost_table=regras["tabela_custos"]
    )

def load_characters(filepath: str, combat_styles: dict[str, CombatStyle], rules: GameRules) -> dict[str, Character]:
    """
    Carrega os personagens a partir de um arquivo JSON, criando instâncias de Character. Retorna um dicionário de personagens acessível por char_id.
    """
    # Abre o JSON
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Inicializa o dicionário de personagens
    characters = {}

    # Para cada tupla (char_id, char_data) no JSON...
    for key, char_data in data.items():
        # Cria o personagem a partir de char_data
        char = Character(
            char_id=key,
            name=char_data["Nome"],
            attributes=[char_data["FIS"], char_data["HAB"], char_data["MEN"]],
            combat_style=combat_styles[char_data["CombatStyle"]],
            rules=rules
        )

        # Cria a arma e armadura a partir de char_data e equipa o personagem
        weapon = Weapon(
            name=char_data["Weapon"]["name"],
            db=char_data["Weapon"]["db"],
            mda=char_data["Weapon"]["mda"],
            type=WeaponType(char_data["Weapon"]["type"])
        )
        char.equip_weapon(weapon)
        
        armor = Armor(
            name=char_data["Armor"]["name"],
            hp_bonus=char_data["Armor"]["hp_bonus"],
            type=ArmorType(char_data["Armor"]["type"])
        )
        char.equip_armor(armor)

        # Itera sobre as habilidades listadas no JSON e cria as instâncias usando o ability_registry
        character_abilities = []
        for ability_name in char_data.get("Abilities", []):
            if ability_name not in ability_registry:
                raise ValueError(f"Habilidade desconhecida no JSON: {ability_name}")
            character_abilities.append(ability_registry[ability_name]())
        
        # Coloca a lista de habilidades no personagem
        char.abilities = character_abilities
        
        # Adiciona o personagem ao dicionário
        characters[key] = char
    
    return characters