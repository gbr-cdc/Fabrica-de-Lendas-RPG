from __future__ import annotations
from typing import Dict, Callable, TYPE_CHECKING
from core.Bases import BattleAction, IBattleContext
from core.Events import ActionLoad, AttackLoad
from core.Structs import AttackActionTemplate
from core.Enums import RollState, BattleActionType, AttackType
from core.CharacterSystem import CharacterSystem

if TYPE_CHECKING:
    from entities.Characters import Character

class AttackAction(BattleAction):
    """
    Uma ação genérica guiada por dados. Lê seus efeitos do AttackActionTemplate.
    """
    def __init__(self, template: 'AttackActionTemplate', actor: 'Character', target: 'Character', context: 'IBattleContext', attack_type: 'AttackType' = None):
        super().__init__(name=template.nome, actor=actor, target=target, context=context, action_type=template.action_type)
        self.template = template
        self.attack_type = attack_type if attack_type is not None else template.attack_type

    def can_execute(self) -> tuple[bool, str]:
        if not CharacterSystem.is_alive(self.target):
            return False, "O alvo já está derrotado!"
        if self.actor.floating_focus < self.template.focus_cost:
            return False, f"Foco insuficiente para usar {self.name}!"
        return True, ""

    def get_hooks(self) -> Dict[str, Callable]:
        hooks = {}
        for effect in self.template.effects:
            if effect.id == "add_gda":
                amount = effect.parameters.get("amount", 0)
                # O Python tem "late binding", por isso é seguro usar default args
                # ou a gente cria uma factory. Para simplificar e evitar o scope trap:
                def make_hook(amt):
                    def add_gda_hook(attack_load: 'AttackLoad'):
                        if attack_load.character.char_id == self.actor.char_id:
                            attack_load.gda += amt
                            attack_load.history.append(f"[{self.name}] adicionou +{amt} de GdA!")
                    return add_gda_hook
                hooks['on_damage_calculation'] = make_hook(amount)
        return hooks

    def execute(self) -> ActionLoad:
        CharacterSystem.spend_focus(self.actor, self.template.focus_cost)

        attack_load = AttackLoad(
            character=self.actor,
            target=self.target,
            battle_context=self.context,
            attack_type=self.attack_type,
            attack_state=RollState.NEUTRAL,
            defense_state=RollState.NEUTRAL,
            gda = 0,
            damage = 0
        )

        self.context.emit('on_roll_modify', attack_load)
        
        roll_result = self.context.dice_service.roll_dice(self.actor.atk_die, attack_load.attack_state)
        attack_load.history.append(f"{self.actor.name} rolou {roll_result.final_roll} para atacar!")
        mod_atk_roll = roll_result.final_roll + self.actor.rank + self.actor.bda
        attack_load.history.append(f"Total modificado ataque: {mod_atk_roll}")
        
        roll_result = self.context.dice_service.roll_dice(self.target.def_die, attack_load.defense_state)
        attack_load.history.append(f"{self.target.name} rolou {roll_result.final_roll} para defender!")
        mod_def_roll = roll_result.final_roll + self.target.rank + self.target.bdd
        attack_load.history.append(f"Total modificado defesa: {mod_def_roll}")
        
        attack_load.gda = mod_atk_roll - mod_def_roll
        attack_load.history.append(f"GdA base é {attack_load.gda}")
        
        self.context.emit('on_defense_reaction', attack_load)
        
        if attack_load.gda > (0 + self.target.grd - self.actor.pre):
            attack_load.hit = True
            attack_load.history.append("O ataque acertou!")
            self.context.emit('on_hit_check', attack_load)
            
            if attack_load.gda < 0:
                attack_load.gda = 0
                
            self.context.emit('on_gda_modify', attack_load)
            
            self.context.emit('on_damage_calculation', attack_load)
            final_gda = max(0, attack_load.gda)
            attack_load.damage = attack_load.damage + self.actor.pda + (self.actor.mda * final_gda)
            attack_load.history.append(f"Dano calculado: PDA {self.actor.pda} + (MDA {self.actor.mda} x GdA {final_gda}) = {attack_load.damage}") 
            
            self.context.emit('on_damage_taken', attack_load)
            CharacterSystem.take_damage(self.target, attack_load.damage)
        else:
            attack_load.history.append("O ataque foi completamente defendido!")
            self.context.emit('on_hit_check', attack_load)

        self.context.emit('on_attack_end', attack_load)
        
        if self.attack_type == AttackType.BASIC_ATTACK:
            CharacterSystem.generate_focus(self.actor)

        return attack_load

class GenerateManaAction(BattleAction):
    def __init__(self, actor: 'Character', target: 'Character', context: 'IBattleContext', action_type: 'BattleActionType' = BattleActionType.MOVE_ACTION):
        super().__init__(name="Gerar Mana", actor=actor, target=target, context=context, action_type=action_type)

    def can_execute(self) -> tuple[bool, str]:
        if self.actor.current_mp <= 0:
            return False, "Sua reserva diária de mana esgotou!"
        max_floating = self.actor.rules.limite_mana * self.actor.men
        if self.actor.floating_mp >= max_floating:
            return False, "Sua mana manifestada já está no limite!"
        return True, ""

    def get_hooks(self) -> Dict[str, Callable]:
        return {}

    def execute(self) -> ActionLoad:
        old_floating = self.actor.floating_mp
        new_floating = CharacterSystem.generate_mana(self.actor)
        generated = new_floating - old_floating
        return ActionLoad(character=self.actor, history=[f"{self.actor.name} canalizou sua energia e gerou {generated} de Mana!"])

class GenerateFocusAction(BattleAction):
    def __init__(self, actor: 'Character', target: 'Character', context: 'IBattleContext', action_type: 'BattleActionType' = BattleActionType.MOVE_ACTION):
        super().__init__(name="Gerar Foco", actor=actor, target=target, context=context, action_type=action_type)

    def can_execute(self) -> tuple[bool, str]:
        max_focus = self.actor.rules.limite_foco * self.actor.men
        if self.actor.floating_focus >= max_focus:
            return False, "Seu Foco já está no limite máximo!"
        return True, ""

    def get_hooks(self) -> Dict[str, Callable]:
        return {}

    def execute(self) -> ActionLoad:
        old_focus = self.actor.floating_focus
        new_focus = CharacterSystem.generate_focus(self.actor)
        generated = new_focus - old_focus
        return ActionLoad(character=self.actor, history=[f"{self.actor.name} respirou fundo e gerou {generated} de Foco!"])

registry = {
    "AttackAction": AttackAction,
    "GenerateMana": GenerateManaAction,
    "GenerateFocus": GenerateFocusAction,
}