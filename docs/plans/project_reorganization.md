# Implementation Plan: Project Reorganization

> **Status:** AWAITING USER APPROVAL
> **Plan file:** `docs/plans/project_reorganization.md` *(to be created on approval)*

---

## Summary

Structural cleanup of the `Fábrica de Lendas` RPG project. No logic changes — pure file/folder reorganization and housekeeping. This plan must be approved before any files are moved.

---

## 1. `combat/` → `battle/` (rename module)

**Decision:** ✅ **Approved by user.**

- Rename the `combat/` source directory to `battle/`.
- Update all imports across the codebase (`combat.BattleManager` → `battle.BattleManager`, etc.).
- Rename the mirrored test folder: `tests/combat/` → `tests/battle/`.
- Update `agent_rules.md` (Section 1) — the rule currently lists `combat` as part of the model layer.

> [!IMPORTANT]
> This is a **high-impact rename**. Every file that imports from `combat` must be updated. Grep pass required before moving anything.

---

## 2. `entities/` — Keep the name

**Decision:** ✅ **Keep as-is.**

`entities` is the correct DDD/MVC term for data-container objects. It pairs well with `core` (systems/logic) and `data` (loaders/JSON). Alternatives like `models` would conflict with the MVC "Model" umbrella that includes all four of those packages.

---

## 3. `test_output.txt` — Delete from repo

**Decision:** ✅ **Delete.**

- It is currently **tracked by git** (confirmed via `git ls-files`).
- It is also listed in `.gitignore` — but `.gitignore` does not untrack already-committed files.
- Action: `git rm test_output.txt` (removes from tracking and deletes the file). The `.gitignore` entry already exists, so it won't re-appear.

---

## 4. `GDD Sistema de Batalha.md` → `docs/GDD Sistema de Batalha.md`

**Decision:** ✅ **Move to `docs/`.**

- Currently tracked in git at the root.
- Action: `git mv "GDD Sistema de Batalha.md" docs/`
- Update any links in `README.md` or `DEVLOG.md` that point to the root GDD file.

---

## 5. `Sistema_RPG_Regras.txt` — Legacy, gitignored, remove from tracking

**Decision:** ✅ **Keep file locally, remove from git tracking.**

- It is already listed in `.gitignore` (line 1), but `git ls-files` confirms it is **NOT tracked** — the gitignore is already working correctly. ✅
- Action: **None needed for git.** The file will remain on disk locally and will not be committed.
- Optional: move to `docs/` alongside the GDD for co-location of all design documents (user mentioned they should live together).

> [!NOTE]
> Since the file is not tracked, moving it to `docs/` is a simple `mv` — no git operation needed.

---

## 6. `DiceCalculator.py` → `utilities/DiceCalculator.py`

**Decision:** ✅ **Move to new `utilities/` folder.**

- Currently tracked at the project root.
- Action: `git mv DiceCalculator.py utilities/DiceCalculator.py`
- Create `utilities/__init__.py`.
- Check for any imports of `DiceCalculator` throughout the project and update paths.

> [!NOTE]
> `DiceCalculator.py` is a standalone utility script (not currently imported by the engine — it appears to be a separate calculator tool). Confirm before moving.

---

## 7. `core/Bases.py` → `core/BaseClasses.py`

**Decision:** ⚠️ **Proposed — needs confirmation.**

`BaseClasses.py` is more descriptive and avoids the ambiguity of `Bases.py` (which could be confused with a data "base"/database concept). The tradeoff is that it touches every file importing from `core.Bases`.

- Action: `git mv core/Bases.py core/BaseClasses.py`
- Update all imports: `from core.Bases import ...` → `from core.BaseClasses import ...`
- Update `tests/core/test_Bases.py` → `tests/core/test_BaseClasses.py`

---

## Suggestions from Agent

### S1. Add `utilities/` to `agent_rules.md` architecture map
The new `utilities/` folder should be documented in **Section 1** of `agent_rules.md` to prevent future agents from being confused about its role (it holds standalone helper scripts, not engine systems).

### S2. Add `docs/` to `agent_rules.md` 
Currently, `docs/plans/` is referenced in Section 4 but the `docs/` directory itself isn't in the architecture map. Adding it clarifies that GDD and legacy docs live there.

### S3. Consider a `utilities/__init__.py` that re-exports `DiceCalculator`
Makes the `utilities` package importable cleanly: `from utilities import DiceCalculator`.

### S4. `.gitignore` housekeeping
`test_output.txt` is in `.gitignore` but was also tracked. After `git rm`, the gitignore entry remains valid. No change needed — just awareness.

---

## Atomic Steps (for Active Task after approval)

| # | Action | Command |
|---|--------|---------|
| 1 | Remove `test_output.txt` from git | `git rm test_output.txt` |
| 2 | Move GDD to `docs/` | `git mv "GDD Sistema de Batalha.md" docs/` |
| 3 | Move `Sistema_RPG_Regras.txt` to `docs/` (local only) | `mv Sistema_RPG_Regras.txt docs/` |
| 4 | Create `utilities/` and move `DiceCalculator.py` | `git mv DiceCalculator.py utilities/DiceCalculator.py` + create `__init__.py` |
| 5 | Rename `core/Bases.py` → `core/BaseClasses.py` | `git mv core/Bases.py core/BaseClasses.py` + update all imports |
| 6 | Rename `tests/core/test_Bases.py` → `test_BaseClasses.py` | `git mv` + update content |
| 7 | Rename `combat/` → `battle/` | `git mv combat battle` |
| 8 | Rename `tests/combat/` → `tests/battle/` | `git mv tests/combat tests/battle` |
| 9 | Grep + update all `from combat.` imports | global find-replace |
| 10 | Update `agent_rules.md` Section 1 | edit file |
| 11 | Update `README.md` links | edit file |
| 12 | Run `pytest` — must be green (same pass rate as before) | `pytest` |
| 13 | Commit | `git commit -m "Project Reorg: rename combat→battle, move docs, add utilities"` |
