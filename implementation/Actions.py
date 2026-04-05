from typing import Dict, Any
from core.Models import Ability, Character, RollState
from core.BattleManager import BattleManager

class BasicAttack(Ability):
    
    def __init__(self):
        # O Ataque Básico custa 0 de foco e seu tempo de ação é dinâmico (vem da HAB)
        super().__init__(name="Ataque Básico", focus_cost=0, action_cost=0)
    
    def can_execute(self, caster: 'Character', target: 'Character') -> tuple[bool, str]:
        # Regra 1: O alvo está vivo?
        if not target.is_alive():
            return False, "O alvo já está derrotado!"
        
        return True, ""

    def execute(self, caster: 'Character', target: 'Character', battle_manager: 'BattleManager', **kwargs) -> Dict[str, Any]:
        event_data = {'caster': caster, 'target': target, 'battle_manager': battle_manager, 'is_skill': kwargs.get('is_skill', False), 'attack_state': RollState.NEUTRAL, 'defense_state': RollState.NEUTRAL}
        event_data = battle_manager.emit('on_roll_modify', event_data) # Permite que passivas modifiquem os dados antes do rolamento (ex: Inspiração)
        # 1. Rola os dados
        atk_roll = battle_manager.dice_service.roll_dice(caster.atk_die, event_data['attack_state'])
        mod_atk_roll = atk_roll + caster.rank + caster.bda
        event_data["history"] = [f"{caster.name} rolou {atk_roll} para atacar!"]
        event_data["history"].append(f"Bônus de Rank do atacante: {caster.rank} | Bônus de Ataque: {caster.bda} | Total modificado: {mod_atk_roll}")
        def_roll = battle_manager.dice_service.roll_dice(target.def_die, event_data['defense_state'])
        mod_def_roll = def_roll + target.rank + target.bdd
        event_data["history"].append(f"{target.name} rolou {def_roll} para defender!")
        event_data["history"].append(f"Bônus de Rank do defensor: {target.rank} | Bônus de Defesa: {target.bdd} | Total modificado: {mod_def_roll}")
        
        # 2. Calcula o GdA base
        gda = mod_atk_roll - mod_def_roll
        event_data['gda'] = gda
        event_data["history"].append(f"GdA base é {gda} ({mod_atk_roll} - {mod_def_roll})")
        event_data = battle_manager.emit('on_defense_reaction', event_data) # Permite que passivas possam anular o hit (ex: Esquiva Perfeita)
        event_data = battle_manager.emit('on_hit_check', event_data) # Permite que passivas chequem o gda inicial para suas condições de ativação
        hit = False
        gda = event_data['gda']
        if gda > (0 + target.grd - caster.pre): 
            hit = True
            if gda < 0:
                gda = 0
                event_data['gda'] = gda
            event_data = battle_manager.emit('on_gda_modify', event_data) # Permite que passivas modifiquem o GdA (ex: Força Bruta, Letalidade)

        # 3. Resolve o Dano
        if hit:
            event_data["history"].append("O ataque acertou!")
            event_data = battle_manager.emit('on_damage_calculation', event_data) # Momento onde Habilidades Marciais aplicam seus bônus de dano
            final_gda = max(0, event_data['gda']) # Recarrega o GdA caso alguma passiva tenha modificado ele na etapa de cálculo de dano
            damage = caster.pda + (caster.mda * final_gda)
            event_data["history"].append(f"Dano calculado: PDA {caster.pda} + (MDA {caster.mda} x GdA {final_gda}) = {damage}") 
            target.take_damage(damage)
            event_data["damage"] = damage
            event_data = battle_manager.emit('on_damage_taken', event_data)
        else:
            event_data["history"].append("O ataque foi completamente defendido!")

        # O custo de ação é puxado direto do atributo do personagem
        self.action_cost = caster.action_cost_base

        event_data = battle_manager.emit('on_attack_end', event_data)

        # Retorna o resumo para o View (Terminal/Pygame) renderizar
        return event_data

