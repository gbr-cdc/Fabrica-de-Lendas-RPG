from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable
    from core.BaseClasses import IPassiveContext, ActionLoad
    from core.Events import AttackLoad
    from entities.Characters import Character
    from core.Structs import BattlePassiveTemplate

from core.Enums import RollState, AttackType
from core.Events import HistoryEmitter
from core.BaseClasses import BattlePassive
from core.CharacterSystem import CharacterSystem
from battle.StatusEffects import Atordoado
from battle.BattleActions import AttackAction

class ForçaBruta(BattlePassive):
    def __init__(self, owner: Character, context: IPassiveContext, template: BattlePassiveTemplate | None = None):
        super().__init__(name="Força Bruta", owner=owner, context=context, template=template)

    def get_hooks(self) -> dict[str, Callable]:
        def multiply_hook(attack_load: AttackLoad):
            if attack_load.character.char_id == self.owner.char_id:
                params = self.template.parameters if self.template else {}
                multiplier = params.get("multiplier", 2)
                
                val = attack_load.gda
                # If multiplier is 2, it adds val. If 3, adds 2*val, etc.
                added_val = int(val * (multiplier - 1))
                
                attack_load.gda += added_val
                attack_load.history.append(HistoryEmitter.passive(self.name, self.owner.char_id))
                attack_load.history.append(HistoryEmitter.atk_load("gda", added_val, attack_load.gda))
        return {'on_gda_modify': multiply_hook}

class MãosPesadas(BattlePassive):
    def __init__(self, owner: Character, context: IPassiveContext, template: BattlePassiveTemplate | None = None):
        super().__init__(name="Mãos Pesadas", owner=owner, context=context, template=template)

    def get_hooks(self) -> dict[str, Callable]:
        def effect_hook(attack_load: AttackLoad):
            if attack_load.target is None:
                return
            if attack_load.character.char_id == self.owner.char_id:
                params = self.template.parameters if self.template else {}
                threshold = params.get("threshold", 3)
                duration = params.get("status_duration", 0)
                
                if attack_load.gda > threshold:
                    effect = Atordoado(duration=duration, target=attack_load.target, context=self.context)
                    self.context.add_status_effect(effect)
                    attack_load.history.append(HistoryEmitter.passive(self.name, self.owner.char_id))
                    attack_load.history.append(HistoryEmitter.status(attack_load.target.char_id, "Atordoado", duration, "APPLIED"))
        return {'on_gda_modify': effect_hook}

class PosturaDefensiva(BattlePassive):
    def __init__(self, owner: Character, context: IPassiveContext, template: BattlePassiveTemplate | None = None):
        super().__init__(name="Postura Defensiva", owner=owner, context=context, template=template)
        self.is_active = False
        self._dice_modifiers = []
        self._tracked_targets: dict[str, bool] = {}  # char_id -> penalty_applied

    def toggle(self) -> str:
        from core.Modifiers import EphemeralModifier
        self.is_active = not self.is_active
        if self.is_active:
            params = self.template.parameters if self.template else {}
            atk_penalty = params.get("atk_die_penalty", -2)
            def_bonus = params.get("def_die_bonus", 2)
            
            # Atacante d12 -> d10 (-2), Defensor d8 -> d10 (+2)
            m1 = EphemeralModifier(stat_name='atk_die', value=atk_penalty, source='PosturaDefensiva')
            m2 = EphemeralModifier(stat_name='def_die', value=def_bonus, source='PosturaDefensiva')
            self._dice_modifiers = [m1, m2]
            self.owner.add_modifier(m1)
            self.owner.add_modifier(m2)
            return f"POSTURA|{self.owner.char_id}|ON"
        else:
            for mod in self._dice_modifiers:
                self.owner.remove_modifier(mod)
            self._dice_modifiers = []
            self._clear_tracking()
            return f"POSTURA|{self.owner.char_id}|OFF"

    def _start_tracking(self, target: Character):
        if target.char_id not in self._tracked_targets:
            self._tracked_targets[target.char_id] = False

    def _clear_tracking(self, char_id: str | None = None):
        if char_id:
            if char_id in self._tracked_targets:
                del self._tracked_targets[char_id]
        else:
            self._tracked_targets.clear()

    def get_hooks(self) -> dict[str, Callable]:
        from core.Modifiers import EphemeralModifier
        
        def hit_hook(attack_load: AttackLoad):
            if self.is_active and attack_load.character.char_id == self.owner.char_id and attack_load.hit:
                self._start_tracking(attack_load.target)
                attack_load.history.append(HistoryEmitter.passive(self.name, self.owner.char_id))
                attack_load.add_event("POSTURA", self.owner.char_id, "OBSERVE", attack_load.target.char_id)

        def penalty_hook(attack_load: AttackLoad):
            cid = attack_load.character.char_id
            if self.is_active and cid in self._tracked_targets and attack_load.target is not None and attack_load.target.char_id == self.owner.char_id:
                params = self.template.parameters if self.template else {}
                pre_penalty = params.get("pre_penalty", -1)
                
                attack_load.pre += pre_penalty
                self._tracked_targets[cid] = True
                attack_load.history.append(HistoryEmitter.passive(self.name, self.owner.char_id))
                attack_load.history.append(HistoryEmitter.atk_load("pre", pre_penalty, attack_load.pre))

        def cleanup_hook(attack_load: AttackLoad):
            cid = attack_load.character.char_id
            if cid in self._tracked_targets:
                if self._tracked_targets[cid]:
                    self._clear_tracking(cid)

        def turn_end_hook(action_load: ActionLoad):
            cid = action_load.character.char_id
            if cid in self._tracked_targets:
                if not self._tracked_targets[cid]:
                    self._clear_tracking(cid)

        return {
            'on_gda_modify': hit_hook,
            'on_roll_modify': penalty_hook,
            'on_attack_end': cleanup_hook,
            'on_turn_end': turn_end_hook
        }

