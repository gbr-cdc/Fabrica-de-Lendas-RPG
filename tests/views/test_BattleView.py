import pytest
from views.BattleView import BattleView
from core.Structs import BattleResult
from tests.utils.entity_factory import create_dummy_character

class TestBattleView:
    def test_parse_exec(self):
        history = ["EXEC|Slash|Hero"]
        result = BattleView.parse(history)
        assert result == ["[ACTION] Hero uses Slash"]

    def test_parse_roll(self):
        history = ["ROLL|Attack|15|20|Hero"]
        result = BattleView.parse(history)
        assert result == ["[ROLL] Hero: Attack -> 15 (d20)"]

    def test_parse_mod(self):
        history = ["MOD|Buff|5|Hero"]
        result = BattleView.parse(history)
        assert result == ["[MODIFIER] Buff adds 5 to Hero"]

    def test_parse_hit(self):
        history = ["HIT|Goblin"]
        result = BattleView.parse(history)
        assert result == ["[HIT] Goblin"]

    def test_parse_miss(self):
        history = ["MISS|Goblin"]
        result = BattleView.parse(history)
        assert result == ["[MISS] Goblin"]

    def test_parse_dmg(self):
        history = ["DMG|Goblin|10|Physical"]
        result = BattleView.parse(history)
        assert result == ["[DAMAGE] Goblin receives 10 Physical damage"]

    def test_parse_stats(self):
        history = [
            "HP|Hero|-5|45",
            "FOCUS|Hero|+1|3",
            "MANA_F|Hero|+2|2",
            "MANA_T|Hero|+0|10"
        ]
        result = BattleView.parse(history)
        assert result == [
            "[STATS] Hero HP: 45 (-5)",
            "[STATS] Hero FOCUS: 3 (+1)",
            "[STATS] Hero Floating MANA: 2 (+2)",
            "[STATS] Hero Total MANA: 10 (+0)"
        ]

    def test_parse_msg(self):
        history = ["MSG|The goblin roars!"]
        result = BattleView.parse(history)
        assert result == ["[MSG] The goblin roars!"]

    def test_parse_death(self):
        history = ["DEATH|Goblin"]
        result = BattleView.parse(history)
        assert result == ["[DEATH] Goblin has been defeated!"]

    def test_parse_status(self):
        history = ["STATUS|Hero|Poison|3|Applied"]
        result = BattleView.parse(history)
        assert result == ["[STATUS] Hero: Poison (3 turns) -> Applied"]

    def test_parse_turn_start(self):
        history = ["TURN_START|Hero|50|50|10|10|0|5"]
        result = BattleView.parse(history)
        assert result == [">>> TURN START: Hero (HP: 50/50, MP: 10/10, Focus: 0, Mana: 5)"]

    def test_parse_multiple(self):
        history = [
            "TURN_START|Hero|50|50|10|10|0|5",
            "EXEC|Strike|Hero",
            "ROLL|Attack|18|20|Hero",
            "HIT|Goblin",
            "DMG|Goblin|8|Physical",
            "HP|Goblin|-8|12"
        ]
        result = BattleView.parse(history)
        assert result == [
            ">>> TURN START: Hero (HP: 50/50, MP: 10/10, Focus: 0, Mana: 5)",
            "[ACTION] Hero uses Strike",
            "[ROLL] Hero: Attack -> 18 (d20)",
            "[HIT] Goblin",
            "[DAMAGE] Goblin receives 8 Physical damage",
            "[STATS] Goblin HP: 12 (-8)"
        ]

    def test_parse_malformed(self):
        history = ["UNKNOWN|Something", "EXEC|Incomplete"]
        result = BattleView.parse(history)
        # Assuming we just keep the raw tag for unknown/malformed ones
        assert result == ["UNKNOWN|Something", "EXEC|Incomplete"]

    def test_present_battle(self, capsys):
        hero = create_dummy_character(char_id="hero", name="Hero")
        hero.current_hp = 10
        
        res = BattleResult()
        res.history = ["EXEC|Slash|Hero", "DMG|Goblin|5|Physical"]
        res.winners = [hero]
        res.losers = []
        res.duration = 5
        
        view = BattleView()
        view.present_battle(res)
        
        captured = capsys.readouterr().out
        assert "[ACTION] Hero uses Slash" in captured
        assert "[DAMAGE] Goblin receives 5 Physical damage" in captured
        assert "Batalha terminada!" in captured
        assert "Hero: 10HP" in captured

    def test_present_summary(self, capsys):
        hero = create_dummy_character(char_id="hero_id", name="Hero")
        
        res = BattleResult()
        res.winners = [hero]
        res.duration = 5
        
        view = BattleView()
        view.present_summary([res], "hero_id", "goblin_id")
        
        captured = capsys.readouterr().out
        assert "Resultados das 1 batalhas:" in captured
        assert "hero_id: 1 vitórias" in captured
        assert "goblin_id: 0 vitórias" in captured
        assert "Média de turnos por batalha: 5.00" in captured