class GenerateManaAction(Ability):
    def __init__(self):
        # Gerar mana não custa foco, mas custa o Tempo de Ação base do personagem
        super().__init__(name="Concentrar Mana", focus_cost=0, action_cost=0)

    def can_execute(self, caster: 'Character', target: 'Character') -> tuple[bool, str]:
        # Regra 1: O tanque secou?
        if caster.current_mp <= 0:
            return False, "Sua reserva diária de mana esgotou!"
            
        # Regra 2: A mão já está cheia?
        max_floating = 5 * caster.men
        if caster.floating_mp >= max_floating:
            return False, "Sua mana engatilhada já está no limite!"
            
        return True, ""

    def execute(self, caster: 'Character', target: 'Character', battle_manager: 'BattleManager') -> dict:
        # Usa a lógica que você já fez na classe Character
        old_floating = caster.floating_mp
        new_floating = caster.generate_mana()
        generated = new_floating - old_floating
        
        self.action_cost = caster.action_cost_base # Puxa o custo de HAB

        return {
            "history": f"{caster.name} gerou {generated} de Mana!"
        }

class GenerateFocusAction(Ability):
    def __init__(self):
        # Como é uma ação ativa do turno, não custa foco para usar, mas custará o Tempo de Ação
        super().__init__(name="Concentrar Foco", focus_cost=0, action_cost=0)

    def can_execute(self, caster: 'Character', target: 'Character') -> tuple[bool, str]:
        # O teto máximo de foco é 5 vezes a Mente (MEN)
        max_focus = 5 * caster.men
        
        # Validação: O tanque já está cheio?
        if caster.floating_focus >= max_focus:
            return False, "Seu Foco já está no limite máximo!"
            
        return True, ""

    def execute(self, caster: 'Character', target: 'Character', battle_manager: 'BattleManager') -> dict:
        # Guardamos o valor antigo para saber exatamente quanto foi gerado neste turno
        old_focus = caster.floating_focus
        
        # Chama o método matemático limpo que você já construiu no Character
        new_focus = caster.generate_focus()
        
        generated = new_focus - old_focus
        
        # A ação gasta o tempo padrão do personagem no Relógio de Ticks
        self.action_cost = caster.action_cost_base

        # Retorna o dicionário para a View ler e mostrar na tela/terminal
        return {
            "history": f"{caster.name} respirou fundo e gerou {generated} de Foco!"
        }

class SkillNivelUm(Ability):
    def __init__(self):
        super().__init__(name="Skill Nível 1", focus_cost=4, action_cost=0)

    def can_execute(self, caster: 'Character', target: 'Character') -> tuple[bool, str]:
        if caster.floating_focus < self.focus_cost:
            return False, "Foco insuficiente para usar esta habilidade!"
        return True, ""

    def execute(self, caster: 'Character', target: 'Character', battle_manager: 'BattleManager') -> dict:
        self.caster = caster
        caster.spend_focus(self.focus_cost)
        battle_manager.subscribe('on_damage_calculation', self.add_Damage)
        ataque = BasicAttack()
        event_data = ataque.execute(caster, target, battle_manager, is_skill=True)
        battle_manager.unsubscribe('on_damage_calculation', self.add_Damage)

        return event_data
    
    def add_Damage(self, event_data: dict) -> dict:
        if event_data['caster'].char_id == self.caster.char_id:
            event_data['gda'] += 5 # Adiciona um bônus fixo de GdA
            event_data['history'].append(f"[SKILL] {self.name} aumentou o GdA em +5!")
        return event_data
    
class Evasão(Ability):
    def __init__(self):
        super().__init__(name="Evasão", focus_cost=2, action_cost=0)
    
    def register_listeners(self, caster: 'Character', battle_manager: 'BattleManager'):
        battle_manager.subscribe('on_defense_reaction', self.apply_passive)
        self.caster = caster
    
    def can_execute(self, caster: Character, target: Character) -> tuple[bool, str]:
        if caster.floating_focus < self.focus_cost:
            return False, "Foco insuficiente para usar esta habilidade!"
        return True, ""
    
    def apply_passive(self, event_data: dict) -> dict:
        if event_data['target'].char_id == self.caster.char_id:
            if event_data['gda'] > 0:
                can_use, msg = self.can_execute(self.caster, event_data['caster'])
                if can_use:
                    self.caster.spend_focus(self.focus_cost)
                    roll = event_data['battle_manager'].dice_service.roll_dice(4) # Rola 1d4
                    event_data['gda'] -= roll # Reduz o GdA com um rolamento de 1d4
                    event_data['history'].append(f"[SKILL] {self.caster.name} usou Evasão! GdA reduzido em {roll} para {event_data['gda']}!")
        
        return event_data