class GracaDoDuelista(BattlePassive):
    def __init__(self, owner: Character, context: IPassiveContext, template: BattlePassiveTemplate | None = None):
        super().__init__(name="Graça do Duelista", owner=owner, context=context, template=template)

    def get_hooks(self) -> dict[str, Callable]:
        params = self.template.parameters if self.template else {}
        bonus_die = params.get("bonus_die", 6)
        reaction_die = params.get("reaction_die", 4)
        reaction_cost = params.get("reaction_cost", 2)
        
        def passiva_acerto_hook(attack_load: AttackLoad) -> None: 
            if attack_load.character.char_id == self.owner.char_id:
                roll = self.dice_service.roll_dice(bonus_die, RollState.NEUTRAL)
                attack_load.gda += roll.final_roll
                attack_load.history.append(HistoryEmitter.passive(self.name, self.owner.char_id))
                attack_load.history.append(HistoryEmitter.atk_load("gda", roll.final_roll, attack_load.gda))

        def reacao_evasao_hook(attack_load: AttackLoad) -> None:
            if attack_load.target is None:
                return
            if attack_load.target.char_id == self.owner.char_id:
                # on_defense_reaction only fires on a confirmed hit; no GdA check needed.
                if self.owner.floating_focus >= reaction_cost:
                    controller = self.context.get_controller(self.owner.char_id)
                    if controller and controller.choose_reaction(self.owner, self.name, attack_load, self.context):
                        if CharacterSystem.spend_focus(self.owner, reaction_cost):
                            attack_load.history.append(HistoryEmitter.focus(self.owner.char_id, -reaction_cost, self.owner.floating_focus))
                        
                        roll = self.dice_service.roll_dice(reaction_die, RollState.NEUTRAL)
                        attack_load.gda -= roll.final_roll
                        attack_load.history.append(HistoryEmitter.passive(self.name, self.owner.char_id))
                        attack_load.history.append(HistoryEmitter.atk_load("gda", -roll.final_roll, attack_load.gda))

        return {
            "on_gda_modify": passiva_acerto_hook,
            "on_defense_reaction": reacao_evasao_hook
        }

class Combo(BattlePassive):
    def __init__(self, owner: Character, context: IPassiveContext, template: BattlePassiveTemplate | None = None):
        super().__init__(name="Combo", owner=owner, context=context, template=template)
        self.stage = 0
        self.hit = False
    
    def get_hooks(self) -> dict[str, Callable]:
        def checar_ataque_bonus(attack_load: AttackLoad):
            if attack_load.target is None:
                return
            if attack_load.character.char_id != self.owner.char_id:
                return

            if self.stage == 0:
                self.stage += 1
                if attack_load.hit:
                    self.hit = True

                response = AttackAction(None, attack_load.character, [attack_load.target], self.context, attack_type=AttackType.EXTRA_ATTACK).execute_if_possible()

                self.stage = 0
                self.hit = False
                
                if response.success:
                    attack_load.history.append(HistoryEmitter.passive(self.name, self.owner.char_id))
                    attack_load.add_event("COMBO", self.owner.char_id, 1)
                    attack_load.history.extend(response.history)

            elif self.stage == 1:
                if not self.hit or not attack_load.hit:
                    self.hit = False
                    self.stage = 0
                    return
                
                self.stage += 1
                response = AttackAction(None, attack_load.character, [attack_load.target], self.context, attack_type=AttackType.EXTRA_ATTACK).execute_if_possible()
                
                if response.success:
                    attack_load.history.append(HistoryEmitter.passive(self.name, self.owner.char_id))
                    attack_load.add_event("COMBO", self.owner.char_id, 2)
                    attack_load.history.extend(response.history)
                else:
                    self.stage = 0
                    self.hit = False

            elif self.stage > 1:
                if attack_load.hit:
                    effect = Atordoado(0, attack_load.target, self.context)
                    self.context.add_status_effect(effect)
                    attack_load.history.append(HistoryEmitter.passive(self.name, self.owner.char_id))
                    attack_load.history.append(HistoryEmitter.status(attack_load.target.char_id, "Atordoado", 0, "APPLIED"))
                    attack_load.add_event("COMBO", self.owner.char_id, self.stage, "FINAL")
        
        return {'on_attack_end': checar_ataque_bonus}

