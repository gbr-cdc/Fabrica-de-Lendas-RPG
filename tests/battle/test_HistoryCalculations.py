"""
Tests for ATK_CALC and DMG_CALC history entries in AttackAction.
Verifies the full formula breakdown is present in the history stream.
[ARCH.TEST_QUALITY.STRUCTURED_HISTORY]
"""
import pytest
from battle.BattleActions import AttackAction
from core.Structs import AttackActionTemplate
from core.Enums import BattleActionType, AttackType
from tests.utils.entity_factory import create_dummy_character
from tests.utils.test_utils import create_test_battle_manager
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_basic_attack(actor_attrs, target_attrs, atk_roll, def_roll, char_id="actor", target_id="target"):
    """Run a basic attack and return the ActionLoad."""
    manager = create_test_battle_manager()
    actor = create_dummy_character(char_id=char_id, attributes=actor_attrs)
    target = create_dummy_character(char_id=target_id, attributes=target_attrs)

    manager.add_character(actor, MagicMock(), start_tick=1000)
    manager.add_character(target, MagicMock(), start_tick=1000)
    manager.set_tick(actor, 0)
    manager.set_tick(target, 100)
    actor = manager.get_next_actor()

    manager.dice_service.schedule_result(atk_roll)
    manager.dice_service.schedule_result(def_roll)

    action = AttackAction(None, actor, [target], manager)
    load = manager.run_action(action)
    return load, actor, target


# ---------------------------------------------------------------------------
# ATK_CALC tag
# ---------------------------------------------------------------------------

class TestAtkCalcHistory:
    """ATK_CALC|actor_id|roll|rank|bda|final must appear after every attack roll."""

    def test_atk_calc_tag_present_on_hit(self):
        load, actor, target = _run_basic_attack([10, 10, 10], [1, 1, 1], atk_roll=10, def_roll=1)
        assert any(e.startswith("ATK_CALC|") for e in load.history), \
            "ATK_CALC tag missing from history"

    def test_atk_calc_tag_present_on_miss(self):
        load, actor, target = _run_basic_attack([1, 1, 1], [15, 15, 15], atk_roll=1, def_roll=20)
        assert any(e.startswith("ATK_CALC|") for e in load.history), \
            "ATK_CALC tag missing even when attack misses"

    def test_atk_calc_values_match_formula(self):
        """Final attack value == roll + rank + bda."""
        manager = create_test_battle_manager()
        actor = create_dummy_character(char_id="actor", attributes=[10, 10, 10])
        target = create_dummy_character(char_id="target", attributes=[1, 1, 1])

        manager.add_character(actor, MagicMock(), start_tick=1000)
        manager.add_character(target, MagicMock(), start_tick=1000)
        manager.set_tick(actor, 0)
        manager.set_tick(target, 100)
        actor = manager.get_next_actor()

        atk_roll = 8
        manager.dice_service.schedule_result(atk_roll)
        manager.dice_service.schedule_result(1)

        action = AttackAction(None, actor, [target], manager)
        load = manager.run_action(action)

        # Find the ATK_CALC entry
        atk_calc = next(e for e in load.history if e.startswith("ATK_CALC|"))
        parts = atk_calc.split("|")
        # ATK_CALC|actor_id|roll|rank|bda|final
        assert parts[1] == "actor"
        roll, rank, bda, final = int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])
        assert roll == atk_roll, f"Expected roll={atk_roll}, got {roll}"
        assert rank == actor.rank, f"Expected rank={actor.rank}, got {rank}"
        assert bda == actor.bda, f"Expected bda={actor.bda}, got {bda}"
        assert final == roll + rank + bda, \
            f"Final ({final}) != roll({roll}) + rank({rank}) + bda({bda})"

    def test_atk_calc_appears_after_roll_tag(self):
        """ATK_CALC must come after the corresponding ROLL tag in history order."""
        load, actor, target = _run_basic_attack([10, 10, 10], [1, 1, 1], atk_roll=5, def_roll=1)
        history = load.history
        roll_idx = next(i for i, e in enumerate(history) if e.startswith("ROLL|ATK|"))
        calc_idx = next(i for i, e in enumerate(history) if e.startswith("ATK_CALC|"))
        assert calc_idx > roll_idx, "ATK_CALC should appear after ROLL tag"


# ---------------------------------------------------------------------------
# DMG_CALC tag
# ---------------------------------------------------------------------------

