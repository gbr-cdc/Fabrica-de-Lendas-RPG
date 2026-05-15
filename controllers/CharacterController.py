from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.Events import ActionLoad
    from entities.Characters import Character
    from battle.BattleActions import BattleAction
    from core.BaseClasses import IControllerContext, IDataContext
    from core.Structs import AIBehavior

def filter_hp_lt(targets: list['Character'], actor: 'Character', context: 'IControllerContext', f: str) -> list['Character']:
    pct = int(f.split("_")[2])
    return [c for c in targets if (c.current_hp / max(1, c.max_hp)) * 100 < pct]

def filter_lowest_hp(targets: list['Character'], actor: 'Character', context: 'IControllerContext', f: str) -> list['Character']:
    if targets:
        lowest = min(targets, key=lambda c: c.current_hp)
        return [lowest]
    return targets

def filter_highest_hp(targets: list['Character'], actor: 'Character', context: 'IControllerContext', f: str) -> list['Character']:
    if targets:
        highest = max(targets, key=lambda c: c.current_hp)
        return [highest]
    return targets

def filter_is_dead(targets: list['Character'], actor: 'Character', context: 'IControllerContext', f: str) -> list['Character']:
    from core.CharacterSystem import CharacterSystem
    return [c for c in targets if not CharacterSystem.is_alive(c)]

def filter_highest_threat(targets: list['Character'], actor: 'Character', context: 'IControllerContext', f: str) -> list['Character']:
    if targets:
        threat = max(targets, key=lambda c: getattr(c, 'pda', 0) + getattr(c, 'mda', 0))
        return [threat]
    return targets

filters_registry = {
    "hp_lt_": filter_hp_lt,
    "lowest_hp": filter_lowest_hp,
    "highest_hp": filter_highest_hp,
    "is_dead": filter_is_dead,
    "highest_threat": filter_highest_threat
}

class CharacterController:
    """
    Interface que define o 'Cérebro' de um personagem em combate.
    Pode ser implementada por um humano (PlayerController) ou por uma máquina (AIController).
    """
    
    def choose_action(self, actor: Character, context: IControllerContext) -> BattleAction:
        """
        Chamado no início do turno do personagem.
        Deve analisar o campo de batalha, escolher uma habilidade, um alvo e retornar o Comando instanciado.
        """
        raise NotImplementedError("Ação de turno não implementada pelo Controller.")

    def choose_reaction(self, actor: Character, reaction_id: str, action_load: ActionLoad, context: IControllerContext) -> bool:
        """
        Chamado no meio da resolução de ações quando uma habilidade condicional é engatilhada.
        O context (ActionLoad) permite que o Controller saiba o que está acontecendo (ex: quem está atacando, qual o dano atual).
        Retorna True se o personagem quiser ativar a reação, False caso contrário.
        """
        raise NotImplementedError("Reação não implementada pelo Controller.")


class AIPriorityController(CharacterController):
    def __init__(self, behavior: AIBehavior, data_context: IDataContext):
        self.behavior = behavior
        self.current_state = behavior.initial_state
        self.data_context = data_context

    def _get_targets(self, actor: Character, context: IControllerContext, selector: str, filters: list[str]) -> list[Character]:
        from core.CharacterSystem import CharacterSystem
        all_chars = context.get_characters()
        
        if selector == "self":
            targets = [actor]
        elif selector in ("any_ally", "all_ally"):
            targets = [c for c in all_chars if getattr(c, 'team', 0) == getattr(actor, 'team', 0) and c != actor]
        elif selector in ("any_enemy", "all_enemy"):
            targets = [c for c in all_chars if getattr(c, 'team', 0) != getattr(actor, 'team', 0)]
        elif selector in ("anyone", "everyone"):
            targets = [c for c in all_chars if c != actor]
        else:
            targets = []

        for f in filters:
            for prefix, func in filters_registry.items():
                if f.startswith(prefix):
                    targets = func(targets, actor, context, f)
                    break

        if "is_dead" not in filters:
            targets = [c for c in targets if CharacterSystem.is_alive(c)]

        if selector in ("any_ally", "any_enemy", "anyone") and targets:
            return [targets[0]]
        
        return targets

    def choose_action(self, actor: Character, context: IControllerContext) -> BattleAction:
        max_attempts = 10
        attempts = 0
        
        while attempts < max_attempts:
            attempts += 1
            valid_nodes = [n for n in self.behavior.nodes if n.required_state in (self.current_state, "any")]
            valid_nodes.sort(key=lambda x: x.priority, reverse=True)
            
            for node in valid_nodes:
                targets = self._get_targets(actor, context, node.target_selector, node.filters)
                if not targets:
                    continue
                
                action = None
                if node.action_id:
                    from battle.BattleActions import AttackAction
                    from battle.BattleActions import registry as action_registry
                    
                    if node.action_id == "Attack":
                        action = AttackAction(None, actor, targets, context)
                    elif node.action_id in self.data_context.list_action_templates():
                        template = self.data_context.get_action_template(node.action_id)
                        action = AttackAction(template, actor, targets, context)
                    elif node.action_id in action_registry:
                        action_class = action_registry[node.action_id]
                        action = action_class(actor, targets, context)

                if node.next_state:
                    self.current_state = node.next_state

                if action:
                    can_exec, _ = action.can_execute()
                    if can_exec:
                        return action
                    else:
                        continue
                else:
                    break
            else:
                break

        from battle.BattleActions import WaitAction
        return WaitAction(actor, [], context)

    def choose_reaction(self, actor: Character, reaction_id: str, action_load: ActionLoad, context: IControllerContext) -> bool:
        return True

registry = {"AIPriorityController": AIPriorityController}