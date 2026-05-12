from __future__ import annotations
from typing import Dict, Callable, TYPE_CHECKING, List
from core.BaseClasses import BattleAction, IActionContext
from core.Events import ActionLoad, AttackLoad, HistoryEmitter
from core.Structs import AttackActionTemplate
from core.Enums import RollState, BattleActionType, AttackType
from core.CharacterSystem import CharacterSystem
from core.Modifiers import EphemeralModifier

"""
This module defines the various battle actions available to characters during combat.
It follows the Command Pattern [ARCH.RULES.CORE.COMMAND], where each action is an object
encapsulating the logic needed to validate and execute a specific game behavior.
Actions interact with the battle engine via the IBattleContext and use the EventBus
to allow for reactive modifications [ARCH.RULES.CORE.OBSERVER].
"""


if TYPE_CHECKING:
    from entities.Characters import Character
    from core.Events import AttackLoad

# --- Hook Builders [ARCH.RULES.BATTLE.ATTACK_DATA] ---
# These functions create ephemeral hooks that modify the AttackAction resolution flow.
# They are mapped in EFFECT_HOOK_BUILDERS and triggered by AttackAction.get_hooks().

def _build_add_gda(effect, action: 'AttackAction'):
    """Increases the Hit Grade (GdA) by a fixed amount during damage calculation."""

    amount = effect.parameters.get("amount", 0)
    def add_gda_hook(attack_load: 'AttackLoad'):
        if attack_load.character.char_id == action.actor.char_id:
            attack_load.gda += amount
            attack_load.history.append(HistoryEmitter.action_hook(action.name, attack_load.character.char_id))
            attack_load.history.append(HistoryEmitter.atk_load("gda", amount, attack_load.gda))
    return {'on_damage_calculation': add_gda_hook}

def _build_swap_atk_def_die(effect, action: 'AttackAction'):
    """
    Temporarily swaps the character's attack die with their defense die
    by modifying the attack_load directly.
    """

    def swap_die_hook(attack_load: 'AttackLoad'):
        if attack_load.character.char_id == action.actor.char_id:
            attack_load.atk_die = action.actor.def_die
            attack_load.history.append(HistoryEmitter.action_hook(action.name, attack_load.character.char_id))
            attack_load.history.append(HistoryEmitter.atk_load("atk_die", 0, attack_load.atk_die))

    return {'on_roll_modify': swap_die_hook}

def _build_add_bda(effect, action: 'AttackAction'):
    """Increases the action-scoped attack bonus (BdA) by a fixed amount during roll modification."""

    amount = effect.parameters.get("amount", 0)
    def add_bda_hook(attack_load: 'AttackLoad'):
        if attack_load.character.char_id == action.actor.char_id:
            attack_load.bda += amount
            attack_load.history.append(HistoryEmitter.action_hook(action.name, attack_load.character.char_id))
            attack_load.history.append(HistoryEmitter.atk_load("bda", amount, attack_load.bda))
    return {'on_roll_modify': add_bda_hook}

def _build_set_gda_zero_on_dmg(effect, action: 'AttackAction'):
    """Forces GdA to 0 during damage calculation, usually for non-damaging utility hits."""

    def set_gda_zero_hook(attack_load: 'AttackLoad'):
        if attack_load.character.char_id == action.actor.char_id:
            attack_load.gda = 0
            attack_load.history.append(HistoryEmitter.action_hook(action.name, attack_load.character.char_id))
            attack_load.history.append(HistoryEmitter.atk_load("gda", 0, 0))
    return {'on_damage_calculation': set_gda_zero_hook}

def _build_apply_status_on_hit_threshold(effect, action: 'AttackAction'):
    """
    Applies a status effect to the target if the hit is successful and GdA exceeds a threshold.
    Validates hit success and GdA before adding the status to the battle context.
    """

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
                    attack_load.history.append(HistoryEmitter.action_hook(action.name, attack_load.character.char_id))
                    attack_load.history.append(HistoryEmitter.status(attack_load.target.char_id, status_name, duration, "APPLIED"))
    return {'on_hit_check': apply_status_hook}

# Registry mapping template effect IDs to their corresponding hook builder functions.
EFFECT_HOOK_BUILDERS: Dict[str, Callable] = {

    "add_bda": _build_add_bda,
    "add_gda": _build_add_gda,
    "swap_atk_def_die": _build_swap_atk_def_die,
    "set_gda_zero_on_dmg": _build_set_gda_zero_on_dmg,
    "apply_status_on_hit_threshold": _build_apply_status_on_hit_threshold
}

