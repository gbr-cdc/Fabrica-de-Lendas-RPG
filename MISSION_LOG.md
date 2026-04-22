# Mission Log

## RECENT HISTORY
- [2026-04-21 17:37: Postura Defensiva](MISSION_HISTORY.md#2026-04-21-1737-postura-defensiva)
- [2026-04-20: Timeline Tie-Breaking Logic](MISSION_HISTORY.md#2026-04-20-timeline-tie-breaking-logic)
- [2026-04-20: PvP Simulator Path Fix](MISSION_HISTORY.md#2026-04-20-pvp-simulator-path-fix)

> [!TIP]
> **Token Economy:** Only **[ACTIVE]** missions are kept here. Completed entries are moved to [MISSION_HISTORY.md](file:///home/alice/Repositorios/RPG/MISSION_HISTORY.md).
> **Step Format:** `- [ ] Description | Files: path/to/file.py` → On completion: `- [x] Description | Files: ... | Note: 1-sentence state summary`.

## MISSION: Targeting System Refactor ([ACTIVE])
Summary: Refactor `BattleAction` and `AttackAction` to support multiple targets (0-N). Update `PosturaDefensiva` to track multiple hit targets simultaneously.
Rule References: `ARCH.1.13`, `OP.1.2`
Plan Link: [targeting_system.md](docs/plans/targeting_system.md)

- [ ] Update `BattleAction` interface to accept `targets: List[Character]` | Files: `core/BaseClasses.py`
- [ ] Update `PvP1v1Controller` to provide targets as a list | Files: `controllers/CharacterController.py`
- [ ] Refactor `AttackAction` and other actions to handle multi-targeting | Files: `battle/BattleActions.py`
- [ ] Update `PosturaDefensiva` tracking logic for multiple targets | Files: `battle/BattlePassives.py`
- [ ] Update and verify tests for multi-target mechanics | Files: `tests/battle/test_postura_defensiva.py`
