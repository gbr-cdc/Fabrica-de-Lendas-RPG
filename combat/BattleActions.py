
from __future__ import annotations
from dataclasses import dataclass
from core.Bases import GameAction
from core.Events import ActionLoad, AttackLoad
from core.Enums import BattleInteractionType, BattleActionType, RollState
from combat.BattleManager import BattleManager
from entities.Characters import Character

class BattleAction(GameAction):
    """
    Comandos executados no contexto de batalha.
    """
    # Parâmetros relevantes recebidos através do construtor, de forma que os métodos não possuam parâmetros em conformidade com o Command Pattern
    def __init__(self, template: 'BattleActionTemplate', actor: 'Character', target: 'Character', battle_manager: 'BattleManager'):
        super().__init__(name=template.nome, actor=actor)
        self.action_type = template.action_type
        self.focus_cost = template.focus_cost
        self.target = target
        self.battle_manager = battle_manager

    def can_execute(self) -> tuple[bool, str]:
        """
        Valida se a ação pode ser usada, retorna uma tupla (Sucesso?, "Mensagem de Erro ou Sucesso").
        Por padrão, retorna true, mas habilidades ativas devem sobrescrever para validar custo de foco, alcance, etc.
        """        
        return True, ""

    def execute(self) -> ActionLoad:
        """
        Executa a lógica da ação e retorna um ActionLoad com um histórico do resultado.
        Por padrão, retorna um ActionLoad indicando que a habilidade não pode ser executada, mas habilidades ativas devem sobrescrever para implementar sua lógica.
        """
        return ActionLoad(character=self.actor, history=[f"A abilidade {self.name} não pode ser executada!"], success=False)


