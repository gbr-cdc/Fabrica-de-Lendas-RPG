# MISSION LOG [MISSION.GLOBAL]

## ACTIVE MISSIONS [MISSION.ACTIVE]

### MISSION: Threat System Implementation [MISSION.ACTIVE.THREAT_SYSTEM]
- **Summary**: Implement Threat logic via ThreatManager to track who threatens whom, restrict targeting, and enforce Disengage Tests. Exposes hooks via get_hooks().
- **Rule References**: [ARCH.RULES.CORE.OBSERVER], [ARCH.RULES.CORE.IOC]
- **Documentation References**: [ARCH.DOC.battle.BattleManager.BattleManager]
- **Definition of Done**: ThreatManager tracks engagements, enforces targeting, executes Disengage tests, and integrates with BattleManager.
- **Plan**: docs/plans/threat_system.md
- **Steps**:
- `[RED] [Test ThreatManager State]: Verify ThreatManager tracks engagements and exposes hooks. | Files: tests/battle/test_ThreatManager.py`
- `[GREEN] [Implement ThreatManager State]: Create ThreatManager, tracking logic, and expose hooks. | Files: battle/ThreatManager.py`
- `[RED] [Test Disengage Logic]: Verify validate_action handles targeting restrictions and tests. | Files: tests/battle/test_ThreatManager.py`
- `[GREEN] [Implement Disengage Logic]: Implement validate_action method, tests and failure states. | Files: battle/ThreatManager.py`
- `[BLUE] [Integrate with BattleManager]: Instantiate ThreatManager and insert validate_action into run_action loop. | Files: battle/BattleManager.py`

## ARCHIVED MISSIONS [MISSION.ARCHIVE]