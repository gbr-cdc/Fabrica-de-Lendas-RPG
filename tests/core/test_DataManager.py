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
            "tabela_hp": [10, 20],
            "tabela_mp": [5, 10],
            "tabela_custos": [1]
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
    assert dm._game_rules.hp_table == [10, 20]

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