class BasicAttack(BattleAction):
    """
    Possui a lógica completa de uma ação de ataque. Dispara eventos de acordo com seu estado de resolução.
    Outras habilidades utilizam estes eventos para funcionar ou usam essa classe para criar uma instância de ataque.
    Ações não ofensivas (que não rolam um ataque) são uma excessão e imprementam lógicas próprias
    """
    
    def __init__(self, template: 'BattleActionTemplate', actor: 'Character', target: 'Character', battle_manager: 'BattleManager', interaction_type: BattleInteractionType = BattleInteractionType.BASIC_ATTACK):
        super().__init__(template=template, actor=actor, target=target, battle_manager=battle_manager)
        self.interaction_type = interaction_type

    def can_execute(self) -> tuple[bool, str]:
        # Regra 1: O alvo está vivo?
        if not self.target.is_alive():
            return False, "O alvo já está derrotado!"
        return True, ""

    def execute(self) -> ActionLoad:
        # Cria o ActionLoad específico para ataques, que será passado por referência em todos os eventos relacionados a este ataque
        attack_load = AttackLoad(
            character=self.actor,
            target=self.target,
            battle_manager=self.battle_manager,
            interaction_type=self.interaction_type,
            attack_state=RollState.NEUTRAL,
            defense_state=RollState.NEUTRAL,
            gda = 0,
            damage = 0
        )

        # Primeiro sinal: permite que habilidades modifiquem o estado do ataque (vantagem, desvantagem, neutro)
        self.battle_manager.emit('on_roll_modify', attack_load)
        
        # Rolagem de ataque
        roll_result = self.battle_manager.dice_service.roll_dice(self.actor.atk_die, attack_load.attack_state)
        if roll_result.rollstate == RollState.ADVANTAGE:
            attack_load.history.append(f"{self.actor.name} tem vantagem! Rolou {roll_result.roll1} e {roll_result.roll2}, ficando com {roll_result.final_roll}!")
        elif roll_result.rollstate == RollState.DISADVANTAGE:
            attack_load.history.append(f"{self.actor.name} tem desvantagem! Rolou {roll_result.roll1} e {roll_result.roll2}, ficando com {roll_result.final_roll}!")
        else:
            attack_load.history.append(f"{self.actor.name} rolou {roll_result.final_roll} para atacar!")
        mod_atk_roll = roll_result.final_roll + self.actor.rank + self.actor.bda
        attack_load.history.append(f"Bônus de Rank do atacante: {self.actor.rank} | Bônus de Ataque: {self.actor.bda} | Total modificado: {mod_atk_roll}")
        
        # Rolagem de defesa
        roll_result = self.battle_manager.dice_service.roll_dice(self.target.def_die, attack_load.defense_state)
        if roll_result.rollstate == RollState.ADVANTAGE:
            attack_load.history.append(f"{self.target.name} tem vantagem na defesa! Rolou {roll_result.roll1} e {roll_result.roll2}, ficando com {roll_result.final_roll}!")
        elif roll_result.rollstate == RollState.DISADVANTAGE:
            attack_load.history.append(f"{self.target.name} tem desvantagem na defesa! Rolou {roll_result.roll1} e {roll_result.roll2}, ficando com {roll_result.final_roll}!")
        else:
            attack_load.history.append(f"{self.target.name} rolou {roll_result.final_roll} para defender!")
        mod_def_roll = roll_result.final_roll + self.target.rank + self.target.bdd
        attack_load.history.append(f"Bônus de Rank do defensor: {self.target.rank} | Bônus de Defesa: {self.target.bdd} | Total modificado: {mod_def_roll}")
        
        # Cálculo do GdA base
        attack_load.gda = mod_atk_roll - mod_def_roll
        attack_load.history.append(f"GdA base é {attack_load.gda} ({mod_atk_roll} - {mod_def_roll})")
        # Segundo sinal: permite que reações reajustem o GdA antes da verificação de acerto
        self.battle_manager.emit('on_defense_reaction', attack_load)
        attack_load.history.append(f"GdA após reações defensivas é {attack_load.gda}, a precisão de {self.actor.name} é {self.actor.pre} e a guarda de {self.target.name} é {self.target.grd}.")
        if attack_load.gda > (0 + self.target.grd - self.actor.pre): # Aplica a lógica de Precisão e Guarda
            attack_load.hit = True
            # Terceiro sinal: permite que passivas chequem o GdA para suas condições de ativação
            self.battle_manager.emit('on_hit_check', attack_load)
            # Transforma o GdA negativo em 0 para o cáculo de dano
            if attack_load.gda < 0:
                attack_load.gda = 0
            # Quarto sinal: permite que passivas reajustem o GdA antes do cálculo de dano
            self.battle_manager.emit('on_gda_modify', attack_load)

            attack_load.history.append("O ataque acertou!")
            # Quinto sinal: permite que magias e skills modifiquem os parâmetros do ataque antes do cálculo de dano
            self.battle_manager.emit('on_damage_calculation', attack_load)
            final_gda = max(0, attack_load.gda)
            attack_load.damage = attack_load.damage + self.actor.pda + (self.actor.mda * final_gda)
            attack_load.history.append(f"Dano calculado: PDA {self.actor.pda} + (MDA {self.actor.mda} x GdA {final_gda}) = {attack_load.damage}") 
            self.battle_manager.emit('on_damage_taken', attack_load)
            self.target.take_damage(attack_load.damage)
        else:
            attack_load.history.append("O ataque foi completamente defendido!")
            # Terceiro sinal: permite que passivas chequem o GdA para suas condições de ativação
            self.battle_manager.emit('on_hit_check', attack_load)

        # Sexto sinal: informa o fim do ataque
        self.battle_manager.emit('on_attack_end', attack_load)
        if(self.interaction_type == BattleInteractionType.BASIC_ATTACK):
            self.actor.generate_focus()

        return attack_load

@dataclass
class BattleActionTemplate:
    id: str
    nome: str
    action_type: BattleActionType
    focus_cost: int
    command: type[BattleAction]