class AttackAction(BattleAction):
    """
    A generic, data-driven attack action [ARCH.RULES.CORE.DATA].
    Logic is driven by an AttackActionTemplate, which defines focus costs, attack types,
    and special effects that are injected into the attack resolution via hooks.
    Supports Area of Effect (AoE) logic [ARCH.RULES.BATTLE.AREA_ATTACK].
    """
    def __init__(self, template: 'AttackActionTemplate' | None, actor: 'Character', targets: List['Character'], context: 'IActionContext', attack_type: 'AttackType' = None):
        if template is None:
            template = AttackActionTemplate(nome="Ataque Básico", action_type=BattleActionType.STANDARD_ACTION, attack_type=AttackType.BASIC_ATTACK, focus_cost=0, effects=[])
        super().__init__(name=template.nome, actor=actor, targets=targets, context=context, action_type=template.action_type)
        self.template = template
        self.attack_type = attack_type if attack_type is not None else template.attack_type

    def can_execute(self) -> tuple[bool, str]:
        """
        Validates if the action can be performed.
        Checks for target existence/vitality and focus resource availability.
        """

        if not self.targets:
            return False, "Nenhum alvo selecionado!"
        
        if all(not CharacterSystem.is_alive(t) for t in self.targets):
            return False, "Todos os alvos já estão derrotados!"

        if self.actor.floating_focus < self.template.focus_cost:
            return False, f"Foco insuficiente para usar {self.name}!"
        return True, ""

    def get_hooks(self) -> Dict[str, Callable]:
        """
        Retrieves ephemeral hooks defined in the action template [ARCH.RULES.BATTLE.ATTACK_DATA].
        These hooks will be registered for the duration of this specific action execution.
        """

        hooks = {}
        for effect in self.template.effects:
            builder = EFFECT_HOOK_BUILDERS.get(effect.id)
            if builder:
                hooks.update(builder(effect, self))
        return hooks

    def execute(self) -> ActionLoad:
        """
        Resolves the attack according to the Combat Flow [GDD.COMBAT.FLOW].
        Handles Master Rolls for Area attacks and individual resolution for each target.
        """
        # --- Resource Consumption ---

        action_load = ActionLoad(character=self.actor)
        action_load.history.append(HistoryEmitter.exec(self.template.nome, self.actor.char_id))
        if self.template.focus_cost > 0:
            CharacterSystem.spend_focus(self.actor, self.template.focus_cost)
            action_load.history.append(HistoryEmitter.focus(self.actor.char_id, -self.template.focus_cost, self.actor.floating_focus))

        master_attack_load = None
        master_roll_result = None
        mod_atk_roll = 0

        # --- Phase 1: Attack Roll ---
        if self.attack_type == AttackType.AREA:
            # AoE Logic [ARCH.RULES.BATTLE.AREA_ATTACK]: One roll for all targets.
            # Only target-agnostic passives influence this roll.
            master_attack_load = AttackLoad(
                character=self.actor,
                target=None,
                attack_type=self.attack_type,
                attack_state=RollState.NEUTRAL,
                defense_state=RollState.NEUTRAL,
                gda = 0,
                damage = 0,
                bda=self.actor.bda,
                pre=self.actor.pre,
                atk_die=self.actor.atk_die,
                def_die=0
            )
            self.context.emit('on_roll_modify', master_attack_load)
            master_roll_result = self.context.dice_service.roll_dice(master_attack_load.atk_die, master_attack_load.attack_state)
            master_attack_load.attack_roll = master_roll_result.final_roll
            
            master_attack_load.history.append(HistoryEmitter.roll("ATK_AREA", master_roll_result.final_roll, master_attack_load.atk_die, self.actor.char_id))
            mod_atk_roll = master_roll_result.final_roll + self.actor.rank + master_attack_load.bda
            action_load.history.extend(master_attack_load.history)

        # --- Phase 2: Target Resolution ---
        for target in self.targets:

            if not CharacterSystem.is_alive(target):
                continue

            attack_load = AttackLoad(
                character=self.actor,
                target=target,
                attack_type=self.attack_type,
                attack_state=RollState.NEUTRAL,
                defense_state=RollState.NEUTRAL,
                gda = 0,
                damage = 0,
                bda=self.actor.bda,
                pre=self.actor.pre,
                bdd=target.bdd,
                grd=target.grd,
                atk_die=self.actor.atk_die,
                def_die=target.def_die
            )

            if self.attack_type == AttackType.AREA:
                # Area Resolution: Use the Master Roll result for every target.
                attack_load.attack_state = master_attack_load.attack_state
                attack_load.attack_roll = master_roll_result.final_roll
                attack_load.bda = master_attack_load.bda
                attack_load.pre = master_attack_load.pre
                attack_load.atk_die = master_attack_load.atk_die
                current_mod_atk = attack_load.attack_roll + self.actor.rank + attack_load.bda
                self.context.emit('on_roll_modify', attack_load)
            else:
                # Single Target Resolution: Roll for this specific attack instance.
                self.context.emit('on_roll_modify', attack_load)
                roll_result = self.context.dice_service.roll_dice(attack_load.atk_die, attack_load.attack_state)
                attack_load.attack_roll = roll_result.final_roll
                current_mod_atk = roll_result.final_roll + self.actor.rank + attack_load.bda
                attack_load.history.append(HistoryEmitter.roll("ATK", roll_result.final_roll, attack_load.atk_die, self.actor.char_id))
            
            # --- Phase 3: Defense Roll ---

            
            roll_result = self.context.dice_service.roll_dice(attack_load.def_die, attack_load.defense_state)
            attack_load.defense_roll = roll_result.final_roll
            mod_def_roll = roll_result.final_roll + target.rank + attack_load.bdd
            attack_load.history.append(HistoryEmitter.roll("DEF", roll_result.final_roll, attack_load.def_die, target.char_id))
            
            # --- Phase 4: Hit Calculation [GDD.COMBAT.FLOW.HIT] ---
            attack_load.gda = current_mod_atk - mod_def_roll

            
            self.context.emit('on_defense_reaction', attack_load)
            
            if attack_load.gda > (0 + attack_load.grd - attack_load.pre):
                attack_load.hit = True
                attack_load.history.append(HistoryEmitter.hit(target.char_id))
                self.context.emit('on_hit_check', attack_load)
                
                if attack_load.gda < 0:
                    attack_load.gda = 0
                    
                self.context.emit('on_gda_modify', attack_load)
                
                self.context.emit('on_damage_calculation', attack_load)
                final_gda = max(0, attack_load.gda)
                attack_load.damage = attack_load.damage + self.actor.pda + (self.actor.mda * final_gda)
                attack_load.damage = max(0, attack_load.damage)
                
                self.context.emit('on_damage_taken', attack_load)
                CharacterSystem.take_damage(target, attack_load.damage)
                attack_load.history.append(HistoryEmitter.dmg(target.char_id, attack_load.damage, self.attack_type.value))
                attack_load.history.append(HistoryEmitter.hp(target.char_id, -attack_load.damage, target.current_hp))
            else:
                # Attack missed: GdA + Pre - Grd <= 0
                attack_load.history.append(HistoryEmitter.miss(target.char_id))
                self.context.emit('on_hit_check', attack_load)


            self.context.emit('on_attack_end', attack_load)
            action_load.history.extend(attack_load.history)
        
        if self.attack_type == AttackType.BASIC_ATTACK:
            old_focus = self.actor.floating_focus
            new_focus = CharacterSystem.generate_focus(self.actor)
            action_load.history.append(HistoryEmitter.focus(self.actor.char_id, new_focus - old_focus, new_focus))

        return action_load

