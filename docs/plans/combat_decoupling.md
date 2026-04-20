# Implementation Plan: Combat Logic Decoupling

## Rationale
The current combat engine (`Judges.py` and `BattleActions.py`) incorrectly assumes that the `Character` entity provides domain logic (like lifecycle checks and resource management). This violates **Rule 1.13 (Anemic Entities)**, which dictates that logic should reside in external systems.

## Proposed Technical Path
We will refactor the calling code to delegate all character-related logic to the `CharacterSystem`.

### 1. Character Entity (`entities/Characters.py`)
- **Add `team: int = 0`**: We will add `team` as a pure data field to the `Character` constructor. This does not violate Rule 1.13 as it is state, not behavior.

### 2. Refactor Callers
- **`combat/Judges.py`**:
    - Import `CharacterSystem`.
    - Replace `character.is_alive()` with `CharacterSystem.is_alive(character)`.
    - Access `character.team` as a data attribute.
- **`combat/BattleActions.py`**:
    - Import `CharacterSystem`.
    - Replace instance method calls with static `CharacterSystem` calls for:
        - `is_alive`
        - `spend_focus`
        - `spend_mana`
        - `take_damage`
        - `generate_focus`
        - `generate_mana`

## Architectural Alignment
- **Rule 1.13**: Preserved. `Character` remains a data container.
- **MVC**: Logic is strictly contained in the "Core/System" layer.

## Risks
- Ensure all calls to `CharacterSystem` pass the `character` instance correctly.
- Verify that `CharacterSystem` has all the required static methods (it currently does, per previous inspection).
