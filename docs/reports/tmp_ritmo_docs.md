##### RitmoAcelerado [ARCH.DOC.battle.BattlePassives.RitmoAcelerado]
[DEPENDS: ARCH.DOC.core.Events.HistoryEmitter, ARCH.DOC.core.Enums.BattleActionType, ARCH.DOC.core.Structs.BattlePassiveTemplate, ARCH.DOC.core.Events.AttackLoad, ARCH.DOC.core.Events.ActionLoad]
A data-driven rhythm passive that rewards high attack rolls by reducing action costs and rewards consecutive hits with increasing precision bonuses.

- Constructor [ARCH.DOC.battle.BattlePassives.RitmoAcelerado.__init__]: `__init__(owner: Character, context: IPassiveContext, template: BattlePassiveTemplate | None = None)`
- `tracked_target_id: str | None` [ARCH.DOC.battle.BattlePassives.RitmoAcelerado.tracked_target_id]: Tracks the ID of the current target to maintain the combo.
- `current_bonus: int` [ARCH.DOC.battle.BattlePassives.RitmoAcelerado.current_bonus]: The current accumulated precision bonus.

###### get_hooks [ARCH.DOC.battle.BattlePassives.RitmoAcelerado.get_hooks]
`get_hooks() -> Dict[str, Callable]`
Method description: Registers hooks for the rhythm logic.
1. `on_roll_modify`: Applies the accumulated precision bonus to the attack roll if targeting the tracked target. If the target differs, resets the tracked target and bonus.
2. `on_attack_end`: Evaluates if the attack roll exceeds the configured threshold. If so, downgrades the action cost to a `MOVE_ACTION`.
3. `on_turn_end`: Verifies the action history for a confirmed hit against the tracked target. If found, increments the precision bonus. If not found, clears the bonus and tracked target.
