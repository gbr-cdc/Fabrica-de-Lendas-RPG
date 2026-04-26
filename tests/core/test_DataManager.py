import pytest
import json
from unittest.mock import patch, mock_open
from core.DataManager import DataManager
from core.Structs import CombatStyle, GameRules, AttackActionTemplate
from core.Enums import AttributeType, ArmorType, WeaponType, BattleActionType, AttackType

def test_load_combat_styles():
    dm = DataManager()
    dm.load_combat_styles('data/CombatStyles.json')
        
    style = dm.get_combat_style("Destruidor")
    assert style.name == "Destruidor"
    assert style.main_stat == AttributeType.FIS
    assert style.armor_type == ArmorType.HEAVY
    
    style = dm.get_combat_style("Duelista")
    assert style.name == "Duelista"
    assert style.main_stat == AttributeType.HAB
    assert style.armor_type == ArmorType.LIGHT

def test_load_game_rules():
    dm = DataManager()
    dm.load_game_rules('data/Rules.json')
        
    assert dm._game_rules.limite_foco == 5
    assert dm._game_rules.hp_table["10"] == 155

def test_load_action_templates():
    dm = DataManager()
    dm.load_action_templates('data/AttackActions.json')
        
    template = dm.get_action_template("BasicAttack")
    assert template.nome == "Ataque Básico"
    assert template.action_type == BattleActionType.STANDARD_ACTION
    assert template.attack_type == AttackType.BASIC_ATTACK
    assert len(template.effects) == 0
    
    template = dm.get_action_template("SkillN1")
    assert template.nome == "Habilidade Nível 1"
    assert len(template.effects) == 1
    assert template.effects[0].id == "add_gda"
    assert template.effects[0].parameters["amount"] == 5

def test_get_action_template_key_error():
    dm = DataManager()
    with pytest.raises(KeyError) as excinfo:
        dm.get_action_template("Invalido")
    assert "não foi encontrado" in str(excinfo.value)

def test_get_character_key_error():
    dm = DataManager()
    with pytest.raises(KeyError) as excinfo:
        dm.get_character("Invalido")
    assert "não foi encontrado" in str(excinfo.value)

def test_get_combat_style_key_error():
    dm = DataManager()
    with pytest.raises(KeyError, match="não foi encontrado"):
        dm.get_combat_style("Invalido")

def test_load_characters_success():
    dm = DataManager()
    dm.load_combat_styles('data/CombatStyles.json')
    dm.load_game_rules('data/Rules.json')
    dm.load_characters('data/Characters.json')
    
    char = dm.get_character("Destruidor")
    assert char.name == "Destruidor"
    assert char.weapon.name == "Espada Larga"
    assert char.armor.name == "Armadura Pesada"
    assert "BasicAttack" in char.active_abilities

def test_load_characters_missing_prereqs():
    dm = DataManager()
    with pytest.raises(KeyError, match="GameRules"):
        dm.load_characters("data/Characters.json")
    
    dm._game_rules = GameRules({}, {}, {}, 0, 0)
    with pytest.raises(KeyError, match="CombatStyles"):
        dm.load_characters("data/Characters.json")

def test_load_characters_invalid_style():
    dm = DataManager()
    dm._game_rules = GameRules({}, {}, {}, 0, 0)
    dm._combat_styles = {"Outro": None}
    
    bad_data = {"char_1": {"CombatStyle": "Guerreiro"}}
    with patch('builtins.open', mock_open()), patch('json.load', return_value=bad_data):
        with pytest.raises(KeyError, match="CombatStyle 'Guerreiro' não encontrado"):
            dm.load_characters('dummy.json')

def test_load_action_templates_invalid_action_type():
    dm = DataManager()
    bad_data = {"Act": {"nome": "N", "action_type": "invalido", "focus_cost": 0}}
    with patch('builtins.open', mock_open()), patch('json.load', return_value=bad_data):
        with pytest.raises(ValueError, match="Action type inválido"):
            dm.load_action_templates('dummy.json')

def test_load_action_templates_invalid_attack_type():
    dm = DataManager()
    bad_data = {"Act": {"nome": "N", "action_type": "standard_action", "attack_type": "invalido", "focus_cost": 0}}
    with patch('builtins.open', mock_open()), patch('json.load', return_value=bad_data):
        with pytest.raises(ValueError, match="Attack type inválido"):
            dm.load_action_templates('dummy.json')
