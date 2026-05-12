from __future__ import annotations
from typing import Callable, Dict, TYPE_CHECKING
from core.Enums import RollState, AttackType
from core.Events import AttackLoad, HistoryEmitter
from core.BaseClasses import IPassiveContext, BattlePassive, ActionLoad
from core.CharacterSystem import CharacterSystem

if TYPE_CHECKING:
    from entities.Characters import Character
from battle.StatusEffects import Atordoado
from battle.BattleActions import AttackAction

class ForçaBruta(BattlePassive):
    def __init__(self, owner: 'Character', context: 'IPassiveContext'):
        super().__init__(name="Força Bruta", owner=owner, context=context)

    def get_hooks(self) -> Dict[str, Callable]:
        def multiply_hook(attack_load: 'AttackLoad'):
            if attack_load.character.char_id == self.owner.char_id:
                if attack_load.hit:
                    val = attack_load.gda
                    attack_load.gda += val
                    attack_load.add_event("MOD", self.name, val, self.owner.char_id)
        return {'on_gda_modify': multiply_hook}

class MãosPesadas(BattlePassive):
    def __init__(self, owner: 'Character', context: 'IPassiveContext'):
        super().__init__(name="Mãos Pesadas", owner=owner, context=context)

    def get_hooks(self) -> Dict[str, Callable]:
        def effect_hook(attack_load: 'AttackLoad'):
            if attack_load.target is None:
                return
            if attack_load.character.char_id == self.owner.char_id:
                if attack_load.hit:
                    if attack_load.gda > 3:
                        effect = Atordoado(duration=0, target=attack_load.target, context=self.context)
                        self.context.add_status_effect(effect)
                        attack_load.add_event("STATUS", attack_load.target.char_id, "Atordoado", 0, "APPLIED")
        return {'on_gda_modify': effect_hook}

class PosturaDefensiva(BattlePassive):
    def __init__(self, owner: 'Character', context: 'IPassiveContext'):
        super().__init__(name="Postura Defensiva", owner=owner, context=context)
        self.is_active = False
        self._dice_modifiers = []
        self._tracked_targets: Dict[str, bool] = {}  # char_id -> penalty_applied

    def toggle(self) -> str:
        from core.Modifiers import EphemeralModifier
        self.is_active = not self.is_active
        if self.is_active:
            # Atacante d12 -> d10 (-2), Defensor d8 -> d10 (+2)
            m1 = EphemeralModifier(stat_name='atk_die', value=-2, source='PosturaDefensiva')
            m2 = EphemeralModifier(stat_name='def_die', value=2, source='PosturaDefensiva')
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

    def _start_tracking(self, target: 'Character'):
        if target.char_id not in self._tracked_targets:
            self._tracked_targets[target.char_id] = False

    def _clear_tracking(self, char_id: str | None = None):
        if char_id:
            if char_id in self._tracked_targets:
                del self._tracked_targets[char_id]
        else:
            self._tracked_targets.clear()

    def get_hooks(self) -> Dict[str, Callable]:
        from core.Modifiers import EphemeralModifier
        
        def hit_hook(attack_load: 'AttackLoad'):
            if self.is_active and attack_load.character.char_id == self.owner.char_id and attack_load.hit:
                self._start_tracking(attack_load.target)
                attack_load.add_event("POSTURA", self.owner.char_id, "OBSERVE", attack_load.target.char_id)

        def penalty_hook(attack_load: 'AttackLoad'):
            cid = attack_load.character.char_id
            if self.is_active and cid in self._tracked_targets and attack_load.target is not None and attack_load.target.char_id == self.owner.char_id:
                attack_load.pre -= 1
                self._tracked_targets[cid] = True
                attack_load.add_event("MOD", "PosturaDefensiva", -1, attack_load.character.char_id)

        def cleanup_hook(attack_load: 'AttackLoad'):
            cid = attack_load.character.char_id
            if cid in self._tracked_targets:
                if self._tracked_targets[cid]:
                    self._clear_tracking(cid)

        def turn_end_hook(action_load: 'ActionLoad'):
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
    def __init__(self, owner: 'Character', context: 'IPassiveContext'):
        super().__init__(name="Graça do Duelista", owner=owner, context=context)

    def get_hooks(self) -> Dict[str, Callable]:
        
        def passiva_acerto_hook(attack_load: 'AttackLoad') -> None: 
            if attack_load.character.char_id == self.owner.char_id:
                roll = self.dice_service.roll_dice(6, RollState.NEUTRAL)
                attack_load.gda += roll.final_roll
                attack_load.add_event("MOD", self.name, roll.final_roll, self.owner.char_id)

        def reacao_evasao_hook(attack_load: 'AttackLoad') -> None:
            if attack_load.target is None:
                return
            if attack_load.target.char_id == self.owner.char_id:
                if attack_load.gda > (0 + attack_load.grd - attack_load.pre):
                    custo_evasao = 2
                    if self.owner.floating_focus >= custo_evasao:
                        controller = self.context.get_controller(self.owner.char_id)
                        if controller and controller.choose_reaction(self.owner, self.name, attack_load, self.context):
                            if CharacterSystem.spend_focus(self.owner, custo_evasao):
                                attack_load.add_event("FOCUS", self.owner.char_id, -custo_evasao, self.owner.floating_focus)
                            
                            roll = self.dice_service.roll_dice(4, RollState.NEUTRAL)
                            attack_load.gda -= roll.final_roll
                            attack_load.add_event("MOD", f"{self.name}_EVASAO", -roll.final_roll, self.owner.char_id)

        return {
            "on_gda_modify": passiva_acerto_hook,
            "on_defense_reaction": reacao_evasao_hook
        }

