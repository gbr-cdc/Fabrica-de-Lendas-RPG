from __future__ import annotations
from typing import TYPE_CHECKING, Protocol, Callable, List, Dict
from core.Events import ActionLoad

if TYPE_CHECKING:
    from entities.Characters import Character
    from battle.BattleManager import BattleManager
    from core.DiceManager import DiceManager
    from core.Enums import BattleActionType, BattleState
    from core.Structs import AttackActionTemplate, BattleResult
    from controllers.CharacterController import CharacterController
    from core.Modifiers import EphemeralModifier


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

class IDiceContext(Protocol):
    @property
    def dice_service(self) -> 'DiceManager': ...

class IEventContext(Protocol):
    def emit(self, event_name: str, payload: 'ActionLoad') -> None: ...

class IEffectContext(Protocol):
    def get_active_passive(self, char_id: str, name: str) -> 'BattlePassive' | None: ...
    def add_status_effect(self, effect: 'StatusEffect') -> None: ...
    def remove_status_effect(self, effect: 'StatusEffect') -> None: ...

class ITimelineContext(Protocol):
    def delay_character(self, character: 'Character', extra_ticks: int) -> None: ...
    def set_tick(self, character: 'Character', tick: int) -> None: ...

class IRegistryContext(Protocol):
    def get_characters(self) -> List['Character']: ...
    def get_graveyard(self) -> List['Character']: ...
    def get_controller(self, char_id: str) -> 'CharacterController': ...

class IDataContext(Protocol):
    def get_template(self, template_id: str) -> 'AttackActionTemplate': ...

class IPassiveContext(IEventContext, IEffectContext, ITimelineContext, IRegistryContext, IDiceContext, Protocol): ...

class IActionContext(IEventContext, IEffectContext, IDiceContext, Protocol): ...

class IControllerContext(IRegistryContext, ITimelineContext, IDataContext, Protocol): ...

class IJudgeContext(IRegistryContext, ITimelineContext, Protocol): ...

class IBattleContext(IEventContext, IEffectContext, ITimelineContext, IRegistryContext, IDiceContext, IDataContext, Protocol): ...

class IBattleJudge(Protocol):
    def rule(self, context: 'IJudgeContext', result: 'BattleResult') -> 'BattleState': ...

class BattleAction(GameAction):
    """
    Comandos executados no contexto de batalha.
    """
    # Parâmetros relevantes recebidos através do construtor, de forma que os métodos não possuam parâmetros em conformidade com o Command Pattern
    def __init__(self, name: str, actor: 'Character', targets: List['Character'], context: 'IActionContext', action_type: 'BattleActionType'):
        super().__init__(name=name, actor=actor)
        self.targets = targets
        self.context = context
        self.action_type = action_type

    @property
    def target(self) -> 'Character' | None:
        return self.targets[0] if self.targets else None

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
    def __init__(self, name: str, owner: 'Character', context: 'IPassiveContext'):
        self.name = name
        self.owner = owner
        self.dice_service = context.dice_service
        self.context = context

    def get_hooks(self) -> Dict[str, Callable]:
        """Deve ser implementado pelas classes filhas para criar e inscrever os hooks."""
        raise NotImplementedError

    def apply(self):
        """Chamado quando a passiva entra em jogo (ex: início da batalha)."""
        pass

    def remove(self):
        """Chamado quando a passiva sai de jogo."""
        pass

class StatusEffect(BattlePassive):
    """ 
    Representa um efeito de status aplicado a um personagem, com duração em turnos.
    Pode ser usado para coisas como Atordoado, Envenenado, etc. 
    """
    def __init__(self, name: str, duration: int, target: 'Character', context: 'IPassiveContext'):
        super().__init__(name=name, owner=target, context=context)
        self.name = name
        self.duration = duration
        self.character = target
        self.context = context
        self.modifiers: list['EphemeralModifier'] = []
    
    def apply(self):
        """Aplica o efeito. Deve ser sobrescrito por subclasses."""
        raise NotImplementedError("StatusEffect deve implementar apply()")
    
    def remove(self):
        """Remove o efeito e limpa seus modificadores."""
        for mod in list(self.modifiers):
            self._remove_modifier(mod)
        self.modifiers.clear()
        self.context.remove_status_effect(self)

    def _add_modifier(self, modifier: 'EphemeralModifier'):
        """Adiciona um modificador tanto ao efeito quanto ao personagem dono."""
        self.modifiers.append(modifier)
        self.owner.add_modifier(modifier)

    def _remove_modifier(self, modifier: 'EphemeralModifier'):
        """Remove um modificador tanto do efeito quanto do personagem dono."""
        if modifier in self.modifiers:
            self.modifiers.remove(modifier)
        self.owner.remove_modifier(modifier)
