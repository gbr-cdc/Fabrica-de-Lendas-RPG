# Implementation Plan - PvP Simulator Refactor

The `pvp_simulator` module is currently outdated and duplicates logic already implemented in the core `BattleManager`. This refactor aims to delegate the execution of combat to the `BattleManager.run_battle()` method, ensuring architectural consistency and reducing maintenance overhead.

## User Review Required

> [!IMPORTANT]
> The current `BattleManager` requires a `BattleJudge` and a `DataManager`. I will update the `PvPSimulator` to initialize these components properly.
> The `PvP1v1Controller` is already available and will be used to maintain the current simulator behavior.

- Are there any specific simulator-only rules that should be preserved outside of the standard `BattleManager` flow?
- Should the simulator support more than 2 characters in the future? (The current implementation is 1v1).

## Proposed Changes

### `pvp_simulator/Simulator.py`

#### 1. Modernize Initialization
- Update `PvPSimulator.__init__` to accept a fully configured `BattleManager`.
- Update `from_data_files` factory method to:
    - Instantiate `DataManager`.
    - Load rules, styles, and characters using the `DataManager` instance.
    - Instantiate `BattleJudge`.
    - Instantiate `BattleManager` with `DiceManager`, `DataManager`, and `BattleJudge`.

#### 2. Delegate Combat Execution
- Refactor `single_battle_verbose` and `single_battle_summary` to:
    - Clear the `BattleManager` state if reused (or better, use a fresh one).
    - Add characters to `BattleManager` with `PvP1v1Controller`.
    - Call `battle_manager.run_battle()`.
    - Retrieve results from `battle_manager.battle_result`.

#### 3. Standardize Results
- Map `BattleResult` attributes to the simulator's return format to maintain compatibility with `simulate_multiple_battles` and `Main.py`.

## Constraints & Rules
- **MVC Compliance**: Ensure `PvPSimulator` acts as a utility/service that orchestrates the Model (core components).
- **Anemic Entities**: Interact with characters only through `CharacterSystem` or `BattleManager`.
- **TDD**: Validate the refactored simulator against existing test cases or create a new test suite for it.

## Verification Plan

### Automated Tests
- Run `pytest tests/pvp_simulator/test_Simulator.py` (if it exists) or create a smoke test.
- Verify that `simulate_multiple_battles` still produces statistical results.

### Manual Verification
- Run `pvp_simulator/Simulator.py` directly (if it has a `__main__`) or through `Main.py` to check the output formatting.
