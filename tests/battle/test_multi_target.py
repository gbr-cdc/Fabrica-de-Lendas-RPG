import pytest
from unittest.mock import MagicMock, patch
from battle.BattleActions import AttackAction
from core.Events import AttackLoad
from core.Enums import AttackType, RollState

def test_attack_action_multi_target():
    # Setup actor
    actor = MagicMock()
    actor.name = "Attacker"
    actor.atk_die = 12
    actor.rank = 2
    actor.bda = 1
    actor.pda = 5
    actor.mda = 2
    actor.pre = 0
    actor.floating_focus = 10
    actor.current_hp = 10
    
    # Setup targets
    t1 = MagicMock()
    t1.name = "T1"
    t1.def_die = 8
    t1.rank = 1
    t1.bdd = 0
    t1.grd = 0
    t1.current_hp = 10
    
    t2 = MagicMock()
    t2.name = "T2"
    t2.def_die = 8
    t2.rank = 1
    t2.bdd = 0
    t2.grd = 0
    t2.current_hp = 10
    
    context = MagicMock()
    # 4 rolls needed for 2 targets
    r1 = MagicMock(); r1.final_roll = 10
    r2 = MagicMock(); r2.final_roll = 5
    r3 = MagicMock(); r3.final_roll = 10
    r4 = MagicMock(); r4.final_roll = 5
    context.dice_service.roll_dice.side_effect = [r1, r2, r3, r4]
    
    template = MagicMock()
    template.nome = "Multi"
    template.focus_cost = 0
    template.effects = []
    template.attack_type = AttackType.BASIC_ATTACK
    
    # Patch CharacterSystem where it is used in battle.BattleActions
    with patch("battle.BattleActions.CharacterSystem") as mock_sys:
        mock_sys.is_alive.return_value = True
        
        action = AttackAction(template, actor, [t1, t2], context)
        result = action.execute()
        
        # Verify both targets were attacked
        history_str = "\n".join(result.history)
        assert "atacar T1" in history_str
        assert "atacar T2" in history_str
        assert mock_sys.take_damage.call_count == 2

def test_attack_action_one_dead():
    actor = MagicMock()
    actor.name = "Attacker"
    actor.rank = 2
    actor.bda = 1
    actor.pda = 5
    actor.mda = 2
    actor.pre = 0
    actor.floating_focus = 10
    actor.current_hp = 10
    
    t_dead = MagicMock(name="DeadTarget")
    t_dead.char_id = "dead"
    
    t_alive = MagicMock(name="AliveTarget")
    t_alive.char_id = "alive"
    t_alive.def_die = 8
    t_alive.rank = 1
    t_alive.bdd = 0
    t_alive.grd = 0
    t_alive.current_hp = 10
    t_alive.name = "Alive"
    
    context = MagicMock()
    r1 = MagicMock(); r1.final_roll = 10
    r2 = MagicMock(); r2.final_roll = 5
    context.dice_service.roll_dice.side_effect = [r1, r2]
    
    template = MagicMock()
    template.nome = "Multi"
    template.focus_cost = 0
    template.effects = []
    template.attack_type = AttackType.BASIC_ATTACK
    
    with patch("battle.BattleActions.CharacterSystem") as mock_sys:
        # First call is_alive for t_dead -> False, Second for t_alive -> True
        mock_sys.is_alive.side_effect = [False, True]
        
        action = AttackAction(template, actor, [t_dead, t_alive], context)
        result = action.execute()
        
        history_str = "\n".join(result.history)
        assert "Alive" in history_str
        # Dead target should be skipped and not appear in history via attack_load
        assert "DeadTarget" not in history_str
        assert mock_sys.take_damage.call_count == 1
