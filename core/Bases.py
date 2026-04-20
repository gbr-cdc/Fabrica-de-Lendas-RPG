from __future__ import annotations
from typing import TYPE_CHECKING, Protocol, Callable, List, Dict
from core.Events import ActionLoad

if TYPE_CHECKING:
    from entities.Characters import Character
    from combat.BattleManager import BattleManager
    from core.DiceManager import DiceManager
    from core.Structs import AttackActionTemplate
    from core.Enums import BattleActionType
    from controllers.CharacterController import CharacterController


# --- CLASSES BASE ---
class GameAction:
    """
    Representação geral de comandos que podem ser gerados por Controllers
    """
    def __init__(self, name: str, actor: 'Character'):
        self.name = name
        self.actor = actor

    def can_execute(self) -> tuple[bool, str]:
        """
        Valida se a ação pode ser usada
        """        
        raise NotImplementedError("Chamou can_execute() sem implementação.")

    def execute(self) -> ActionLoad:
        """
        Executa a lógica da ação
        """
        raise NotImplementedError("Chamou execute() sem implementação.")
    
    def execute_if_possible(self) -> ActionLoad:
        """
        Wrapper para chamar can_execute antes de execute.
        """
        can, msg = self.can_execute()
        if not can:
            return ActionLoad(character=self.actor, history=[msg], success=False)
        return self.execute()

class IBattleContext(Protocol):
    dice_service: 'DiceManager'
    
    def emit(self, event_name: str, payload: 'ActionLoad') -> None: ...
    def get_template(self, template_id: str) -> 'AttackActionTemplate': ...
    def delay_character(self, character: 'Character', extra_ticks: int) -> None: ...
    def subscribe(self, event_name: str, callback: Callable) -> None: ...
    def unsubscribe(self, event_name: str, callback: Callable) -> None: ...
    def get_characters(self) -> List[Character]: ...
    def get_controller(self, char_id: str) -> 'CharacterController': ...

class BattleAction(GameAction):
    """
    Comandos executados no contexto de batalha.
    """
    # Parâmetros relevantes recebidos através do construtor, de forma que os métodos não possuam parâmetros em conformidade com o Command Pattern
    def __init__(self, name: str, actor: 'Character', target: 'Character', context: 'IBattleContext', action_type: 'BattleActionType'):
        super().__init__(name=name, actor=actor)
        self.target = target
        self.context = context
        self.action_type = action_type

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
    
class BattlePassive:
    """
    Representa características estáticas ou passivas que não podem ser conjuradas.
    Elas apenas alteram regras do motor através do Event Bus.
    """
    def __init__(self, name: str, owner: 'Character', context: 'IBattleContext'):
        self.name = name
        self.owner = owner
        self.dice_service = context.dice_service
        self.context = context

    def get_hooks(self) -> Dict[str, Callable]:
        """Deve ser implementado pelas classes filhas para criar e inscrever os hooks."""
        raise NotImplementedError
