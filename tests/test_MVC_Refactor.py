import pytest
from unittest.mock import MagicMock, patch
from pvp_simulator.Simulator import PvPSimulator, simulate_multiple_battles
from views.BattleView import BattleView
from core.Structs import BattleResult
from entities.Characters import Character

class TestMVCRefactor:
    @pytest.fixture
    def mock_character(self):
        char = MagicMock(spec=Character)
        char.name = "Hero"
        char.char_id = "hero_id"
        char.current_hp = 10
        char.action_cost_base = 50
        return char

    @pytest.fixture
    def mock_battle_result(self, mock_character):
        res = BattleResult()
        res.history = ["EXEC|Slash|Hero", "DMG|Goblin|5|Physical"]
        res.winners = [mock_character]
        res.losers = []
        res.duration = 5
        return res

    def test_battle_view_present_battle(self, mock_battle_result, capsys):
        view = BattleView()
        view.present_battle(mock_battle_result)
        
        captured = capsys.readouterr().out
        assert "[ACTION] Hero uses Slash" in captured
        assert "[DAMAGE] Goblin receives 5 Physical damage" in captured
        assert "Batalha terminada!" in captured
        assert "Hero: 10HP" in captured

    def test_battle_view_present_summary(self, mock_battle_result, capsys):
        view = BattleView()
        view.present_summary([mock_battle_result], "hero_id", "goblin_id")
        
        captured = capsys.readouterr().out
        assert "Resultados das 1 batalhas:" in captured
        assert "hero_id: 1 vitórias" in captured
        assert "goblin_id: 0 vitórias" in captured
        assert "Média de turnos por batalha: 5.00" in captured

    @patch("pvp_simulator.Simulator.BattleManager")
    def test_simulator_run_simulation(self, mock_bm_class, mock_character):
        # Setup mock
        mock_bm = mock_bm_class.return_value
        mock_bm.battle_result = BattleResult(history=["Test"])
        
        dice_manager = MagicMock()
        data_manager = MagicMock()
        judge = MagicMock()
        
        sim = PvPSimulator(dice_manager, data_manager, judge, mock_character, mock_character)
        result = sim.run_simulation()
        
        assert result.history == ["Test"]
        assert mock_bm.run_battle.called

    @patch("pvp_simulator.Simulator.PvPSimulator")
    @patch("pvp_simulator.Simulator.DataManager")
    def test_simulate_multiple_battles(self, mock_dm_class, mock_sim_class, mock_battle_result):
        mock_sim = mock_sim_class.return_value
        mock_sim.run_simulation.return_value = mock_battle_result
        
        results = simulate_multiple_battles(2, "hero", "goblin")
        
        assert len(results) == 2
        assert results[0] == mock_battle_result
        assert mock_sim.run_simulation.call_count == 2

    @patch("pvp_simulator.Simulator.PvPSimulator.from_data_files")
    @patch("views.BattleView.BattleView.present_battle")
    def test_mono(self, mock_present, mock_from_data, mock_battle_result):
        mock_sim = mock_from_data.return_value
        mock_sim.run_simulation.return_value = mock_battle_result
        
        from pvp_simulator.Simulator import mono
        mono("char1", "char2")
        
        mock_present.assert_called_once_with(mock_battle_result)

    @patch("pvp_simulator.Simulator.simulate_multiple_battles")
    @patch("views.BattleView.BattleView.present_summary")
    def test_multy(self, mock_present, mock_simulate):
        mock_simulate.return_value = []
        
        from pvp_simulator.Simulator import multy
        multy("char1", "char2")
        
        mock_present.assert_called_once_with([], "char1", "char2")