class GenerateManaAction(BattleAction):
    """
    Ação padrão para gerar mana
    """
    def __init__(self, template: BattleActionTemplate, actor: 'Character', target: 'Character', battle_manager: 'BattleManager'):
        super().__init__(template = template, actor=actor, target=target, battle_manager=battle_manager)

    def can_execute(self) -> tuple[bool, str]:
        """ 
        Verifica a reserva de mana e o limite de mana manifestada antes de permitir e retorna uma tupla (can_execute: bool, message: str).
        """
        # Regra 1: O tanque secou?
        if self.actor.current_mp <= 0:
            return False, "Sua reserva diária de mana esgotou!"
            
        # Regra 2: O mão já está cheia?
        max_floating = self.actor.rules.limite_mana * self.actor.men
        if self.actor.floating_mp >= max_floating:
            return False, "Sua mana manifestada já está no limite!"
        return True, ""

    def execute(self) -> ActionLoad:
        """
        Gera mana usando a lógica interna do Character e retorna um ActionLoad.
        """
        old_floating = self.actor.floating_mp
        # Lógica interna de gerar mana dentro de Character
        new_floating = self.actor.generate_mana()
        generated = new_floating - old_floating

        return ActionLoad(
            character=self.actor,
            history=[f"{self.actor.name} canalizou sua energia e gerou {generated} de Mana!"]
        )

class GenerateFocusAction(BattleAction):
    """
    Ação padrão para gerar foco
    """
    def __init__(self, template: BattleActionTemplate, actor: 'Character', target: 'Character', battle_manager: 'BattleManager'):
        super().__init__(template=template, actor=actor, target=target, battle_manager=battle_manager)

    def can_execute(self) -> tuple[bool, str]:
        """
        Verifica o limite de foco manifestado e retorna uma tupla (can_execute: bool, message: str).
        """
        max_focus = self.actor.rules.limite_foco * self.actor.men
        
        # Regra: O foco já está no limite?
        if self.actor.floating_focus >= max_focus:
            return False, "Seu Foco já está no limite máximo!"
            
        return True, ""

    def execute(self) -> ActionLoad:
        """
        Gera foco usando a lógica interna do Character e retorna um ActionLoad.
        """
        old_focus = self.actor.floating_focus
        # Lógica interna de gerar foco dentro de Character
        new_focus = self.actor.generate_focus()
        generated = new_focus - old_focus

        return ActionLoad(
            character=self.actor,
            history=[f"{self.actor.name} respirou fundo e gerou {generated} de Foco!"]
        )

class SkillNivelUm(BattleAction):
    def __init__(self, template: BattleActionTemplate, actor: 'Character', target: 'Character', battle_manager: 'BattleManager'):
        super().__init__(template=template, actor=actor, target=target, battle_manager=battle_manager)

    def can_execute(self) -> tuple[bool, str]:
        if self.actor.floating_focus < self.focus_cost:
            return False, "Foco insuficiente para usar esta habilidade!"
        return True, ""

    def execute(self) -> ActionLoad:
        
        # Consome o custo
        self.actor.spend_focus(self.focus_cost)
        
        # Callback para modificar o ataque. Consegue lembrar quem é "caster".)
        def add_damage_hook(attack_load: 'AttackLoad'):
            # Verificação de se o ataque é deste caster
            if attack_load.character.char_id == self.actor.char_id:
                attack_load.gda += 5 # Bônus de GdA
                attack_load.history.append(f"[SKILL] {self.name} aumentou o GdA em +5!")

        # Inscreve o callback
        self.battle_manager.subscribe('on_damage_calculation', add_damage_hook)
        
        basic_attack_template = self.battle_manager.data_service.get_action_template("basic_attack_template")

        # Executa o ataque
        ataque = BasicAttack(template = basic_attack_template, actor = self.actor, target=self.target, battle_manager=self.battle_manager, interaction_type=BattleInteractionType.SKILL)
        action_load = ataque.execute()
        
        # Desinscreve o callback
        self.battle_manager.unsubscribe('on_damage_calculation', add_damage_hook)

        return action_load

registry = {
    "BasicAttack": BasicAttack,
    "GenerateManaAction": GenerateManaAction,
    "GenerateFocusAction": GenerateFocusAction,
    "TemplateSkillN1": SkillNivelUm
}