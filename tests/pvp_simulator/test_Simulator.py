import pytest
from unittest.mock import MagicMock, patch
from pvp_simulator.Simulator import PvPSimulator, simulate_multiple_battles
from core.Structs import BattleResult
from tests.utils.entity_factory import create_dummy_character
from core.DiceManager import DiceManager
from core.DataManager import DataManager
from battle.Judges import BattleJudge

class TestPvPSimulator:
    @pytest.fixture
    def hero(self):
        return create_dummy_character(char_id="hero_id", name="Hero")

    @pytest.fixture
    def goblin(self):
        return create_dummy_character(char_id="goblin_id", name="Goblin")

    @pytest.fixture
    def mock_dm(self):
        return MagicMock(spec=DataManager)

    def test_simulator_initialization(self, hero, goblin, mock_dm):
        dm = mock_dm
        dice = DiceManager()
        judge = BattleJudge()
        
        sim = PvPSimulator(dice, dm, judge, hero, goblin)
        
        assert sim.character1 == hero
        assert sim.character2 == goblin
        assert sim.dice_manager == dice
        assert sim.data_manager == dm
        assert sim.judge == judge

    @patch("pvp_simulator.Simulator.BattleManager")
    def test_run_simulation_calls_battle_manager(self, mock_bm_class, hero, goblin, mock_dm):
        mock_bm = mock_bm_class.return_value
        mock_bm.battle_result = BattleResult(history=["Test Event"])
        
        sim = PvPSimulator(DiceManager(), mock_dm, BattleJudge(), hero, goblin)
        result = sim.run_simulation()
        
        assert result.history == ["Test Event"]
        assert mock_bm.run_battle.called
        # Check if deepcopy was used (different instances)
        assert mock_bm.add_character.call_args_list[0][0][0] != hero
        assert mock_bm.add_character.call_args_list[1][0][0] != goblin

    @patch("pvp_simulator.Simulator.PvPSimulator")
    @patch("pvp_simulator.Simulator.DataManager")
    def test_simulate_multiple_battles(self, mock_dm_class, mock_sim_class):
        mock_sim = mock_sim_class.return_value
        expected_result = BattleResult(history=["Simulated"])
        mock_sim.run_simulation.return_value = expected_result
        
        # We need to mock DataManager because simulate_multiple_battles instantiates it
        mock_dm = mock_dm_class.return_value
        mock_dm.get_character.side_effect = [
            create_dummy_character(char_id="h"),
            create_dummy_character(char_id="g")
        ]
        
        results = simulate_multiple_battles(2, "h", "g")
        
        assert len(results) == 2
        assert results[0] == expected_result
        assert mock_sim.run_simulation.call_count == 2

    @patch("pvp_simulator.Simulator.PvPSimulator.from_data_files")
    @patch("views.BattleView.BattleView.present_battle")
    def test_mono_interface(self, mock_present, mock_from_data):
        mock_sim = mock_from_data.return_value
        res = BattleResult(history=["Battle"])
        mock_sim.run_simulation.return_value = res
        
        from pvp_simulator.Simulator import mono
        mono("char1", "char2")
        
        mock_present.assert_called_once_with(res)

    @patch("pvp_simulator.Simulator.simulate_multiple_battles")
    @patch("views.BattleView.BattleView.present_summary")
    def test_multy_interface(self, mock_present, mock_simulate):
        mock_simulate.return_value = ["res1", "res2"]
        
        from pvp_simulator.Simulator import multy
        multy("char1", "char2")
        
        mock_present.assert_called_once_with(["res1", "res2"], "char1", "char2")