class Combo(BattlePassive):
    def __init__(self, owner: 'Character', context: 'IPassiveContext'):
        super().__init__(name="Combo", owner=owner, context=context)
        self.stage = 0
        self.hit = False
    
    def get_hooks(self) -> Dict[str, Callable]:
        def checar_ataque_bonus(attack_load: 'AttackLoad'):
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
                    attack_load.add_event("COMBO", self.owner.char_id, 2)
                    attack_load.history.extend(response.history)
                else:
                    self.stage = 0
                    self.hit = False

            elif self.stage > 1:
                if attack_load.hit:
                    effect = Atordoado(0, attack_load.target, self.context)
                    self.context.add_status_effect(effect)
                    attack_load.add_event("STATUS", attack_load.target.char_id, "Atordoado", 0, "APPLIED")
                    attack_load.add_event("COMBO", self.owner.char_id, self.stage, "FINAL")
        
        return {'on_attack_end': checar_ataque_bonus}

class Bloquear(BattlePassive):
    def __init__(self, owner: 'Character', context: 'IPassiveContext'):
        super().__init__(name="Bloquear", owner=owner, context=context)
        self._counter_targets: Dict[str, bool] = {}

    def get_hooks(self) -> Dict[str, Callable]:
        from core.Modifiers import EphemeralModifier

        def reacao_bloqueio_hook(attack_load: 'AttackLoad'):
            if attack_load.target is None or attack_load.target.char_id != self.owner.char_id:
                return
            
            custo = 2
            if self.owner.floating_focus >= custo:
                controller = self.context.get_controller(self.owner.char_id)
                if controller.choose_reaction(self.owner, "Bloquear", attack_load, self.context):
                    if CharacterSystem.spend_focus(self.owner, custo):
                        attack_load.add_event("FOCUS", self.owner.char_id, -custo, self.owner.floating_focus)
                        
                        roll = self.dice_service.roll_dice(4, RollState.NEUTRAL)
                        attack_load.gda -= roll.final_roll
                        attack_load.add_event("MOD", self.name, -roll.final_roll, self.owner.char_id)

                        if attack_load.gda < -3:
                            self._counter_targets[attack_load.character.char_id] = True

        def bonus_contra_ataque_hook(attack_load: 'AttackLoad'):
            if attack_load.character.char_id == self.owner.char_id and attack_load.target is not None:
                if self._counter_targets.get(attack_load.target.char_id):
                    attack_load.bda += 1
                    attack_load.add_event("MOD", "Bloquear_Counter", 1, self.owner.char_id)

        def cleanup_bonus_hook(attack_load: 'AttackLoad'):
            if attack_load.character.char_id == self.owner.char_id:
                if attack_load.target is not None:
                    self._counter_targets.pop(attack_load.target.char_id, None)

        return {
            "on_defense_reaction": reacao_bloqueio_hook,
            "on_roll_modify": bonus_contra_ataque_hook,
            "on_attack_end": cleanup_bonus_hook
        }

