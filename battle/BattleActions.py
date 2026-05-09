from __future__ import annotations
from typing import Dict, Callable, TYPE_CHECKING, List
from core.BaseClasses import BattleAction, IBattleContext
from core.Events import ActionLoad, AttackLoad, HistoryEmitter
from core.Structs import AttackActionTemplate
from core.Enums import RollState, BattleActionType, AttackType
from core.CharacterSystem import CharacterSystem
from core.Modifiers import EphemeralModifier

if TYPE_CHECKING:
    from entities.Characters import Character
    from core.Events import AttackLoad

def _build_add_gda(effect, action: 'AttackAction'):
    amount = effect.parameters.get("amount", 0)
    def add_gda_hook(attack_load: 'AttackLoad'):
        if attack_load.character.char_id == action.actor.char_id:
            attack_load.gda += amount
            attack_load.add_event("MOD", action.name, amount, attack_load.character.char_id)
    return {'on_damage_calculation': add_gda_hook}

def _build_swap_atk_def_die(effect, action: 'AttackAction'):
    def swap_die_hook(attack_load: 'AttackLoad'):
        if attack_load.character.char_id == action.actor.char_id:
            diff = action.actor.def_die - action.actor.atk_die
            mod = EphemeralModifier(stat_name="atk_die", value=diff, source=action.name)
            action.actor.add_modifier(mod)

    def cleanup_hook(attack_load: 'AttackLoad'):
        if attack_load.character.char_id == action.actor.char_id:
            action.actor.remove_modifiers_by_source(action.name)
            
    return {'on_roll_modify': swap_die_hook, 'on_attack_end': cleanup_hook}

def _build_set_gda_zero_on_dmg(effect, action: 'AttackAction'):
    def set_gda_zero_hook(attack_load: 'AttackLoad'):
        if attack_load.character.char_id == action.actor.char_id:
            attack_load.gda = 0
            attack_load.add_event("MOD", action.name, 0, attack_load.character.char_id)
    return {'on_damage_calculation': set_gda_zero_hook}

def _build_apply_status_on_hit_threshold(effect, action: 'AttackAction'):
    status_name = effect.parameters.get("status")
    threshold = effect.parameters.get("threshold", 0)
    duration = effect.parameters.get("duration", 1)
    
    def apply_status_hook(attack_load: 'AttackLoad'):
        if attack_load.character.char_id == action.actor.char_id and attack_load.hit:
            if attack_load.gda > threshold:
                if status_name == "Atordoado":
                    from battle.StatusEffects import Atordoado
                    effect = Atordoado(duration=duration, target=attack_load.target, context=action.context)
                    action.context.add_status_effect(effect)
                    attack_load.add_event("STATUS", attack_load.target.char_id, status_name, duration, "APPLIED")
    return {'on_hit_check': apply_status_hook}

EFFECT_HOOK_BUILDERS: Dict[str, Callable] = {
    "add_gda": _build_add_gda,
    "swap_atk_def_die": _build_swap_atk_def_die,
    "set_gda_zero_on_dmg": _build_set_gda_zero_on_dmg,
    "apply_status_on_hit_threshold": _build_apply_status_on_hit_threshold
}

