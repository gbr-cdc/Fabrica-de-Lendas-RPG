from typing import List, Callable, Dict
from core.BaseClasses import IBattleContext
from core.DiceManager import DiceManager
from core.Events import ActionLoad
from core.Structs import AttackActionTemplate, AttackEffects
from core.Enums import BattleActionType, AttackType
from entities.Characters import Character

class BattleTestContext(IBattleContext):
    def __init__(self, characters: List[Character] = None):
        self.dice_service = DiceManager(seed=42)
        self._characters = characters or []
        self._templates = {}
        self.emitted_events = []
        self.subscriptions = {}
        self.controllers = {}

    def emit(self, event_name: str, payload: ActionLoad) -> None:
        self.emitted_events.append((event_name, payload))
        if event_name in self.subscriptions:
            for callback in self.subscriptions[event_name]:
                callback(payload)

    def get_template(self, template_id: str) -> AttackActionTemplate:
        if template_id in self._templates:
            return self._templates[template_id]
        
        # Default templates for testing if not provided
        if template_id == "BasicAttack":
            return AttackActionTemplate(
                id="BasicAttack", nome="Ataque Básico", 
                action_type=BattleActionType.STANDARD_ACTION, 
                attack_type=AttackType.BASIC_ATTACK, 
                focus_cost=0, effects=[]
            )
        if template_id == "SkillN1":
            return AttackActionTemplate(
                id="SkillN1", nome="Habilidade N1", 
                action_type=BattleActionType.STANDARD_ACTION, 
                attack_type=AttackType.BASIC_ATTACK, 
                focus_cost=5, effects=[]
            )
        
        raise ValueError(f"Template {template_id} not found in TestContext")

    def delay_character(self, character: Character, extra_ticks: int) -> None:
        pass

    def subscribe(self, event_name: str, callback: Callable) -> None:
        if event_name not in self.subscriptions:
            self.subscriptions[event_name] = []
        self.subscriptions[event_name].append(callback)

    def unsubscribe(self, event_name: str, callback: Callable) -> None:
        if event_name in self.subscriptions:
            self.subscriptions[event_name].remove(callback)

    def get_characters(self) -> List[Character]:
        return self._characters

    def get_controller(self, char_id: str):
        return self.controllers.get(char_id)

    def get_active_passive(self, char_id: str, name: str):
        return None

    def add_template(self, template: AttackActionTemplate):
        self._templates[template.id] = template

    def add_character(self, character: Character):
        self._characters.append(character)
