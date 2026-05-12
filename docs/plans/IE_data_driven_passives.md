# Implementation Plan: Data-Driven BattlePassives [IE_DATA_DRIVEN_PASSIVES]

The objective is to refactor the `BattlePassive` system to support data-driven parameters, allowing game balance values (thresholds, dice sizes, modifiers) to be managed via JSON configurations instead of being hardcoded in Python classes.

## User Requirements
- Passives parameters must be changeable via data files.
- Tests should not break when these values change (by using the same data files).
- Standardize the way passives access their configuration.

## Proposed Changes

### 1. Core Data Structures [ARCH.RULES.CORE.DATA]
- Add `BattlePassiveTemplate` to `core/Structs.py`.
- This template will hold a name, an ID, and a dictionary of parameters.

### 2. Data Management [ARCH.RULES.CORE.DATA]
- Update `DataManager.py` to:
    - Load `data/BattlePassives.json`.
    - Provide access to these templates.

### 3. Base Classes [ARCH.RULES.CORE.IOC]
- Update `BattlePassive` in `core/BaseClasses.py` to accept an optional `BattlePassiveTemplate` in its constructor.

### 4. Battle Engine Integration [ARCH.RULES.BATTLE.PASSIVE_HOOKS]
- Update `BattleManager.py` to fetch the appropriate `BattlePassiveTemplate` when instantiating passives for characters.

### 5. Concrete Passives Refactoring [ARCH.RULES.CORE.OBSERVER]
- Refactor all classes in `battle/BattlePassives.py` to:
    - Use values from `self.template.parameters` instead of hardcoded constants.
    - Ensure default values are provided if parameters are missing to maintain robustness.

### 6. Data Definition
- Create `data/BattlePassives.json` with the current balance values for all existing passives.

### 7. Testing [ARCH.TEST_QUALITY]
- Update tests to ensure they remain valid regardless of the specific values in the JSON.

## Detailed Steps

### Step 1: Update `core/Structs.py`
Add the `BattlePassiveTemplate` dataclass.

### Step 2: Update `core/BaseClasses.py`
Modify `BattlePassive.__init__` to store the `template`.

### Step 3: Create `data/BattlePassives.json`
Define parameters for all existing passives.

### Step 4: Update `core/DataManager.py`
Add `load_battle_passives` and `get_passive_template`.

### Step 5: Update `battle/BattleManager.py`
Ensure `BattleManager` uses `DataManager` to get templates when creating passives.

### Step 6: Refactor `battle/BattlePassives.py`
Update all classes to use `self.template.parameters`.

### Step 7: Validation
Run `pytest` to ensure no regressions.

## Alternatives Considered
- **Direct Parameter injection**: Passing individual arguments to constructors.
    - *Cons*: Less flexible than a template.
- **Global Config Object**: A single object with all values.
    - *Cons*: Less encapsulated.

## Verification Plan
1.  **Manual Verification**: Change a value in `BattlePassives.json` and verify behavior.
2.  **Automated Testing**: Run existing integration tests.
