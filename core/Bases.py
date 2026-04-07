from entities.Characters import Character
from core.Events import ActionLoad

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
