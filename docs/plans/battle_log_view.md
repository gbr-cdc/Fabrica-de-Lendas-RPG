# Plan: Battle Log View Implementation [PLAN.BATTLE_VIEW]

## Problem Statement
The battle engine now emits structured history tags (e.g., `DMG|Target1|10|Physical`) instead of narrative strings. We need a View layer to parse these tags and generate human-readable technical logs for battle simulation and debugging.

## Proposed Solution
Create a new directory `views/` and implement `BattleView.py`. This module will contain logic to translate the pipe-delimited history stream into a list of strings.

### 1. New Directory Structure
- `views/`
  - `__init__.py`
  - `BattleView.py`: Contains the `BattleLog` class or functions.

### 2. Implementation Details
The `BattleLog.parse(history: List[str]) -> List[str]` function will iterate through the history tags and use a mapping or a series of match/case (Python 3.10+) statements to format them.

**Technical Formatting Rules:**
- `EXEC|action_id|actor_id`: `[ACTION] {actor_id} uses {action_id}`
- `ROLL|type|value|die_size|actor_id`: `[ROLL] {actor_id}: {type} -> {value} (d{die_size})`
- `MOD|source_id|value|target_id`: `[MODIFIER] {source_id} adds {value} to {target_id}`
- `HIT|target_id`: `[HIT] {target_id}`
- `MISS|target_id`: `[MISS] {target_id}`
- `DMG|target_id|amount|type`: `[DAMAGE] {target_id} receives {amount} {type} damage`
- `HP|entity_id|delta|current`: `[STATS] {entity_id} HP: {current} ({delta})`
- `FOCUS|entity_id|delta|current`: `[STATS] {entity_id} FOCUS: {current} ({delta})`
- `MANA_F|entity_id|delta|current`: `[STATS] {entity_id} Floating MANA: {current} ({delta})`
- `MANA_T|entity_id|delta|current`: `[STATS] {entity_id} Total MANA: {current} ({delta})`
- `MSG|message`: `[MSG] {message}`
- `DEATH|entity_id`: `[DEATH] {entity_id} has been defeated!`
- `STATUS|entity_id|name|duration|state`: `[STATUS] {entity_id}: {name} ({duration} turns) -> {state}`
- `TURN_START|actor_id|hp|max_hp|mp|max_mp|focus|mana`: `>>> TURN START: {actor_id} (HP: {hp}/{max_hp}, MP: {mp}/{max_mp}, Focus: {focus}, Mana: {mana})`

## Verification Plan
1. **Unit Tests**: Create `tests/test_BattleView.py` to verify that each tag is correctly translated.
2. **Integration Test**: Use a mock `ActionLoad` with a sequence of tags and verify the resulting log output.

## Architectural Consistency
- **Decoupling**: Adheres to `[ARCH.RULES.CORE.MVC]` by moving string formatting out of the Model.
- **History Format**: Correctly parses the pipe-delimited format defined in `[ARCH.RULES.CORE.HISTORY]`.
