from typing import Dict, Any
import copy
from entities.Characters import Character
from combat.BattleManager import BattleManager
from core.CharacterSystem import CharacterSystem
from controllers.CharacterController import PvP1v1Controller
from core.DiceManager import DiceManager
from core.DataManager import DataManager
from combat.Judges import BattleJudge

CHARACTERS_FILE = "data/Characters.json"
COMBAT_STYLES_FILE = "data/CombatStyles.json"
RULES_FILE = "data/Rules.json"
ATTACK_ACTIONS_FILE = "data/AttackActions.json"

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
        bm.add_character(c1, PvP1v1Controller(), start_tick=c1.action_cost_base)
        bm.add_character(c2, PvP1v1Controller(), start_tick=c2.action_cost_base)
        return bm

    def single_battle_verbose(self):
        """ 
        Simulates a battle and returns detailed history.
        """
        c1 = copy.deepcopy(self.character1)
        c2 = copy.deepcopy(self.character2)
        
        bm = self._setup_battle(c1, c2)
        bm.run_battle()
        
        result = bm.battle_result
        winner_name = c1.name if CharacterSystem.is_alive(c1) else c2.name
        
        # Add a final line to match previous output style
        history = list(result.history)
        history.append(f"\n{'='*50}")
        history.append(f"Batalha terminada! {c1.name}: {c1.current_hp}HP | {c2.name}: {c2.current_hp}HP")

        return {
            "winner": winner_name,
            "turns": result.duration,
            "final_hp": {
                c1.name: c1.current_hp,
                c2.name: c2.current_hp
            },
            "history": history
        }

    def single_battle_summary(self):
        """ 
        Simulates a battle and returns only the final result.
        """
        c1 = copy.deepcopy(self.character1)
        c2 = copy.deepcopy(self.character2)
        
        bm = self._setup_battle(c1, c2)
        bm.run_battle()
        
        result = bm.battle_result
        winner_name = c1.name if CharacterSystem.is_alive(c1) else c2.name
        
        return {
            "winner": winner_name,
            "turns": result.duration,
            "final_hp": {
                c1.name: c1.current_hp,
                c2.name: c2.current_hp
            }
        }

def simulate_multiple_battles(
    num_simulations: int,
    char1_id: str,
    char2_id: str,
    characters_filepath: str = CHARACTERS_FILE,
    combat_styles_filepath: str = COMBAT_STYLES_FILE,
    rules_filepath: str = RULES_FILE,
) -> Dict[str, Any]:
    """
    Simulates multiple battles and returns aggregated statistics.
    """
    dm = DataManager()
    dm.load_game_rules(rules_filepath)
    dm.load_combat_styles(combat_styles_filepath)
    dm.load_action_templates(ATTACK_ACTIONS_FILE)
    dm.load_characters(characters_filepath)
    
    char1_template = dm.get_character(char1_id)
    char2_template = dm.get_character(char2_id)
    char1_template.team = 1
    char2_template.team = 2

    results = {
        char1_id: 0,
        char2_id: 0,
        "draws": 0,
        "total_turns": 0,
        "average_turns": 0.0
    }

    turns_list = []

    for _ in range(num_simulations):
        simulator = PvPSimulator(
            dice_manager=DiceManager(),
            data_manager=dm,
            judge=BattleJudge(),
            character1=char1_template,
            character2=char2_template
        )

        summary = simulator.single_battle_summary()
        winner = summary["winner"]
        turns = summary["turns"]
        
        turns_list.append(turns)

        if winner == char1_template.name:
            results[char1_id] += 1
        elif winner == char2_template.name:
            results[char2_id] += 1
        else:
            results["draws"] += 1

    results["total_turns"] = sum(turns_list)
    results["average_turns"] = sum(turns_list) / len(turns_list) if turns_list else 0.0

    return results

# Interface functions for Main.py
def multy(char1_id: str, char2_id: str):
    results = simulate_multiple_battles(10000, char1_id, char2_id)

    print("Resultados das 10000 batalhas:")
    print(f"{char1_id}: {results[char1_id]} vitórias")
    print(f"{char2_id}: {results[char2_id]} vitórias")
    print(f"Empates: {results['draws']}")
    print(f"Total de turnos: {results['total_turns']}")
    print(f"Média de turnos por batalha: {results['average_turns']:.2f}")


def mono(char1_id: str, char2_id: str):
    simulator = PvPSimulator.from_data_files(
        CHARACTERS_FILE,
        COMBAT_STYLES_FILE,
        RULES_FILE,
        char1_id,
        char2_id
    )
    result = simulator.single_battle_verbose()
    for line in result["history"]:
        print(line)
