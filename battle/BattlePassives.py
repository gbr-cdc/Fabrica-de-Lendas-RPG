from __future__ import annotations
from typing import Callable, Dict, TYPE_CHECKING
from core.Enums import RollState, AttackType
from core.Events import AttackLoad
from core.BaseClasses import IBattleContext, BattlePassive
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
            if attack_load.character.char_id != self.owner.char_id:
                return

            basic_attack_template = self.context.get_template("BasicAttack")
            
            if self.stage == 0:
                self.stage += 1
                if attack_load.hit:
                    self.hit = True

                response = action_registry["AttackAction"](basic_attack_template, attack_load.character, attack_load.target, self.context, attack_type=AttackType.EXTRA_ATTACK).execute_if_possible()

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
                response = action_registry["AttackAction"](basic_attack_template, attack_load.character, attack_load.target, self.context, attack_type=AttackType.EXTRA_ATTACK).execute_if_possible()
                
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

registry = {
    "MãosPesadas": MãosPesadas,
    "ForçaBruta": ForçaBruta,
    "Combo": Combo,
    "GraçaDoDuelista": GracaDoDuelista
}
