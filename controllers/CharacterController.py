from core.Events import ActionLoad
from entities.Characters import Character
from battle.BattleActions import BattleAction
from core.BaseClasses import IBattleContext

class CharacterController:
    """
    Interface que define o 'Cérebro' de um personagem em combate.
    Pode ser implementada por um humano (PlayerController) ou por uma máquina (AIController).
    """
    
    def choose_action(self, actor: 'Character', context: 'IBattleContext', action_load: 'ActionLoad|None' = None) -> 'BattleAction':
        """
        Chamado no início do turno do personagem.
        Deve analisar o campo de batalha, escolher uma habilidade, um alvo e retornar o Comando instanciado.
        """
        raise NotImplementedError("Ação de turno não implementada pelo Controller.")

    def choose_reaction(self, actor: 'Character', reaction_id: str, action_load: 'ActionLoad', context: 'IBattleContext') -> bool:
        """
        Chamado no meio da resolução de ações quando uma habilidade condicional é engatilhada.
        O context (ActionLoad) permite que o Controller saiba o que está acontecendo (ex: quem está atacando, qual o dano atual).
        Retorna True se o personagem quiser ativar a reação, False caso contrário.
        """
        raise NotImplementedError("Reação não implementada pelo Controller.")

class PvP1v1Controller(CharacterController):

    def choose_action(self, actor: 'Character', context: 'IBattleContext', action_load: 'ActionLoad|None' = None) -> 'BattleAction':
        target = None
        for character in context.get_characters():
            if character is not actor:
                target = character
                break
        
        if target is None:
            raise RuntimeError(f"Controller de {actor} não conseguiu achar um alvo")
        
        if action_load is not None:
            from battle.BattleActions import registry as actions_registry
            basic_attack_template = context.get_template("BasicAttack")
            return actions_registry["AttackAction"](basic_attack_template, actor, target, context)

        skill_template = context.get_template("SkillN1")
        cost = skill_template.focus_cost
        if actor.floating_focus >= cost:
            from battle.BattleActions import registry as actions_registry
            return actions_registry["AttackAction"](skill_template, actor, target, context)
            
        from battle.BattleActions import registry as actions_registry
        basic_attack_template = context.get_template("BasicAttack")
        return actions_registry["AttackAction"](basic_attack_template, actor, target, context)
    
    def choose_reaction(self, actor: 'Character', reaction_id: str, action_load: 'ActionLoad', context: 'IBattleContext') -> bool:
        return True


registry = {"1v1Controller": PvP1v1Controller}