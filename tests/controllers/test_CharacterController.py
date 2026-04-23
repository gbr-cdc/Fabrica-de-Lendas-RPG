import pytest
from unittest.mock import MagicMock, patch
from controllers.CharacterController import PvP1v1Controller

def test_pvp1v1_controller_no_target():
    ctrl = PvP1v1Controller()
    actor = MagicMock()
    context = MagicMock()
    # Context only returns the actor, no enemies
    context.get_characters.return_value = [actor]
    
    with pytest.raises(RuntimeError):
        ctrl.choose_action(actor, context)

def test_pvp1v1_controller_with_target_no_focus():
    ctrl = PvP1v1Controller()
    actor = MagicMock()
    actor.floating_focus = 0
    target = MagicMock()
    context = MagicMock()
    context.get_characters.return_value = [actor, target]
    
    # Setup mock templates
    basic_atk = MagicMock()
    skill_atk = MagicMock()
    skill_atk.focus_cost = 5
    
    def mock_get_template(name):
        if name == "BasicAttack":
            return basic_atk
        return skill_atk
    
    context.get_template.side_effect = mock_get_template
    
    with patch('battle.BattleActions.registry') as mock_registry:
        mock_action_class = MagicMock()
        mock_registry.__getitem__.return_value = mock_action_class
        
        ctrl.choose_action(actor, context)
        
        # It should have chosen BasicAttack because floating_focus (0) < cost (5)
        mock_registry.__getitem__.assert_called_with("AttackAction")
        mock_action_class.assert_called_with(basic_atk, actor, [target], context)

def test_pvp1v1_controller_with_target_with_focus():
    ctrl = PvP1v1Controller()
    actor = MagicMock()
    actor.floating_focus = 10
    target = MagicMock()
    context = MagicMock()
    context.get_characters.return_value = [actor, target]
    
    # Setup mock templates
    basic_atk = MagicMock()
    skill_atk = MagicMock()
    skill_atk.focus_cost = 5
    
    def mock_get_template(name):
        if name == "BasicAttack":
            return basic_atk
        return skill_atk
    
    context.get_template.side_effect = mock_get_template
    
    with patch('battle.BattleActions.registry') as mock_registry:
        mock_action_class = MagicMock()
        mock_registry.__getitem__.return_value = mock_action_class
        
        ctrl.choose_action(actor, context)
        
        # It should have chosen SkillN1 because floating_focus (10) >= cost (5)
        mock_registry.__getitem__.assert_called_with("AttackAction")
        mock_action_class.assert_called_with(skill_atk, actor, [target], context)

def test_pvp1v1_controller_with_action_load():
    ctrl = PvP1v1Controller()
    actor = MagicMock()
    target = MagicMock()
    context = MagicMock()
    context.get_characters.return_value = [actor, target]
    action_load = MagicMock() # Not None
    
    basic_atk = MagicMock()
    context.get_template.return_value = basic_atk
    
    with patch('battle.BattleActions.registry') as mock_registry:
        mock_action_class = MagicMock()
        mock_registry.__getitem__.return_value = mock_action_class
        ctrl.choose_action(actor, context, action_load)
        mock_action_class.assert_called_with(basic_atk, actor, [target], context)