class PosturaBatalha(BattlePassive):
    def __init__(self, owner: 'Character', context: 'IPassiveContext'):
        super().__init__(name="Postura de Batalha", owner=owner, context=context)
        self.current_postura = None
        self._modifiers = []

    def set_mode(self, mode: str | None, action_load: 'ActionLoad'):
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

    def get_hooks(self) -> Dict[str, Callable]:
        def on_gda_modify(attack_load: 'AttackLoad'):
            if self.current_postura == "OFFENSIVE" and attack_load.character.char_id == self.owner.char_id and attack_load.hit:
                bonus = 2
                if attack_load.attack_roll > 7:
                    bonus = 4
                attack_load.gda += bonus
                attack_load.add_event("MOD", f"{self.name}_OFF", bonus, self.owner.char_id)

        def on_defense_reaction(attack_load: 'AttackLoad'):
            from core.Enums import RollState
            if self.current_postura == "DEFENSIVE" and attack_load.target is not None and attack_load.target.char_id == self.owner.char_id:
                cost = 2
                if self.owner.floating_focus >= cost:
                    controller = self.context.get_controller(self.owner.char_id)
                    if controller and controller.choose_reaction(self.owner, f"{self.name}_REROLL", attack_load, self.context):
                        if CharacterSystem.spend_focus(self.owner, cost):
                            attack_load.add_event("FOCUS", self.owner.char_id, -cost, self.owner.floating_focus)
                            
                            new_roll_res = self.dice_service.roll_dice(attack_load.def_die, RollState.NEUTRAL)
                            attack_load.add_event("ROLL", "DEF_REROLL", new_roll_res.final_roll, attack_load.def_die, self.owner.char_id)
                            
                            diff = new_roll_res.final_roll - attack_load.defense_roll
                            attack_load.gda -= diff
                            attack_load.defense_roll = new_roll_res.final_roll
                            attack_load.add_event("MOD", f"{self.name}_DEF", -diff, self.owner.char_id)

        return {
            'on_gda_modify': on_gda_modify,
            'on_defense_reaction': on_defense_reaction
        }

class RitmoAcelerado(BattlePassive):
    def __init__(self, owner: 'Character', context: 'IPassiveContext'):
        super().__init__(name="Ritmo Acelerado", owner=owner, context=context)
        self.consecutive_accelerations = 0
        self.processed_actions = set()

    def get_hooks(self) -> Dict[str, Callable]:
        from core.Enums import BattleActionType

        def on_roll_modify(attack_load: 'AttackLoad'):
            if attack_load.character.char_id == self.owner.char_id:
                if self.consecutive_accelerations == 2:
                    attack_load.pre += 2
                    attack_load.history.append(HistoryEmitter.passive(self.name, self.owner.char_id))
                    attack_load.history.append(HistoryEmitter.atk_load("pre", 2, attack_load.pre))

        def on_attack_end(attack_load: 'AttackLoad'):
            if attack_load.character.char_id == self.owner.char_id:
                current_action = self.context.current_action
                if current_action and id(current_action) not in self.processed_actions:
                    self.processed_actions.add(id(current_action))
                    if self.consecutive_accelerations == 2:
                        self.consecutive_accelerations = 0
                    elif attack_load.attack_roll >= 7:
                        if current_action.action_type != BattleActionType.MOVE_ACTION:
                            current_action.action_type = BattleActionType.MOVE_ACTION
                            self.consecutive_accelerations += 1
                            attack_load.history.append(HistoryEmitter.passive(self.name, self.owner.char_id))
                            attack_load.history.append(HistoryEmitter.msg("Ritmo Acelerado: Ação de Movimento!"))
                    else:
                        self.consecutive_accelerations = 0

        return {
            'on_roll_modify': on_roll_modify,
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