class GenerateManaAction(BattleAction):
    """
    Standard Move Action to convert daily Mana into Floating MP.
    Limited by the character's manifest limit (MEN * rules.limite_mana).
    """
    def __init__(self, actor: 'Character', targets: List['Character'], context: 'IActionContext', action_type: 'BattleActionType' = BattleActionType.MOVE_ACTION):

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
        load.history.append(HistoryEmitter.mana_t(self.actor.char_id, new_total - old_total, new_total))
        load.history.append(HistoryEmitter.mana_f(self.actor.char_id, new_floating - old_floating, new_floating))
        return load

class GenerateFocusAction(BattleAction):
    """
    Standard Move Action to generate Focus for the character.
    Limited by the character's focus limit (MEN * rules.limite_foco).
    Used to pay for Skills/Attacks.
    """
    def __init__(self, actor: 'Character', targets: List['Character'], context: 'IActionContext', action_type: 'BattleActionType' = BattleActionType.MOVE_ACTION):

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
        load.history.append(HistoryEmitter.focus(self.actor.char_id, new_focus - old_focus, new_focus))
        return load

class TogglePosturaDefensiva(BattleAction):
    """
    A Free Action that toggles the state of the 'Postura Defensiva' passive.
    It retrieves the active passive from the context and calls its toggle method.
    """
    def __init__(self, actor: 'Character', targets: List['Character'], context: 'IActionContext'):

        super().__init__(name="Alternar Postura Defensiva", actor=actor, targets=targets, context=context, action_type=BattleActionType.FREE_ACTION)

    def execute(self) -> ActionLoad:
        # Pega a instância da passiva através do contexto
        passive = self.context.get_active_passive(self.actor.char_id, "Postura Defensiva")
        if passive and hasattr(passive, 'toggle'):
            msg = passive.toggle()
            return ActionLoad(character=self.actor, history=[msg])
        return ActionLoad(character=self.actor, history=["Falha ao alternar postura: passiva não encontrada."], success=False)

class MudarPosturaBatalha(BattleAction):
    """
    A Free Action that toggles the state of the 'Postura de Batalha' passive.
    It retrieves the active passive from the context and calls its set_mode method.
    """
    def __init__(self, actor: 'Character', targets: List['Character'], context: 'IActionContext'):
        super().__init__(name="Mudar Postura de Batalha", actor=actor, targets=targets, context=context, action_type=BattleActionType.FREE_ACTION)

    def execute(self) -> ActionLoad:
        passive = self.context.get_active_passive(self.actor.char_id, "Postura de Batalha")
        if passive and hasattr(passive, 'set_mode'):
            # Logic: None -> OFFENSIVE -> DEFENSIVE -> None
            current = passive.current_postura
            next_mode = None
            if current is None:
                next_mode = "OFFENSIVE"
            elif current == "OFFENSIVE":
                next_mode = "DEFENSIVE"
            else:
                next_mode = None
                
            action_load = ActionLoad(character=self.actor)
            passive.set_mode(next_mode, action_load)
            return action_load
        return ActionLoad(character=self.actor, history=["Falha ao alternar postura: passiva não encontrada."], success=False)