class AttackAction(BattleAction):
    """
    Uma ação genérica guiada por dados. Lê seus efeitos do AttackActionTemplate.
    """
    def __init__(self, template: 'AttackActionTemplate', actor: 'Character', targets: List['Character'], context: 'IBattleContext', attack_type: 'AttackType' = None):
        super().__init__(name=template.nome, actor=actor, targets=targets, context=context, action_type=template.action_type)
        self.template = template
        self.attack_type = attack_type if attack_type is not None else template.attack_type

    def can_execute(self) -> tuple[bool, str]:
        if not self.targets:
            return False, "Nenhum alvo selecionado!"
        
        if all(not CharacterSystem.is_alive(t) for t in self.targets):
            return False, "Todos os alvos já estão derrotados!"

        if self.actor.floating_focus < self.template.focus_cost:
            return False, f"Foco insuficiente para usar {self.name}!"
        return True, ""

    def get_hooks(self) -> Dict[str, Callable]:
        hooks = {}
        for effect in self.template.effects:
            builder = EFFECT_HOOK_BUILDERS.get(effect.id)
            if builder:
                hooks.update(builder(effect, self))
        return hooks

    def execute(self) -> ActionLoad:
        CharacterSystem.spend_focus(self.actor, self.template.focus_cost)

        action_load = ActionLoad(character=self.actor)
        action_load.add_event("EXEC", self.template.id, self.actor.char_id)
        if self.template.focus_cost > 0:
            action_load.add_event("FOCUS", self.actor.char_id, -self.template.focus_cost, self.actor.floating_focus)

        master_attack_load = None
        master_roll_result = None
        mod_atk_roll = 0

        if self.attack_type == AttackType.AREA:
            # Master Roll Phase
            master_attack_load = AttackLoad(
                character=self.actor,
                target=None,
                battle_context=self.context,
                attack_type=self.attack_type,
                attack_state=RollState.NEUTRAL,
                defense_state=RollState.NEUTRAL,
                gda = 0,
                damage = 0
            )
            self.context.emit('on_roll_modify', master_attack_load)
            master_roll_result = self.context.dice_service.roll_dice(self.actor.atk_die, master_attack_load.attack_state)
            
            master_attack_load.add_event("ROLL", "ATK_AREA", master_roll_result.final_roll, self.actor.atk_die, self.actor.char_id)
            mod_atk_roll = master_roll_result.final_roll + self.actor.rank + self.actor.bda
            action_load.history.extend(master_attack_load.history)

        for target in self.targets:
            if not CharacterSystem.is_alive(target):
                continue

            attack_load = AttackLoad(
                character=self.actor,
                target=target,
                battle_context=self.context,
                attack_type=self.attack_type,
                attack_state=RollState.NEUTRAL,
                defense_state=RollState.NEUTRAL,
                gda = 0,
                damage = 0
            )

            if self.attack_type == AttackType.AREA:
                # Inherit state from master roll but for this specific target
                attack_load.attack_state = master_attack_load.attack_state
                current_mod_atk = mod_atk_roll
            else:
                self.context.emit('on_roll_modify', attack_load)
                roll_result = self.context.dice_service.roll_dice(self.actor.atk_die, attack_load.attack_state)
                current_mod_atk = roll_result.final_roll + self.actor.rank + self.actor.bda
                attack_load.add_event("ROLL", "ATK", roll_result.final_roll, self.actor.atk_die, self.actor.char_id)
            
            roll_result = self.context.dice_service.roll_dice(target.def_die, attack_load.defense_state)
            mod_def_roll = roll_result.final_roll + target.rank + target.bdd
            attack_load.add_event("ROLL", "DEF", roll_result.final_roll, target.def_die, target.char_id)
            
            attack_load.gda = current_mod_atk - mod_def_roll
            
            self.context.emit('on_defense_reaction', attack_load)
            
            if attack_load.gda > (0 + target.grd - self.actor.pre):
                attack_load.hit = True
                attack_load.add_event("HIT", target.char_id)
                self.context.emit('on_hit_check', attack_load)
                
                if attack_load.gda < 0:
                    attack_load.gda = 0
                    
                self.context.emit('on_gda_modify', attack_load)
                
                self.context.emit('on_damage_calculation', attack_load)
                final_gda = max(0, attack_load.gda)
                attack_load.damage = attack_load.damage + self.actor.pda + (self.actor.mda * final_gda)
                
                self.context.emit('on_damage_taken', attack_load)
                CharacterSystem.take_damage(target, attack_load.damage)
                attack_load.add_event("DMG", target.char_id, attack_load.damage, self.attack_type.value)
                attack_load.add_event("HP", target.char_id, -attack_load.damage, target.current_hp)
            else:
                attack_load.add_event("MISS", target.char_id)
                self.context.emit('on_hit_check', attack_load)

            self.context.emit('on_attack_end', attack_load)
            action_load.history.extend(attack_load.history)
        
        if self.attack_type == AttackType.BASIC_ATTACK:
            old_focus = self.actor.floating_focus
            new_focus = CharacterSystem.generate_focus(self.actor)
            action_load.add_event("FOCUS", self.actor.char_id, new_focus - old_focus, new_focus)

        return action_load

class GenerateManaAction(BattleAction):
    def __init__(self, actor: 'Character', targets: List['Character'], context: 'IBattleContext', action_type: 'BattleActionType' = BattleActionType.MOVE_ACTION):
        super().__init__(name="Gerar Mana", actor=actor, targets=targets, context=context, action_type=action_type)

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
        old_total = self.actor.current_mp
        old_floating = self.actor.floating_mp
        new_floating = CharacterSystem.generate_mana(self.actor)
        new_total = self.actor.current_mp
        
        load = ActionLoad(character=self.actor)
        load.add_event("MANA_T", self.actor.char_id, new_total - old_total, new_total)
        load.add_event("MANA_F", self.actor.char_id, new_floating - old_floating, new_floating)
        return load

class GenerateFocusAction(BattleAction):
    def __init__(self, actor: 'Character', targets: List['Character'], context: 'IBattleContext', action_type: 'BattleActionType' = BattleActionType.MOVE_ACTION):
        super().__init__(name="Gerar Foco", actor=actor, targets=targets, context=context, action_type=action_type)

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
        
        load = ActionLoad(character=self.actor)
        load.add_event("FOCUS", self.actor.char_id, new_focus - old_focus, new_focus)
        return load

class TogglePosturaDefensiva(BattleAction):
    def __init__(self, actor: 'Character', targets: List['Character'], context: 'IBattleContext'):
        super().__init__(name="Alternar Postura Defensiva", actor=actor, targets=targets, context=context, action_type=BattleActionType.FREE_ACTION)

    def execute(self) -> ActionLoad:
        # Pega a instância da passiva através do contexto
        passive = self.context.get_active_passive(self.actor.char_id, "Postura Defensiva")
        if passive and hasattr(passive, 'toggle'):
            msg = passive.toggle()
            return ActionLoad(character=self.actor, history=[msg])
        return ActionLoad(character=self.actor, history=["Falha ao alternar postura: passiva não encontrada."], success=False)
