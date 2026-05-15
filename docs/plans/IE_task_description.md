# IE_task_description: Buff "Rítmo Acelerado" Passive

## 1. Understand
The user wants to buff the `RitmoAcelerado` passive. Currently, it allows an action to become a `MOVE_ACTION` (fast action) if the `attack_roll` exceeds a threshold. 
The new requirements are:
- Gain `+1 pre` (configurable via json, default 1) against the same target upon a successful hit.
- The bonus accumulates up to `+2` (configurable via json, default 2).
- If the attack misses, the bonus is completely lost.
- If the character performs a different action instead of attacking the tracked target, the bonus is lost.
- The logic to verify the hit and manage bonus tracking MUST rely on our structured `ActionLoad.history`, ensuring elegance and adherence to the framework's mechanics.

## 2. Propose (Execution Plan)
1.  **Update `BattlePassives.json`:**
    - Add `"pre_bonus_per_hit": 1` and `"max_pre_bonus": 2` to the `Ritmo Acelerado` parameters.
2.  **Update `battle/BattlePassives.py` (`RitmoAcelerado`):**
    -   **State Initialization:** Add `self.tracked_target_id: str | None = None` and `self.current_bonus: int = 0` to `__init__`.
    -   **`on_roll_modify` Hook (Apply Bonus):** The event guarantees an `AttackLoad`. If the attack targets `self.tracked_target_id`, apply `self.current_bonus` to `attack_load.pre` and emit the `PASSIVE` and `ATK_LOAD` history events. If it targets a different character, reset `self.current_bonus = 0` and update `self.tracked_target_id = attack_load.target.char_id`.
    -   **`on_attack_end` Hook:** Keep the existing logic for the `MOVE_ACTION` threshold roll unchanged.
    -   **`on_turn_end` Hook (Update & Clear tracking):** 
        - For the owner's turn, construct the expected hit message using `HistoryEmitter.hit(self.tracked_target_id)`.
        - If the hit message is in `action_load.history`, increment `self.current_bonus` by `pre_bonus_per_hit` (up to `max_pre_bonus`).
        - If the hit message is NOT in the history, reset the state (`self.current_bonus = 0` and `self.tracked_target_id = None`).
3.  **Update/Create Tests in `tests/`:**
    - Write tests for `RitmoAcelerado` verifying the bonus application, accumulation, clearing on miss (by verifying history absence), and clearing on attacking another target.
    - Ensure all tests pass.

## 3. HALT EXECUTION
Awaiting user approval to proceed.