class Bloquear(BattlePassive):
    def __init__(self, owner: Character, context: IPassiveContext, template: BattlePassiveTemplate | None = None):
        super().__init__(name="Bloquear", owner=owner, context=context, template=template)
        self._counter_targets: dict[str, bool] = {}

    def get_hooks(self) -> dict[str, Callable]:
        params = self.template.parameters if self.template else {}
        focus_cost = params.get("focus_cost", 2)
        reduction_die = params.get("reduction_die", 4)
        counter_threshold = params.get("counter_threshold", -3)
        counter_bda_bonus = params.get("counter_bda_bonus", 1)

        def reacao_bloqueio_hook(attack_load: AttackLoad):
            if attack_load.target is None or attack_load.target.char_id != self.owner.char_id:
                return
            
            if self.owner.floating_focus >= focus_cost:
                controller = self.context.get_controller(self.owner.char_id)
                if controller.choose_reaction(self.owner, "Bloquear", attack_load, self.context):
                    if CharacterSystem.spend_focus(self.owner, focus_cost):
                        attack_load.history.append(HistoryEmitter.focus(self.owner.char_id, -focus_cost, self.owner.floating_focus))
                        
                        roll = self.dice_service.roll_dice(reduction_die, RollState.NEUTRAL)
                        bonus = roll.final_roll
                        attack_load.defense_roll += bonus
                        attack_load.gda -= bonus
                        attack_load.history.append(HistoryEmitter.passive(self.name, self.owner.char_id))
                        attack_load.history.append(HistoryEmitter.atk_load("defense_roll", bonus, attack_load.defense_roll))
                        attack_load.history.append(HistoryEmitter.atk_load("gda", -bonus, attack_load.gda))
        
        def bloqueio_ofensivo_hook(attack_load: AttackLoad):
            if attack_load.target is None or attack_load.target.char_id != self.owner.char_id:
                return
            if attack_load.gda <= counter_threshold:
                self._counter_targets[attack_load.character.char_id] = True

        def bonus_contra_ataque_hook(attack_load: AttackLoad):
            if attack_load.character.char_id == self.owner.char_id and attack_load.target is not None:
                if self._counter_targets.get(attack_load.target.char_id):
                    attack_load.bda += counter_bda_bonus
                    attack_load.history.append(HistoryEmitter.passive(self.name, self.owner.char_id))
                    attack_load.history.append(HistoryEmitter.atk_load("bda", counter_bda_bonus, attack_load.bda))

        def turn_end_hook(action_load: ActionLoad):
            if action_load.character.char_id == self.owner.char_id:
                from core.Enums import BattleActionType
                current_action = self.context.current_action
                if current_action and current_action.action_type != BattleActionType.FREE_ACTION:
                    self._counter_targets.clear()

        return {
            "on_defense_reaction": reacao_bloqueio_hook,
            "on_hit_check": bloqueio_ofensivo_hook,
            "on_roll_modify": bonus_contra_ataque_hook,
            "on_turn_end": turn_end_hook
        }