class TestDmgCalcHistory:
    """DMG_CALC|target_id|pda|gda|mda|modifier|final must appear on every hit."""

    def test_dmg_calc_present_on_hit(self):
        load, actor, target = _run_basic_attack([10, 10, 10], [1, 1, 1], atk_roll=10, def_roll=1)
        assert any(e.startswith("DMG_CALC|") for e in load.history), \
            "DMG_CALC tag missing from history"

    def test_dmg_calc_absent_on_miss(self):
        load, actor, target = _run_basic_attack([1, 1, 1], [15, 15, 15], atk_roll=1, def_roll=20)
        assert not any(e.startswith("DMG_CALC|") for e in load.history), \
            "DMG_CALC should not appear when attack misses"

    def test_dmg_calc_values_match_formula(self):
        """Final damage == pda + (gda * mda) + modifier (where modifier=0 for plain attack)."""
        manager = create_test_battle_manager()
        actor = create_dummy_character(char_id="actor", attributes=[10, 10, 10])
        target = create_dummy_character(char_id="target", attributes=[1, 1, 1])

        manager.add_character(actor, MagicMock(), start_tick=1000)
        manager.add_character(target, MagicMock(), start_tick=1000)
        manager.set_tick(actor, 0)
        manager.set_tick(target, 100)
        actor = manager.get_next_actor()

        # Use large values to guarantee a hit.
        manager.dice_service.schedule_result(15)
        manager.dice_service.schedule_result(1)

        action = AttackAction(None, actor, [target], manager)
        load = manager.run_action(action)

        dmg_calc = next(e for e in load.history if e.startswith("DMG_CALC|"))
        parts = dmg_calc.split("|")
        # DMG_CALC|target_id|pda|gda|mda|modifier|final
        assert parts[1] == "target"
        pda, gda, mda, modifier, final = (
            int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5]), int(parts[6])
        )
        expected = pda + (gda * mda) + modifier
        assert final == expected, \
            f"DMG_CALC final ({final}) != pda({pda}) + (gda({gda})*mda({mda})) + mod({modifier}) = {expected}"

    def test_dmg_calc_appears_after_hit_tag(self):
        """DMG_CALC must come after HIT tag."""
        load, actor, target = _run_basic_attack([10, 10, 10], [1, 1, 1], atk_roll=10, def_roll=1)
        history = load.history
        hit_idx = next(i for i, e in enumerate(history) if e.startswith("HIT|"))
        calc_idx = next(i for i, e in enumerate(history) if e.startswith("DMG_CALC|"))
        assert calc_idx > hit_idx, "DMG_CALC should appear after HIT tag"


# ---------------------------------------------------------------------------
# BattleView parsing
# ---------------------------------------------------------------------------

class TestBattleViewCalcParsing:
    """Verify BattleView correctly translates ATK_CALC and DMG_CALC tags."""

    def setup_method(self):
        from views.BattleView import BattleView
        self.view = BattleView()

    def test_atk_calc_parsed(self):
        tag = "ATK_CALC|Aragorn|10|2|3|15"
        result = self.view._parse_entry(tag)
        assert "[CALC]" in result
        assert "Aragorn" in result
        assert "15" in result
        assert "10" in result  # roll
        assert "2" in result   # rank
        assert "3" in result   # bda

    def test_dmg_calc_parsed(self):
        tag = "DMG_CALC|Orc|5|3|2|0|11"
        result = self.view._parse_entry(tag)
        assert "[CALC]" in result
        assert "Orc" in result
        assert "11" in result   # final
        assert "5" in result    # pda
        assert "3" in result    # gda
        assert "2" in result    # mda
        assert "0" in result    # modifier

    def test_atk_calc_full_narrative(self):
        tag = "ATK_CALC|actor|8|2|0|10"
        result = self.view._parse_entry(tag)
        # Expect format: [CALC] actor Final Attack: 10 = 8 (Roll) + 2 (Rank) + 0 (BdA)
        assert "Final Attack" in result or "Roll" in result

    def test_dmg_calc_full_narrative(self):
        tag = "DMG_CALC|target|4|2|3|1|11"
        result = self.view._parse_entry(tag)
        # Expect format: [CALC] target Damage: 11 = 4 (PdA) + (2 GdA * 3 MdA) + 1 (Mod)
        assert "PdA" in result or "GdA" in result or "Damage" in result
