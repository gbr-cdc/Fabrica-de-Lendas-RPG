from core.Models import PassiveAbility, Character, AttackLoad, RollState
from core.BattleManager import BattleManager
from Effects import Atordoado
from Actions import BasicAttack


class GracaDoDuelista(PassiveAbility):
    def __init__(self, actor: 'Character', battle_manager: 'BattleManager'):
        super().__init__(name="Graça do Duelista", owner=actor, battle_manager=battle_manager)

    # O motor chama isso uma vez para cada personagem quando o combate começa
    def register_listeners(self):
        
        # 1. Criamos a Passiva de Acerto. 
        # Ela "prende" as variáveis 'owner' e 'battle_manager' deste escopo específico.
        def passiva_acerto_hook(attack_load: 'AttackLoad') -> None:
            # Note que não usamos 'self.owner', usamos direto a variável local 'owner'
            if attack_load.character.char_id == self.owner.char_id:
                roll = self.battle_manager.dice_service.roll_dice(6, RollState.NEUTRAL)
                attack_load.gda += roll.final_roll
                attack_load.history.append(f"[PASSIVA] Graça do Duelista adicionou +{roll.final_roll} de GdA!")

        # 2. Criamos a Reação de Evasão.
        def reacao_evasao_hook(attack_load: 'AttackLoad') -> None:
            if attack_load.target.char_id == self.owner.char_id:
                if attack_load.gda > (0 + self.owner.grd - attack_load.character.pre):
                    custo_evasao = 2
                    if self.owner.floating_focus >= custo_evasao:
                        if self.owner.controller.choose_reaction(self.owner, self.name, attack_load, self.battle_manager):
                            self.owner.spend_focus(custo_evasao)
                            roll = self.battle_manager.dice_service.roll_dice(4, RollState.NEUTRAL)
                            attack_load.gda -= roll.final_roll

                            attack_load.history.append(f"[REAÇÃO] {self.owner.name} gastou 2 de Foco e usou Evasão!")
                            attack_load.history.append(f"Rolou +{roll.final_roll} na Defesa. O GdA caiu para {attack_load.gda}.")

        # 3. Inscrevemos os "hooks" independentes que acabamos de criar.
        self.battle_manager.subscribe('on_gda_modify', passiva_acerto_hook)
        self.battle_manager.subscribe('on_defense_reaction', reacao_evasao_hook)

class ForçaBruta(PassiveAbility):
    def __init__(self, actor: 'Character', battle_manager: 'BattleManager'):
        super().__init__(name="Força Bruta", owner=actor, battle_manager=battle_manager)

    def register_listeners(self):
        def multiply_hook(self, attack_load: 'AttackLoad'):
            if attack_load.character.char_id == self.owner.char_id:
                if attack_load.hit:
                    attack_load.gda += attack_load.gda
                    attack_load.history.append(f"[PASSIVA] Força Bruta dobrou o GdA para {attack_load.gda}!")
        self.battle_manager.subscribe('on_gda_modify', multiply_hook)
        self.active_hooks.append(multiply_hook)
    
    

class MãosPesadas(PassiveAbility):
    def __init__(self, actor: 'Character', battle_manager: 'BattleManager'):
        super().__init__(name="Mãos Pesadas", owner=actor, battle_manager=battle_manager)

    def register_listeners(self):
        def effect_hook(self, attack_load: 'AttackLoad'):
            if attack_load.character.char_id == self.owner.char_id:
                if attack_load.hit:
                    if attack_load.gda > 3:
                        Atordoado(duration=0, target=attack_load.target, battle_manager=self.battle_manager)
                    attack_load.history.append(f"[PASSIVA] Mãos Pesadas dobrada o GdA para {attack_load.gda}!")
        self.battle_manager.subscribe('on_gda_modify', effect_hook)


class Combo(PassiveAbility):
    def __init__(self, owner: 'Character', battle_manager: 'BattleManager'):
        super().__init__(name="Combo", owner=owner, battle_manager=battle_manager)
        self.stage = 0
        self.hit = False
    
    def register_listeners(self):
        def checar_ataque_bonus(attack_load: 'AttackLoad'):
            if attack_load.character.char_id != self.owner.char_id:
                return

            basic_attack_template = self.battle_manager.data_service.get_action_template("BasicAttack")
            
            if self.stage == 0:
                self.stage += 1
                if attack_load.hit:
                    self.hit = True

                response = BasicAttack(basic_attack_template, attack_load.character, attack_load.target, self.battle_manager).execute_if_possible()

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
                response = BasicAttack(basic_attack_template, attack_load.character, attack_load.target, self.battle_manager).execute_if_possible()
                
                if response.success:
                    attack_load.history.append(f"[PASSIVA] Combo! {self.owner.name} ataca novamente (Estágio {self.stage})!")
                    attack_load.history.extend(response.history)
                else:
                    self.stage = 0
                    self.hit = False

            elif self.stage > 1:
                if attack_load.hit:
                    Atordoado(0, attack_load.target, attack_load.battle_manager)
                    attack_load.history.append(f"[PASSIVA] Combo! {self.owner.name} ataca novamente (Estágio {self.stage})!")
                


        # Inscreve no motor
        self.battle_manager.subscribe('on_attack_end', checar_ataque_bonus)
        
        # Lembra que tem que ser uma Tupla para o unregister_listeners saber qual evento limpar!
        self.active_hooks.append(('on_attack_end', checar_ataque_bonus))

registry = {
    "MãosPesadas": MãosPesadas,
    "ForçaBruta": ForçaBruta,
    "Combo": Combo,
    "GraçaDoDuelista": GracaDoDuelista
}
