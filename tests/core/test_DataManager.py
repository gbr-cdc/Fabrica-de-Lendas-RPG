import pytest
import json
from unittest.mock import patch, mock_open
from core.DataManager import DataManager
from core.Structs import CombatStyle, GameRules, AttackActionTemplate
from core.Enums import AttributeType, ArmorType, WeaponType, BattleActionType, AttackType
from tests.utils.json_integrity_checker import get_json_keys

def test_load_combat_styles():
    dm = DataManager()
    dm.load_combat_styles('data/CombatStyles.json')
    
    assert len(dm._combat_styles) > 0
    
    keys = get_json_keys('data/CombatStyles.json')
    for key in keys:
        style = dm.get_combat_style(key)
        assert isinstance(style, CombatStyle)
        assert isinstance(style.name, str)
        assert isinstance(style.main_stat, AttributeType)
        assert isinstance(style.armor_type, ArmorType)
        assert isinstance(style.weapon_type, WeaponType)

def test_load_game_rules():
    dm = DataManager()
    dm.load_game_rules('data/Rules.json')
    
    rules = dm._game_rules
    assert isinstance(rules, GameRules)
    assert isinstance(rules.limite_foco, int)
    assert isinstance(rules.hp_table, dict)
    assert len(rules.hp_table) > 0

def test_load_action_templates():
    dm = DataManager()
    dm.load_action_templates('data/AttackActions.json')
    
    assert len(dm._action_templates) > 0
    
    keys = get_json_keys('data/AttackActions.json')
    for key in keys:
        template = dm.get_action_template(key)
        assert isinstance(template, AttackActionTemplate)
        assert isinstance(template.action_type, BattleActionType)
        assert isinstance(template.attack_type, AttackType)
        assert isinstance(template.effects, list)

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
    
    assert len(dm._characters) > 0
    
    keys = get_json_keys('data/Characters.json')
    for key in keys:
        char = dm.get_character(key)
        assert char.char_id == key
        assert isinstance(char.name, str)
        assert char.combat_style is not None
        assert isinstance(char.combat_style, CombatStyle)
        assert char.weapon is not None
        assert isinstance(char.weapon.type, WeaponType)
        assert char.armor is not None
        assert isinstance(char.armor.type, ArmorType)
        assert isinstance(char.active_abilities, list)
        assert isinstance(char.passive_abilities, list)

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
