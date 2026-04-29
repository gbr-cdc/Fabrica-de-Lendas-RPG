import pytest
from battle.BattlePassives import ForçaBruta, Combo, GracaDoDuelista, MãosPesadas
from core.Events import AttackLoad
from tests.utils.entity_factory import create_dummy_character, create_dummy_weapon
from core.DiceManager import DiceManager
from core.Enums import WeaponType, BattleActionType
from unittest.mock import MagicMock, patch

def test_forca_bruta():
    char = create_dummy_character()
    passive = ForçaBruta(char, MagicMock())
    hooks = passive.get_hooks()
    
    load = AttackLoad(character=char, target=create_dummy_character(), battle_context=MagicMock(), 
                      attack_type=MagicMock(), attack_state=MagicMock(), defense_state=MagicMock(), 
                      gda=4, damage=0)
    
    load.hit = True
    hooks["on_gda_modify"](load)
    assert load.gda == 8

def test_maos_pesadas():
    char = create_dummy_character()
    weapon = create_dummy_weapon(weapon_type=WeaponType.GREAT_WEAPON)
    char.weapon = weapon
    
    passive = MãosPesadas(char, MagicMock())
    hooks = passive.get_hooks()
    
    target = create_dummy_character()
    load = AttackLoad(character=char, target=target, battle_context=MagicMock(), 
                      attack_type=MagicMock(), attack_state=MagicMock(), defense_state=MagicMock(), 
                      gda=4, damage=0)
    load.hit = True
    
    hooks["on_gda_modify"](load)
    # MãosPesadas checks if gda > 3 to apply Atordoado
    assert any(effect.__class__.__name__ == "Atordoado" for effect in target.status_effects)
    assert "Mãos Pesadas" in load.history[0]

def test_graca_do_duelista_acerto():
    char = create_dummy_character()
    dice = DiceManager(seed=42)
    dice.schedule_result(5)
    
    context = MagicMock()
    context.dice_service = dice
    
    passive = GracaDoDuelista(char, context)
    hooks = passive.get_hooks()
    
    load = AttackLoad(character=char, target=create_dummy_character(), battle_context=context, 
                      attack_type=MagicMock(), attack_state=MagicMock(), defense_state=MagicMock(), 
                      gda=2, damage=0)
    
    hooks["on_gda_modify"](load)
    assert load.gda == 7
    assert "Graça do Duelista adicionou +5 de GdA!" in load.history[0]

def test_graca_do_duelista_reacao():
    char = create_dummy_character(attributes=[10, 10, 10]) # Rank 2. GRD = 2.
    char.floating_focus = 10
    
    dice = DiceManager(seed=42)
    dice.schedule_result(3)
    
    context = MagicMock()
    context.dice_service = dice
    controller = MagicMock()
    controller.choose_reaction.return_value = True
    context.get_controller.return_value = controller
    
    passive = GracaDoDuelista(char, context)
    hooks = passive.get_hooks()
    
    attacker = create_dummy_character(attributes=[10, 10, 10]) # Rank 2. PRE = 2.
    
    load = AttackLoad(character=attacker, target=char, battle_context=context, 
                      attack_type=MagicMock(), attack_state=MagicMock(), defense_state=MagicMock(), 
                      gda=5, damage=0)
                      
    hooks["on_defensive_reaction"](load)
    
    # 5 > (0 + 2 - 2) => 5 > 0, so reaction triggers
    assert char.floating_focus == 8 # 10 - 2
    assert load.gda == 2 # 5 - 3
    assert "usou Evasão!" in load.history[0]

def test_combo_passive_logic():
    owner = create_dummy_character(char_id="owner")
    context = MagicMock()
    
    # Mock template for basic attack
    template = MagicMock()
    context.get_template.return_value = template
    
    combo = Combo(owner, context)
    hooks = combo.get_hooks()
    hook = hooks['on_attack_end']
    
    # 1. Trigger non-owner attack
    other_char = create_dummy_character(char_id="other")
    other_load = AttackLoad(character=other_char, target=create_dummy_character(), battle_context=MagicMock(), attack_type=MagicMock(), attack_state=MagicMock(), defense_state=MagicMock())
    hook(other_load)
    assert combo.stage == 0
    
    # 2. Stage 0 -> Stage 1 (hit)
    hit_load = AttackLoad(character=owner, target=create_dummy_character(), battle_context=MagicMock(), attack_type=MagicMock(), attack_state=MagicMock(), defense_state=MagicMock())
    hit_load.hit = True
    hit_load.history = []
    
    # Mock AttackAction execution
    action_mock = MagicMock()
    action_mock.execute_if_possible.return_value = MagicMock(success=True, history=["Combo Hit!"])
    
    from battle.BattlePassives import action_registry
    with patch.dict(action_registry, {"AttackAction": MagicMock(return_value=action_mock)}):
        hook(hit_load)
        
    assert "Combo!" in hit_load.history[0]
    
    # 3. Trigger Stage 1 fail
    combo.stage = 1
    combo.hit = True
    miss_load = AttackLoad(character=owner, target=create_dummy_character(), battle_context=MagicMock(), attack_type=MagicMock(), attack_state=MagicMock(), defense_state=MagicMock())
    miss_load.hit = False 
    hook(miss_load)
    assert combo.stage == 0



