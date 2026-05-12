from battle.BattleManager import BattleManager
from core.DiceManager import DiceManager
from core.DataManager import DataManager
from battle.Judges import BattleJudge

def create_test_battle_manager():
    """
    Cria uma instância real do BattleManager para uso em testes.
    Utiliza DiceManager determinístico (seed 42) e carrega todos os dados reais.
    """
    dice = DiceManager(seed=42)
    data = DataManager()
    data.load_action_templates('data/AttackActions.json')
    data.load_passive_templates('data/BattlePassives.json')
    data.load_combat_styles('data/CombatStyles.json')
    data.load_game_rules('data/Rules.json')
    judge = BattleJudge()

    return BattleManager(dice, data, judge)
