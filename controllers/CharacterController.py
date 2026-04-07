from core.Events import ActionLoad
from entities.Characters import Character
from combat.BattleActions import BattleAction
from combat.BattleManager import BattleManager

class CharacterController:
    """
    Interface que define o 'Cérebro' de um personagem em combate.
    Pode ser implementada por um humano (PlayerController) ou por uma máquina (AIController).
    """
    
    def choose_action(self, actor: 'Character', battle_manager: 'BattleManager', action_load: 'ActionLoad|None' = None) -> 'BattleAction':
        """
        Chamado no início do turno do personagem.
        Deve analisar o campo de batalha, escolher uma habilidade, um alvo e retornar o Comando instanciado.
        """
        raise NotImplementedError("Ação de turno não implementada pelo Controller.")

    def choose_reaction(self, actor: 'Character', reaction_id: str, context: 'ActionLoad', battle_manager: 'BattleManager') -> bool:
        """
        Chamado no meio da resolução de ações quando uma habilidade condicional é engatilhada.
        O context (ActionLoad) permite que o Controller saiba o que está acontecendo (ex: quem está atacando, qual o dano atual).
        Retorna True se o personagem quiser ativar a reação, False caso contrário.
        """
        raise NotImplementedError("Reação não implementada pelo Controller.")

class PvP1v1Controller(CharacterController):

    def choose_action(self, actor: 'Character', battle_manager: 'BattleManager', action_load: 'ActionLoad|None' = None) -> 'BattleAction':
        target = None
        for key, character in battle_manager.characters.items():
            if character is not actor:
                target = character
                break
        
        if target is None:
            raise RuntimeError(f"Controller de {actor} não conseguiu achar um alvo")
        
        if action_load is not None:
            basic_attack_template = battle_manager.data_service.get_action_template("BasicAttack")
            return basic_attack_template.command(basic_attack_template, actor, target, battle_manager)

        skill_template = battle_manager.data_service.get_action_template("TemplateSkillN1")
        cost = skill_template.focus_cost
        if actor.floating_focus >= cost:
            return skill_template.command(skill_template, actor, target, battle_manager)
        basic_attack_template = battle_manager.data_service.get_action_template("BasicAttack")
        return basic_attack_template.command(basic_attack_template, actor, target, battle_manager)
    
    def choose_reaction(self, actor: 'Character', reaction_id: str, context: 'ActionLoad', battle_manager: 'BattleManager') -> bool:
        return True


registry = {"1v1Controller": PvP1v1Controller}