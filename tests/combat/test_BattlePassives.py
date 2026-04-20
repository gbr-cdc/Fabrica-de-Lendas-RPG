import pytest
from unittest.mock import MagicMock, patch
from combat.BattlePassives import ForçaBruta, Combo, GracaDoDuelista, MãosPesadas
from core.Events import AttackLoad

def test_forca_bruta():
    char = MagicMock()
    char.char_id = "c1"
    passive = ForçaBruta(char, MagicMock())
    hooks = passive.get_hooks()
    
    load = AttackLoad(character=char, target=MagicMock(), battle_context=MagicMock(), 
                      attack_type=MagicMock(), attack_state=MagicMock(), defense_state=MagicMock(), 
                      gda=4, damage=0)
    
    load.hit = True
    hooks["on_gda_modify"](load)
    assert load.gda == 8

@patch("combat.BattlePassives.Atordoado")
def test_combo(mock_atordoado):
    char = MagicMock()
    char.char_id = "c1"
    
    context = MagicMock()
    basic_atk = MagicMock()
    context.get_template.return_value = basic_atk
    
    passive = Combo(char, context)
    hooks = passive.get_hooks()
    
    load = AttackLoad(character=char, target=MagicMock(), battle_context=MagicMock(), 
                      attack_type=MagicMock(), attack_state=MagicMock(), defense_state=MagicMock(), 
                      gda=5, damage=0)
    load.hit = True
                      
    with patch("combat.BattlePassives.action_registry") as mock_registry:
        mock_action_class = MagicMock()
        mock_action_instance = MagicMock()
        mock_action_instance.execute_if_possible.return_value = MagicMock(success=True, history=["mocked"])
        mock_action_class.return_value = mock_action_instance
        mock_registry.__getitem__.return_value = mock_action_class
        
        # Stage 0 -> 1
        hooks["on_attack_end"](load)
        assert "[PASSIVA] Combo!" in load.history[0]
        
        # Stage 1 -> 2
        passive.stage = 1
        passive.hit = True
        hooks["on_attack_end"](load)
        
        # Stage > 1
        passive.stage = 2
        hooks["on_attack_end"](load)
        mock_atordoado.assert_called_once()

@patch("combat.BattlePassives.Atordoado")
def test_maos_pesadas(mock_atordoado):
    char = MagicMock()
    char.char_id = "c1"
    char.weapon.type.name = "GREAT_WEAPON"
    passive = MãosPesadas(char, MagicMock())
    hooks = passive.get_hooks()
    
    load = AttackLoad(character=char, target=MagicMock(), battle_context=MagicMock(), 
                      attack_type=MagicMock(), attack_state=MagicMock(), defense_state=MagicMock(), 
                      gda=4, damage=0)
    load.hit = True
    
    hooks["on_gda_modify"](load)
    # MãosPesadas checks if gda > 3 to apply Atordoado
    mock_atordoado.assert_called_once()
    assert "Mãos Pesadas" in load.history[0]

def test_graca_do_duelista_acerto():
    char = MagicMock()
    char.char_id = "c1"
    passive = GracaDoDuelista(char, MagicMock())
    hooks = passive.get_hooks()
    
    passive.dice_service.roll_dice.return_value = MagicMock(final_roll=5)
    
    load = AttackLoad(character=char, target=MagicMock(), battle_context=MagicMock(), 
                      attack_type=MagicMock(), attack_state=MagicMock(), defense_state=MagicMock(), 
                      gda=2, damage=0)
    
    hooks["on_gda_modify"](load)
    assert load.gda == 7
    assert "Graça do Duelista adicionou +5 de GdA!" in load.history[0]

@patch("core.CharacterSystem.CharacterSystem.spend_focus")
def test_graca_do_duelista_reacao(mock_spend_focus):
    char = MagicMock()
    char.char_id = "c1"
    char.grd = 2
    char.floating_focus = 3
    char.name = "Duelist"
    
    context = MagicMock()
    controller = MagicMock()
    controller.choose_reaction.return_value = True
    context.get_controller.return_value = controller
    
    passive = GracaDoDuelista(char, context)
    hooks = passive.get_hooks()
    
    passive.dice_service.roll_dice.return_value = MagicMock(final_roll=3)
    
    attacker = MagicMock()
    attacker.pre = 1
    
    load = AttackLoad(character=attacker, target=char, battle_context=context, 
                      attack_type=MagicMock(), attack_state=MagicMock(), defense_state=MagicMock(), 
                      gda=5, damage=0)
                      
    hooks["on_defensive_reaction"](load)
    
    # 5 > (0 + 2 - 1) => 5 > 1, so reaction triggers
    mock_spend_focus.assert_called_once_with(char, 2)
    assert load.gda == 2 # 5 - 3
    assert "usou Evasão!" in load.history[0]
