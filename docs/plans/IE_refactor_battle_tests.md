# Plan: Refactor Battle Tests to Align with Quality Standards

## Objective
Implement the recommendations from `docs/reports/IE_2026-05-08_02:18.md` to improve the quality and organization of tests in the `tests/battle` directory, ensuring alignment with `[ARCH.TEST_QUALITY]` and `[ARCH.TEST_QUALITY.ATTACK_ACTION_DATA]`.

## Steps
1. **Consolidate Action Tests:**
    - Merge `test_multi_target.py` and `test_area_attacks.py` into `test_BattleActions.py`.
    - Delete `test_multi_target.py` and `test_area_attacks.py` after successful migration.

2. **Refactor Action Tests for Data Integration:**
    - Update the consolidated `test_BattleActions.py` to use `DataManager` to load `AttackActionTemplate` instead of manual instantiation.
    - Ensure assertions focus on final behavior (HP, history, status) rather than internal mock verification.

3. **Standardize Context & Enforce Entity Factory:**
    - Refactor `test_EngineEdgeCases.py` to use `create_dummy_character` and `BattleTestContext` instead of raw dictionaries and `MagicMock`.
    - Replace `MagicMock` with `BattleTestContext` in all other relevant unit tests where appropriate.

4. **Implement Lifecycle Audits:**
    - Update `test_postura_defensiva.py` to include `EventBus` subscriber baseline assertions (`assert context.event_bus.subscriber_count == baseline`).
    - Apply the same subscriber baseline checks to `test_StatusEffects.py` for ephemeral hooks.

5. **Validation:**
    - Run the entire test suite to guarantee no regressions (`pytest tests/`).

6. **Documentation Evaluation:**
    - Determine if project guidelines need updates, follow [WORKFLOWS.DOC_MODULES] if needed.
    - Create a report in `docs/reports` outlining the changes made.
