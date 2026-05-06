# Plan: MVC Refactor for Simulator and BattleView

## Objective
Refactor `pvp_simulator/Simulator.py` and `views/BattleView.py` to strictly adhere to the MVC pattern. The simulator (Controller) will handle logic and data orchestration, while the view (View) will handle all output presentation.

## Proposed Changes

### 1. View Layer: `views/BattleView.py`
- Convert `BattleView` into a more robust class.
- Add `present_battle(result: BattleResult)`:
    - Responsible for parsing history tags and printing the battle narrative.
    - Handles the "Battle Over" summary printing.
- Add `present_summary(results: List[BattleResult], char1_id: str, char2_id: str)`:
    - Calculates statistics (win rate, average turns, etc.) from a list of `BattleResult` objects.
    - Prints the multi-battle summary.
- Encapsulate the tag parsing logic into a private method `_parse_entry(entry: str)`.

### 2. Controller Layer: `pvp_simulator/Simulator.py`
- Refactor `PvPSimulator` methods:
    - `run_simulation()`: Run a battle and return the `BattleResult` object.
    - Remove `single_battle_verbose` and `single_battle_summary` in favor of a single execution method that returns data.
- Refactor `simulate_multiple_battles()`:
    - Return a list of `BattleResult` objects instead of a pre-calculated dictionary.
- Refactor interface functions `mono()` and `multy()`:
    - Instantiante `BattleView`.
    - Call the simulator to get data.
    - Pass the data to the view for presentation.
    - Remove all `print()` calls from these functions.

### 3. Model Alignment
- Ensure `BattleManager` or `Simulator` correctly populates `BattleResult` (winners, losers, etc.) so the View has all the information it needs without having to recalculate it from history if possible.

## Architectural Justification
- **MVC [ARCH.RULES.CORE.MVC]:** Clearly separates simulation logic (Controller) from string formatting and printing (View).
- **Event Stream History [ARCH.RULES.CORE.HISTORY]:** View remains the only layer responsible for narrative strings.

## Steps
1. Modify `views/BattleView.py` to implement the new methods.
2. Modify `pvp_simulator/Simulator.py` to remove prints and return raw data.
3. Update `Main.py` if necessary (though it seems `mono` and `multy` are the main entry points).
