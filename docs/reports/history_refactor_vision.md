# Architectural Refactor Report: Data-Driven History Stream

**Date:** 2026-04-23
**Status:** PROPOSED
**Context:** [DISCUSSION] regarding MVC Purity and Agentic Verification.

## 1. Problem Statement
The current implementation of the `history` list in `ActionLoad` and `AttackLoad` violates the **ARCH.1.1 (Game-MVC)** guardrail. It stores narrative, human-readable strings (e.g., *"Warrior hit for 10 damage!"*) within the Model layer. 

### Issues:
*   **Leakage:** The Model is responsible for View-level presentation logic.
*   **Verification:** Agents and automated tests must rely on fragile string matching (Regex) to verify engine behavior.
*   **Scalability:** Localization and multi-platform rendering (UI vs. CLI) are coupled to the core logic.

## 2. Proposed Solution: The "Data Stream" Protocol
Transition the `history` from a `List[str]` of narratives to a `List[str]` of **Structured Event Codes**.

### 2.1 Event Format
`[TAG:META_DATA]` or `TAG|PARAM1|PARAM2`

### 2.2 Core Event Dictionary (Preliminary)
| Tag | Parameters | Description |
| :--- | :--- | :--- |
| `EXEC` | `action_id, actor_id` | Execution of a battle action started. |
| `ROLL` | `type, value, die_size` | A dice roll occurred (atk, def, etc). |
| `MOD`  | `source_id, value` | A value was modified by a passive or hook. |
| `HIT`  | `target_id` | Accuracy check passed. |
| `MISS` | `target_id` | Accuracy check failed. |
| `DMG`  | `target_id, amount, type` | Damage calculated and applied. |
| `HP`   | `entity_id, delta, current` | Final state change of health. |

## 3. Impact on Quality Metrics
By formalizing the history, we enable **Log-Trace Verification**:
*   Tests can assert the exact sequence of events.
*   Agents can verify if hooks (e.g., `on_damage_calculation`) were actually triggered by looking for the `MOD` tag.
*   The "Definition of Done" for a mechanic includes the presence of its specific tags in the trace.

## 4. Implementation Strategy (Future Task)
1.  **Phase 1:** Update `ActionLoad` to support both legacy and structured logs.
2.  **Phase 2:** Refactor `AttackAction.execute` to emit structured tags.
3.  **Phase 3:** Implement a `NarrativeService` in the View layer to translate tags back into player-friendly text.

---
**Note:** This report serves as the technical basis for a future [PLANNING] session. Implementation is deferred in favor of immediate Test Quality improvements.
