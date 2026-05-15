from __future__ import annotations
from typing import Dict, Any
import copy
from entities.Characters import Character
from battle.BattleManager import BattleManager
from core.CharacterSystem import CharacterSystem
from core.DiceManager import DiceManager
from core.DataManager import DataManager
from battle.Judges import BattleJudge
from core.Structs import BattleResult

CHARACTERS_FILE = "data/Characters.json"
COMBAT_STYLES_FILE = "data/CombatStyles.json"
RULES_FILE = "data/Rules.json"
BATTLE_PASSIVES_FILE = "data/BattlePassives.json"
ATTACK_ACTIONS_FILE = "data/AttackActions.json"
AI_BEHAVIORS_FILE = "data/ai_behaviors.json"

class PvPSimulator:
    def __init__(self, dice_manager: DiceManager, data_manager: DataManager, judge: BattleJudge, character1: Character, character2: Character):
        self.dice_manager = dice_manager
        self.data_manager = data_manager
        self.judge = judge
        self.character1 = character1
        self.character2 = character2

    @classmethod
    def from_data_files(
        cls,
        characters_filepath: str,
        combat_styles_filepath: str,
        rules_filepath: str,
        char1_id: str,
        char2_id: str,
        dice_seed: int | None = None
    ) -> "PvPSimulator":
        """
        Factory method to create a PvPSimulator from data files.
        """
        dm = DataManager()
        dm.load_game_rules(rules_filepath)
        dm.load_combat_styles(combat_styles_filepath)
        dm.load_action_templates(ATTACK_ACTIONS_FILE)
        dm.load_passive_templates(BATTLE_PASSIVES_FILE)
        dm.load_ai_behaviors(AI_BEHAVIORS_FILE)
        dm.load_characters(characters_filepath)

        char1 = dm.get_character(char1_id)
        char2 = dm.get_character(char2_id)
        
        # In PvP 1v1, we assign teams 1 and 2
        char1.team = 1
        char2.team = 2

        return cls(
            dice_manager=DiceManager(seed=dice_seed),
            data_manager=dm,
            judge=BattleJudge(),
            character1=char1,
            character2=char2
        )

    def _setup_battle(self, c1: Character, c2: Character) -> BattleManager:
        bm = BattleManager(self.dice_manager, self.data_manager, self.judge)
        bm.add_character(c1, start_tick=c1.action_cost_base)
        bm.add_character(c2, start_tick=c2.action_cost_base)
        return bm

    def run_simulation(self) -> BattleResult:
        """
        Runs a single battle simulation and returns the result.
        """
        c1 = copy.deepcopy(self.character1)
        c2 = copy.deepcopy(self.character2)
        
        bm = self._setup_battle(c1, c2)
        bm.run_battle()
        
        return bm.battle_result

def simulate_multiple_battles(
    num_simulations: int,
    char1_id: str,
    char2_id: str,
    characters_filepath: str = CHARACTERS_FILE,
    combat_styles_filepath: str = COMBAT_STYLES_FILE,
    rules_filepath: str = RULES_FILE,
) -> list[BattleResult]:
    """
    Simulates multiple battles and returns a list of BattleResult objects.
    """
    dm = DataManager()
    dm.load_game_rules(rules_filepath)
    dm.load_combat_styles(combat_styles_filepath)
    dm.load_action_templates(ATTACK_ACTIONS_FILE)
    dm.load_passive_templates(BATTLE_PASSIVES_FILE)
    dm.load_ai_behaviors(AI_BEHAVIORS_FILE)
    dm.load_characters(characters_filepath)
    
    char1_template = dm.get_character(char1_id)
    char2_template = dm.get_character(char2_id)
    char1_template.team = 1
    char2_template.team = 2

    results = []

    for _ in range(num_simulations):
        simulator = PvPSimulator(
            dice_manager=DiceManager(),
            data_manager=dm,
            judge=BattleJudge(),
            character1=char1_template,
            character2=char2_template
        )

        results.append(simulator.run_simulation())

    return results

# Interface functions for Main.py
def multy(char1_id: str, char2_id: str):
    from views.BattleView import BattleView
    results = simulate_multiple_battles(10000, char1_id, char2_id)
    view = BattleView()
    view.present_summary(results, char1_id, char2_id)


def mono(char1_id: str, char2_id: str):
    from views.BattleView import BattleView
    simulator = PvPSimulator.from_data_files(
        CHARACTERS_FILE,
        COMBAT_STYLES_FILE,
        RULES_FILE,
        char1_id,
        char2_id
    )
    result = simulator.run_simulation()
    view = BattleView()
    view.present_battle(result)
