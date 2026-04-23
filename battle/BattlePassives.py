from __future__ import annotations
from typing import Callable, Dict, TYPE_CHECKING
from core.Enums import RollState, AttackType
from core.Events import AttackLoad
from core.BaseClasses import IBattleContext, BattlePassive, ActionLoad
from core.CharacterSystem import CharacterSystem

if TYPE_CHECKING:
    from entities.Characters import Character
from battle.StatusEffects import Atordoado
from battle.BattleActions import AttackAction, registry as action_registry

class GracaDoDuelista(BattlePassive):
    def __init__(self, owner: 'Character', context: 'IBattleContext'):
        super().__init__(name="Graça do Duelista", owner=owner, context=context)

    def get_hooks(self) -> Dict[str, Callable]:
        
        def passiva_acerto_hook(attack_load: 'AttackLoad') -> None: 
            if attack_load.character.char_id == self.owner.char_id:
                roll = self.dice_service.roll_dice(6, RollState.NEUTRAL)
                attack_load.gda += roll.final_roll
                attack_load.history.append(f"[PASSIVA] Graça do Duelista adicionou +{roll.final_roll} de GdA!")

        def reacao_evasao_hook(attack_load: 'AttackLoad') -> None:
            if attack_load.target is None:
                return
            if attack_load.target.char_id == self.owner.char_id:
                if attack_load.gda > (0 + self.owner.grd - attack_load.character.pre):
                    custo_evasao = 2
                    if self.owner.floating_focus >= custo_evasao:
                        controller = self.context.get_controller(self.owner.char_id)
                        if controller and controller.choose_reaction(self.owner, self.name, attack_load, self.context):
                            CharacterSystem.spend_focus(self.owner, custo_evasao)
                            roll = self.dice_service.roll_dice(4, RollState.NEUTRAL)
                            attack_load.gda -= roll.final_roll

                            attack_load.history.append(f"[REAÇÃO] {self.owner.name} gastou 2 de Foco e usou Evasão!")
                            attack_load.history.append(f"Rolou +{roll.final_roll} na Defesa. O GdA caiu para {attack_load.gda}.")

        return {
            "on_gda_modify": passiva_acerto_hook,
            "on_defensive_reaction": reacao_evasao_hook
        }

class ForçaBruta(BattlePassive):
    def __init__(self, owner: 'Character', context: 'IBattleContext'):
        super().__init__(name="Força Bruta", owner=owner, context=context)

    def get_hooks(self) -> Dict[str, Callable]:
        def multiply_hook(attack_load: 'AttackLoad'):
            if attack_load.character.char_id == self.owner.char_id:
                if attack_load.hit:
                    attack_load.gda += attack_load.gda
                    attack_load.history.append(f"[PASSIVA] Força Bruta dobrou o GdA para {attack_load.gda}!")
        return {'on_gda_modify': multiply_hook}

class MãosPesadas(BattlePassive):
    def __init__(self, owner: 'Character', context: 'IBattleContext'):
        super().__init__(name="Mãos Pesadas", owner=owner, context=context)

    def get_hooks(self) -> Dict[str, Callable]:
        def effect_hook(attack_load: 'AttackLoad'):
            if attack_load.target is None:
                return
            if attack_load.character.char_id == self.owner.char_id:
                if attack_load.hit:
                    if attack_load.gda > 3:
                        Atordoado(duration=1, target=attack_load.target, context=self.context)
                    attack_load.history.append(f"[PASSIVA] Mãos Pesadas dobrada o GdA para {attack_load.gda}!")
        return {'on_gda_modify': effect_hook}