class PosturaBatalha(BattlePassive):
    def __init__(self, owner: Character, context: IPassiveContext, template: BattlePassiveTemplate | None = None):
        super().__init__(name="Postura de Batalha", owner=owner, context=context, template=template)
        self.current_postura = None
        self._modifiers = []

    def set_mode(self, mode: str | None, action_load: ActionLoad):
        from core.Modifiers import EphemeralModifier
        for mod in self._modifiers:
            self.owner.remove_modifier(mod)
        self._modifiers = []
        
        self.current_postura = mode
        if mode == "OFFENSIVE":
            m1 = EphemeralModifier(stat_name='grd', value=-1, source=self.name)
            m2 = EphemeralModifier(stat_name='pre', value=1, source=self.name)
            self._modifiers = [m1, m2]
            self.owner.add_modifier(m1)
            self.owner.add_modifier(m2)
            action_load.add_event("POSTURA", self.owner.char_id, "OFFENSIVE")
        elif mode == "DEFENSIVE":
            m1 = EphemeralModifier(stat_name='pre', value=-1, source=self.name)
            m2 = EphemeralModifier(stat_name='grd', value=1, source=self.name)
            self._modifiers = [m1, m2]
            self.owner.add_modifier(m1)
            self.owner.add_modifier(m2)
            action_load.add_event("POSTURA", self.owner.char_id, "DEFENSIVE")
        else:
            action_load.add_event("POSTURA", self.owner.char_id, "NONE")

    def get_hooks(self) -> dict[str, Callable]:
        def on_gda_modify(attack_load: AttackLoad):
            if self.current_postura == "OFFENSIVE" and attack_load.character.char_id == self.owner.char_id and attack_load.hit:
                params = self.template.parameters if self.template else {}
                gda_bonus = params.get("offensive_gda_bonus", 2)
                high_bonus = params.get("offensive_high_bonus", 4)
                threshold = params.get("offensive_threshold", 7)
                
                bonus = gda_bonus
                if attack_load.attack_roll > threshold:
                    bonus = high_bonus
                attack_load.gda += bonus
                attack_load.history.append(HistoryEmitter.passive(self.name, self.owner.char_id))
                attack_load.history.append(HistoryEmitter.atk_load("gda", bonus, attack_load.gda))

        def on_defense_reaction(attack_load: AttackLoad):
            from core.Enums import RollState
            if self.current_postura == "DEFENSIVE" and attack_load.target is not None and attack_load.target.char_id == self.owner.char_id:
                # on_defense_reaction only fires on a confirmed hit; no GdA check needed.
                params = self.template.parameters if self.template else {}
                reroll_cost = params.get("reroll_cost", 2)
                
                if self.owner.floating_focus >= reroll_cost:
                    controller = self.context.get_controller(self.owner.char_id)
                    if controller and controller.choose_reaction(self.owner, f"{self.name}_REROLL", attack_load, self.context):
                        if CharacterSystem.spend_focus(self.owner, reroll_cost):
                            attack_load.history.append(HistoryEmitter.focus(self.owner.char_id, -reroll_cost, self.owner.floating_focus))
                            
                            new_roll_res = self.dice_service.roll_dice(attack_load.def_die, RollState.NEUTRAL)
                            attack_load.history.append(HistoryEmitter.roll("DEF_REROLL", new_roll_res.final_roll, attack_load.def_die, self.owner.char_id))
                            
                            diff = new_roll_res.final_roll - attack_load.defense_roll
                            attack_load.gda -= diff
                            attack_load.defense_roll = new_roll_res.final_roll
                            attack_load.history.append(HistoryEmitter.passive(self.name, self.owner.char_id))
                            attack_load.history.append(HistoryEmitter.atk_load("defense_roll", diff, attack_load.defense_roll))
                            attack_load.history.append(HistoryEmitter.atk_load("gda", -diff, attack_load.gda))

        return {
            'on_gda_modify': on_gda_modify,
            'on_defense_reaction': on_defense_reaction
        }

class RitmoAcelerado(BattlePassive):
    def __init__(self, owner: Character, context: IPassiveContext, template: BattlePassiveTemplate | None = None):
        super().__init__(name="Ritmo Acelerado", owner=owner, context=context, template=template)

    def get_hooks(self) -> dict[str, Callable]:
        from core.Enums import BattleActionType

        def on_attack_end(attack_load: AttackLoad):
            if attack_load.character.char_id == self.owner.char_id:
                current_action = self.context.current_action
                if current_action and current_action.action_type != BattleActionType.MOVE_ACTION:
                    params = self.template.parameters if self.template else {}
                    threshold_roll = params.get("threshold_roll", 7)
                    
                    if attack_load.attack_roll >= threshold_roll:
                        current_action.action_type = BattleActionType.MOVE_ACTION
                        attack_load.history.append(HistoryEmitter.passive(self.name, self.owner.char_id))
                        attack_load.history.append(HistoryEmitter.msg(f"{self.name}: Ação de Movimento!"))

        return {
            'on_attack_end': on_attack_end
        }

registry = {
    "MãosPesadas": MãosPesadas,
    "ForçaBruta": ForçaBruta,
    "Combo": Combo,
    "GraçaDoDuelista": GracaDoDuelista,
    "PosturaDefensiva": PosturaDefensiva,
    "Bloquear": Bloquear,
    "Postura de Batalha": PosturaBatalha,
    "Ritmo Acelerado": RitmoAcelerado
}
