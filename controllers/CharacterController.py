from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.Events import ActionLoad
    from entities.Characters import Character
    from battle.BattleActions import BattleAction
    from core.BaseClasses import IControllerContext
    from core.Structs import AIBehavior

class CharacterController:
    """
    Interface que define o 'Cérebro' de um personagem em combate.
    Pode ser implementada por um humano (PlayerController) ou por uma máquina (AIController).
    """
    
    def choose_action(self, actor: Character, context: IControllerContext, action_load: ActionLoad | None = None) -> BattleAction:
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

class PvP1v1Controller(CharacterController):

    def choose_action(self, actor: Character, context: IControllerContext, action_load: ActionLoad | None = None) -> BattleAction:
        target = None
        for character in context.get_characters():
            if character is not actor:
                target = character
                break
        
        if target is None:
            raise RuntimeError(f"Controller de {actor} não conseguiu achar um alvo")
        
        if action_load is not None:
            from battle.BattleActions import AttackAction
            return AttackAction(None, actor, [target], context)

        skill_template = context.get_template("SkillN1")
        cost = skill_template.focus_cost
        if actor.floating_focus >= cost:
            from battle.BattleActions import AttackAction
            return AttackAction(skill_template, actor, [target], context)
            
        from battle.BattleActions import AttackAction
        return AttackAction(None, actor, [target], context)
    
    def choose_reaction(self, actor: Character, reaction_id: str, action_load: ActionLoad, context: IControllerContext) -> bool:
        return True

class AIPriorityController(CharacterController):
    def __init__(self, behavior: AIBehavior):
        self.behavior = behavior
        self.current_state = behavior.initial_state

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
            if f.startswith("hp_lt_"):
                pct = int(f.split("_")[2])
                targets = [c for c in targets if (c.current_hp / max(1, c.max_hp)) * 100 < pct]
            elif f == "lowest_hp":
                if targets:
                    lowest = min(targets, key=lambda c: c.current_hp)
                    targets = [lowest]
            elif f == "is_dead":
                targets = [c for c in targets if not CharacterSystem.is_alive(c)]

        if "is_dead" not in filters:
            targets = [c for c in targets if CharacterSystem.is_alive(c)]

        if selector in ("any_ally", "any_enemy", "anyone") and targets:
            return [targets[0]]
        
        return targets

    def choose_action(self, actor: Character, context: IControllerContext, action_load: ActionLoad | None = None) -> BattleAction:
        if action_load is not None:
            from battle.BattleActions import AttackAction
            return AttackAction(None, actor, [], context)

        max_attempts = 10
        attempts = 0
        
        while attempts < max_attempts:
            attempts += 1
            valid_nodes = [n for n in self.behavior.nodes if n.required_state in (self.current_state, "any")]
            valid_nodes.sort(key=lambda x: x.priority, reverse=True)
            
            for node in valid_nodes:
                targets = self._get_targets(actor, context, node.target_selector, node.filters)
                if not targets and node.target_selector != "self" and "any" not in node.target_selector and "all" not in node.target_selector and node.target_selector not in ("anyone", "everyone"):
                    pass
                if not targets and node.target_selector != "self":
                    continue
                
                action = None
                if node.action_id:
                    if node.action_id == "WaitAction":
                        from battle.BattleActions import WaitAction
                        action = WaitAction(actor, context)
                    elif node.action_id == "GenerateFocus":
                        from battle.BattleActions import GenerateFocusAction
                        action = GenerateFocusAction(actor, targets, context)
                    else:
                        from battle.BattleActions import AttackAction
                        template = context.get_template(node.action_id) if hasattr(context, 'get_template') else None
                        action = AttackAction(template, actor, targets, context)

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
        return WaitAction(actor, context)

    def choose_reaction(self, actor: Character, reaction_id: str, action_load: ActionLoad, context: IControllerContext) -> bool:
        return True

registry = {"1v1Controller": PvP1v1Controller, "AIPriorityController": AIPriorityController}