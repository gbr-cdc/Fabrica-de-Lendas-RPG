# Plan: Test Quality Improvement

This plan outlines a series of missions to align the engine's test suite with the new **Test Quality Standards**. The focus is on replacing excessive mocking with behavior-driven integration tests using real objects.

## Problem Statement
Current tests rely heavily on `MagicMock` for core entities (`Character`, `BattleAction`, `Judge`), which leads to:
1.  **False Positives**: Tests pass because mocks are called, not because logic is correct.
2.  **Implementation Coupling**: Tests break on internal refactoring even if public behavior is unchanged.
3.  **Low Confidence**: 100% coverage does not guarantee system integrity.

## Proposed Solution
Shift the testing strategy to:
- **Behavior over Implementation**: Assert final states (HP, MP, Event logs) instead of method call counts.
- **Controlled Mocking**: Use real object instances initialized via `DataManager`. Mocks are restricted to I/O and external Controllers.
- **Scenario-Based Testing**: Test complete action cycles (e.g., Attack -> Defense Passive -> Damage Apply).

---

## Mission Series Breakdown

### 1. Core Module Integrity [TEST.CORE]
- **Target**: `core/` (CharacterSystem, DataManager, Modifiers, DiceManager).
- **Strategy**: Refactor unit tests to use real `Character` and `StatModifier` instances. Verify that `CharacterSystem` operations result in correct state changes.
- **Impact**: Establishes a reliable foundation for all other modules.

### 2. Battle Orchestration & Logic [TEST.BATTLE]
- **Target**: `battle/` (BattleManager, BattleActions, BattlePassives).
- **Strategy**: 
    - Replace `MagicMock` characters in `BattleManager` tests.
    - Test `BattleActions` as system behaviors (resource cost + effect application).
    - Test `BattlePassives` via the EventBus using real `AttackLoad` payloads.
- **Impact**: Ensures combat logic is resilient and architecturally sound.

### 3. Controllers, Entities & Data [TEST.CED]
- **Target**: `controllers/`, `entities/`, `data/`.
- **Strategy**:
    - Test `CharacterController` decision loops with real state scenarios.
    - Validate `data/` loading integrity and schema compliance.
- **Impact**: Guarantees that the engine's data-driven configuration is valid.

### 4. System Integration & Regression [TEST.SYSTEM]
- **Target**: Cross-module flows and `pvp_simulator/`.
- **Strategy**: Implement full battle scenarios and assert system-wide invariants.
- **Impact**: Provides final verification of engine stability.

---

## Architecture Compliance
- **ARCH.1.1 (Game-MVC)**: Tests must verify Model behavior without relying on specific View/Controller implementations.
- **ARCH.1.5 (Data-Driven)**: Tests must use `DataManager` to load real templates for Characters and Actions.
- **ARCH.1.8 (Modifier Stack)**: Verification must assert the correctness of the character's final stat totals after modifiers are applied.
