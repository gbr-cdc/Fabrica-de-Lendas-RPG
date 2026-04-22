# Mission Log

## RECENT HISTORY
- [2026-04-22 09:35: Targeting System Refactor](MISSION_HISTORY.md#2026-04-22-0935-targeting-system-refactor)
- [2026-04-21 17:37: Postura Defensiva](MISSION_HISTORY.md#2026-04-21-1737-postura-defensiva)
- [2026-04-20: Timeline Tie-Breaking Logic](MISSION_HISTORY.md#2026-04-20-timeline-tie-breaking-logic)

> [!TIP]
> **Token Economy:** Only **[ACTIVE]** missions are kept here. Completed entries are moved to [MISSION_HISTORY.md](file:///home/alice/Repositorios/RPG/MISSION_HISTORY.md).
> **Step Format:** `- [ ] Description | Files: path/to/file.py` → On completion: `- [x] Description | Files: ... | Note: 1-sentence state summary`.

## MISSION: Area Attacks Implementation ([ACTIVE]) [PART 1]

**Summary:** Update core event infrastructure and passive safety to support a "Master Roll" (a single shared attack roll applied to multiple targets).
**Rule References:** ARCH.1.2, ARCH.1.3, ARCH.2.2
**Plan:** [area_attacks.md](docs/plans/area_attacks.md)

- [ ] Add `AREA = "area"` to `AttackType` enum | Files: core/Enums.py
- [ ] Update `AttackLoad` dataclass to allow `target: Character | None = None` (required for shared rolls) | Files: core/Events.py
- [ ] Wrap target-dependent logic in `battle/BattlePassives.py` hooks with `if attack_load.target is not None` checks | Files: battle/BattlePassives.py
- [ ] Add unit test verifying `AttackLoad` supports optional targets | Files: tests/core/test_Events.py

## MISSION: Area Attacks Implementation ([ACTIVE]) [PART 2]

**Summary:** Implement the "Master Roll" logic in `AttackAction`:
        - **If `self.attack_type == AttackType.AREA`**:
            - Perform one shared attack roll (emit `on_roll_modify` with `target=None`, then call `dice_service.roll_dice`).
            - Store this "Master Roll" result.
            - Iterate through `self.targets`:
                - For each target, resolve hits/damage using the shared Master Roll but individual target defense rolls.
        - **Else (Standard)**:
            - Maintain existing iterative logic (individual attack and defense rolls per target).
**Rule References:** ARCH.1.2, ARCH.2.2
**Plan:** [area_attacks.md](docs/plans/area_attacks.md)

- [ ] Refactor `AttackAction.execute` to trigger a single attack roll when `self.attack_type == AttackType.AREA` | Files: battle/BattleActions.py
- [ ] Implement iterative loop for target defense/damage using the shared attack roll result | Files: battle/BattleActions.py
- [ ] Create tests validating one attack roll vs multiple defense rolls in area scenarios | Files: tests/battle/test_area_attacks.py
