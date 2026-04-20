import pytest
import json
from unittest.mock import patch, mock_open
from core.DataManager import DataManager
from core.Structs import CombatStyle, GameRules, AttackActionTemplate
from core.Enums import AttributeType, ArmorType, WeaponType, BattleActionType, AttackType

@pytest.fixture
def dummy_combat_styles_json():
    return {
        "Guerreiro": {
            "name": "Guerreiro",
            "atq_die": 20,
            "def_die": 20,
            "main_stat": "FIS",
            "armor_type": "heavy",
            "weapon_type": "great_weapon"
        }
    }

@pytest.fixture
def dummy_game_rules_json():
    return {
        "regras_progressao": {
            "tabela_hp": {"10": 50},
            "tabela_mp": {"10": 20},
            "tabela_custos": {"10": 1}
        },
        "limite_foco": 3,
        "limite_mana": 2
    }

@pytest.fixture
def dummy_attack_actions_json():
    return {
        "BasicAttack": {
            "nome": "Ataque Basico",
            "action_type": "standard_action",
            "attack_type": "basic_attack",
            "focus_cost": 0,
            "effects": [
                {
                    "id": "add_gda",
                    "parameters": {"amount": 2}
                }
            ]
        }
    }

@pytest.fixture
def dummy_characters_json():
    return {
        "char_01": {
            "Nome": "Arthur",
            "CombatStyle": "Guerreiro",
            "controller": "1v1Controller",
            "FIS": 10,
            "HAB": 10,
            "MEN": 10,
            "Weapon": {
                "name": "Sword",
                "db": 2,
                "mda": 0,
                "type": "great_weapon"
            },
            "Armor": {
                "name": "Chainmail",
                "hp_bonus": 10,
                "type": "heavy"
            },
            "Abilities": ["BasicAttack"],
            "Passives": ["ForçaBruta"]
        }
    }

def test_load_combat_styles(dummy_combat_styles_json):
    dm = DataManager()
    with patch('builtins.open', mock_open()), patch('json.load', return_value=dummy_combat_styles_json):
        dm.load_combat_styles('dummy.json')
        
    style = dm.get_combat_style("Guerreiro")
    assert style.name == "Guerreiro"
    assert style.main_stat == AttributeType.FIS
    assert style.armor_type == ArmorType.HEAVY

def test_load_game_rules(dummy_game_rules_json):
    dm = DataManager()
    with patch('builtins.open', mock_open()), patch('json.load', return_value=dummy_game_rules_json):
        dm.load_game_rules('dummy.json')
        
    assert dm._game_rules.limite_foco == 3
    assert dm._game_rules.hp_table == {"10": 50}

def test_load_action_templates(dummy_attack_actions_json):
    dm = DataManager()
    with patch('builtins.open', mock_open()), patch('json.load', return_value=dummy_attack_actions_json):
        dm.load_action_templates('dummy.json')
        
    template = dm.get_action_template("BasicAttack")
    assert template.nome == "Ataque Basico"
    assert template.action_type == BattleActionType.STANDARD_ACTION
    assert template.attack_type == AttackType.BASIC_ATTACK
    assert len(template.effects) == 1
    assert template.effects[0].id == "add_gda"
    assert template.effects[0].parameters["amount"] == 2

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

def test_load_characters_success(dummy_combat_styles_json, dummy_game_rules_json, dummy_characters_json):
    dm = DataManager()
    with patch('builtins.open', mock_open()), patch('json.load', return_value=dummy_combat_styles_json):
        dm.load_combat_styles('dummy.json')
    with patch('builtins.open', mock_open()), patch('json.load', return_value=dummy_game_rules_json):
        dm.load_game_rules('dummy.json')
    with patch('builtins.open', mock_open()), patch('json.load', return_value=dummy_characters_json):
        dm.load_characters('dummy.json')
    
    char = dm.get_character("char_01")
    assert char.name == "Arthur"
    assert char.weapon.name == "Sword"
    assert char.armor.name == "Chainmail"
    assert "BasicAttack" in char.active_abilities

def test_load_characters_missing_prereqs():
    dm = DataManager()
    with pytest.raises(KeyError, match="GameRules"):
        dm.load_characters("dummy.json")
    
    dm._game_rules = GameRules([], [], [], 0, 0)
    with pytest.raises(KeyError, match="CombatStyles"):
        dm.load_characters("dummy.json")

def test_load_characters_invalid_style():
    dm = DataManager()
    dm._game_rules = GameRules([], [], [], 0, 0)
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