class Combo(BattlePassive):
    def __init__(self, owner: 'Character', context: 'IBattleContext'):
        super().__init__(name="Combo", owner=owner, context=context)
        self.stage = 0
        self.hit = False
    
    def get_hooks(self) -> Dict[str, Callable]:
        def checar_ataque_bonus(attack_load: 'AttackLoad'):
            if attack_load.target is None:
                return
            if attack_load.character.char_id != self.owner.char_id:
                return

            basic_attack_template = self.context.get_template("BasicAttack")
            
            if self.stage == 0:
                self.stage += 1
                if attack_load.hit:
                    self.hit = True

                response = action_registry["AttackAction"](basic_attack_template, attack_load.character, [attack_load.target], self.context, attack_type=AttackType.EXTRA_ATTACK).execute_if_possible()

                self.stage = 0
                self.hit = False
                
                if response.success:
                    attack_load.history.append(f"[PASSIVA] Combo! {self.owner.name} ataca novamente (Estágio {self.stage})!")
                    attack_load.history.extend(response.history)

            elif self.stage == 1:
                if not self.hit or not attack_load.hit:
                    self.hit = False
                    self.stage = 0
                    return
                
                self.stage += 1
                response = action_registry["AttackAction"](basic_attack_template, attack_load.character, [attack_load.target], self.context, attack_type=AttackType.EXTRA_ATTACK).execute_if_possible()
                
                if response.success:
                    attack_load.history.append(f"[PASSIVA] Combo! {self.owner.name} ataca novamente (Estágio {self.stage})!")
                    attack_load.history.extend(response.history)
                else:
                    self.stage = 0
                    self.hit = False

            elif self.stage > 1:
                if attack_load.hit:
                    Atordoado(0, attack_load.target, attack_load.battle_context)
                    attack_load.history.append(f"[PASSIVA] Combo! {self.owner.name} ataca novamente (Estágio {self.stage})!")
        
        return {'on_attack_end': checar_ataque_bonus}

class PosturaDefensiva(BattlePassive):
    def __init__(self, owner: 'Character', context: 'IBattleContext'):
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
            return f"{self.owner.name} assumiu a Postura Defensiva!"
        else:
            for mod in self._dice_modifiers:
                self.owner.remove_modifier(mod)
            self._dice_modifiers = []
            self._clear_tracking()
            return f"{self.owner.name} saiu da Postura Defensiva."

    def _start_tracking(self, target: 'Character'):
        if target.char_id not in self._tracked_targets:
            self._tracked_targets[target.char_id] = False

    def _clear_tracking(self, char_id: str | None = None):
        chars = {c.char_id: c for c in self.context.get_characters()}
        if char_id:
            if char_id in self._tracked_targets:
                if self._tracked_targets[char_id] and char_id in chars:
                    chars[char_id].remove_modifiers_by_source("PosturaDefensiva_Penalidade")
                del self._tracked_targets[char_id]
        else:
            for cid, applied in self._tracked_targets.items():
                if applied and cid in chars:
                    chars[cid].remove_modifiers_by_source("PosturaDefensiva_Penalidade")
            self._tracked_targets = {}

    def get_hooks(self) -> Dict[str, Callable]:
        from core.Modifiers import EphemeralModifier
        
        def hit_hook(attack_load: 'AttackLoad'):
            if self.is_active and attack_load.character.char_id == self.owner.char_id and attack_load.hit:
                self._start_tracking(attack_load.target)
                attack_load.history.append(f"[POSTURA] {self.owner.name} está observando {attack_load.target.name}!")

        def penalty_hook(attack_load: 'AttackLoad'):
            cid = attack_load.character.char_id
            if self.is_active and cid in self._tracked_targets and attack_load.target is not None and attack_load.target.char_id == self.owner.char_id:
                mod = EphemeralModifier(stat_name='pre', value=-1, source='PosturaDefensiva_Penalidade')
                attack_load.character.add_modifier(mod)
                self._tracked_targets[cid] = True
                attack_load.history.append(f"[POSTURA] {attack_load.character.name} sofre penalidade de -1 de Precisão contra {self.owner.name}!")

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

registry = {
    "MãosPesadas": MãosPesadas,
    "ForçaBruta": ForçaBruta,
    "Combo": Combo,
    "GraçaDoDuelista": GracaDoDuelista,
    "PosturaDefensiva": PosturaDefensiva
}
