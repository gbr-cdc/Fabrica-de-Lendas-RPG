from core.Models import Ability, Character
from core.BattleManager import BattleManager
from Effects import Atordoado
from Actions import BasicAttack

class Letalidade(Ability):
    def __init__(self):
        super().__init__(name="Letalidade", focus_cost=0, action_cost=0)

    def register_listeners(self, caster: 'Character', battle_manager: 'BattleManager'):
        battle_manager.subscribe('on_gda_modify', self.apply_passive)
        self.caster = caster

    def apply_passive(self, event_data: dict) -> dict:
        if event_data['caster'].char_id == self.caster.char_id:
            if event_data['gda'] > 0:
                roll = event_data['battle_manager'].dice_service.roll_dice(6)
                event_data['gda'] += roll
                event_data['history'].append(f"[PASSIVA] {self.caster.name} ativou Letalidade! GdA aumentado em {roll} para {event_data['gda']}!")
        
        return event_data

class MãosPesadas(Ability):
    def __init__(self):
        super().__init__(name="Mãos Pesadas", focus_cost=0, action_cost=0)
    
    def register_listeners(self, caster: 'Character', battle_manager: 'BattleManager'):
        battle_manager.subscribe('on_hit_check', self.apply_passive)
        self.caster = caster
    
    def apply_passive(self, event_data: dict) -> dict:
        if event_data['caster'].char_id == self.caster.char_id:
            if event_data['gda'] > 3:
                atordoamento = Atordoado(duration=0, target=event_data['target'])
                atordoamento.apply(event_data['battle_manager'])
        return event_data


class ForcaBruta(Ability):
    def __init__(self):
        # É uma passiva, não gasta recursos nem tempo
        super().__init__(name="Força Bruta", focus_cost=0, action_cost=0)

    def register_listeners(self, caster: 'Character', battle_manager: 'BattleManager'):
        # Aqui ela avisa o BattleManager: "Me chame quando o GdA for calculado!"
        battle_manager.subscribe('on_gda_modify', self.apply_passive)

        # Guardamos a referência do dono para saber se o evento é nosso
        self.caster = caster

    def apply_passive(self, event_data: dict) -> dict:
        # Verifica se quem está atacando é o dono desta habilidade
        if event_data['caster'].char_id == self.caster.char_id:
            if event_data['gda'] > 0:
                # Dobra o GdA silenciosamente
                event_data['gda'] *= 2 
                event_data['history'].append(f"[PASSIVA] {self.caster.name} ativou Força Bruta! GdA dobrado para {event_data['gda']}!")
        
        return event_data

    # can_execute e execute podem simplesmente retornar False ou pass, 
    # pois o jogador nunca seleciona essa habilidade ativamente no menu.
    def can_execute(self, caster: 'Character', target: 'Character') -> tuple[bool, str]:
        return False, "Esta é uma habilidade passiva."
    
class RitmoAcelerado(Ability):
    def __init__(self):
        super().__init__(name="Ritmo Acelerado", focus_cost=0, action_cost=0)
        self.current_target_id = None
        
        # O nosso Mutex / Guarda de Reentrada
        self.is_busy = False
    
    def register_listeners(self, caster: 'Character', battle_manager: 'BattleManager'):
        # Aqui ela avisa o BattleManager: "Me chame quando o ataque terminar!"
        battle_manager.subscribe('on_attack_end', self.checar_ataque_bonus)

        # Guardamos a referência do dono para saber se o evento é nosso
        self.caster = caster

    def checar_ataque_bonus(self, event_data: dict) -> dict:
        # 1. A trava de segurança! Se já estamos processando um ataque bônus, ignora.
        if self.is_busy:
            return event_data
        
        if event_data.get('is_skill', False): 
            return event_data

        if event_data['caster'].char_id == self.caster.char_id:
            
            if self.current_target_id == event_data['target'].char_id:
                event_data['history'].append(f"[PASSIVA] Ritmo Acelerado! Ataque extra em {event_data['target'].name}!")
                
                ataque_bonus = BasicAttack()
                self.current_target_id = None
                
                # 2. Tranca o Mutex
                self.is_busy = True 
                
                try:
                    # 3. Executa o ataque. Qualquer evento que ele gerar vai bater no 'if self.is_busy' ali em cima e ser ignorado por esta passiva.
                    extra_data = ataque_bonus.execute(self.caster, event_data['target'], event_data['battle_manager'])
                    event_data['history'].extend(extra_data['history'])
                finally:
                    # 4. Libera o Mutex, INDEPENDENTEMENTE de o ataque ter dado certo ou lançado uma exceção/erro.
                    self.is_busy = False
            else:
                # Se o ataque foi para um alvo diferente, atualiza o alvo monitorado por esta passiva.
                self.current_target_id = event_data['target'].char_id
                
        return event_data

class Combo(Ability):
    
    def __init__(self, name = "Combo", focus_cost = 0, action_cost = 0):
        super().__init__(name, focus_cost, action_cost)
        self.stage = 0
    
    def register_listeners(self, caster: 'Character', battle_manager: 'BattleManager'):
        # Aqui ela avisa o BattleManager: "Me chame quando o ataque terminar!"
        battle_manager.subscribe('on_attack_end', self.checar_ataque_bonus)

        # Guardamos a referência do dono para saber se o evento é nosso
        self.caster = caster
    
    def checar_ataque_bonus(self, event_data: dict) -> dict:
        if event_data.get('is_skill', False): 
            return event_data
        if event_data['caster'].char_id == self.caster.char_id:
            if self.stage == 0 or self.stage == 1:
                if event_data['gda'] > 0:
                    event_data['history'].append(f"[PASSIVA] Combo! {self.caster.name} ataca novamente!")
                    ataque_bonus = BasicAttack()
                    self.stage += 1
                    extra_data = ataque_bonus.execute(self.caster, event_data['target'], event_data['battle_manager'])
                    event_data['history'].extend(extra_data['history'])
                else:
                    self.stage = 0 # Reseta o combo se errar o ataque
            else:
                self.stage = 0 # Reseta o combo se chegar no estágio 3 (ou seja, após 3 ataques)
        return event_data
