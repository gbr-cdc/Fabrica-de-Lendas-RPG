from core.Models import Character, BattleManager, BattleAction, ActionLoad

class CharacterController:
    """
    Interface que define o 'Cérebro' de um personagem em combate.
    Pode ser implementada por um humano (PlayerController) ou por uma máquina (AIController).
    """
    
    def choose_action(self, caster: 'Character', battle_manager: 'BattleManager') -> 'BattleAction':
        """
        Chamado no início do turno do personagem.
        Deve analisar o campo de batalha, escolher uma habilidade, um alvo e retornar o Comando instanciado.
        """
        raise NotImplementedError("Ação de turno não implementada pelo Controller.")

    def choose_reaction(self, caster: 'Character', reaction_id: str, context: 'ActionLoad', battle_manager: 'BattleManager') -> bool:
        """
        Chamado no meio da resolução de ações quando uma habilidade condicional é engatilhada.
        O context (ActionLoad) permite que o Controller saiba o que está acontecendo (ex: quem está atacando, qual o dano atual).
        Retorna True se o personagem quiser ativar a reação, False caso contrário.
        """
        raise NotImplementedError("Reação não implementada pelo Controller.")

registry = {}