from core.Enums import BattleState
from combat.BattleManager import BattleManager

class BattleJudge:
    """
    Determina a condição de vitória de uma batalha
    """
    def rule(self, battle_manager: BattleManager)-> BattleState: 
        raise NotImplementedError  

class LastManStanding(BattleJudge):
    """
    Determina a condição de vitória de uma batalha
    """
    def rule(self, battle_manager: BattleManager)-> BattleState:
        live_characters = 0
        winner = None
        for key,character in battle_manager.characters.items():
            if character.is_alive():
                live_characters += 1
                winner = character
        if live_characters != 1:
            winner = None
        if live_characters == 0:
            return BattleState.DRAW
        if winner:
            battle_manager.battle_result.winners.append(winner)
            battle_manager.characters.pop(winner.char_id)
            for key, character in battle_manager.characters.items():
                battle_manager.battle_result.losers.append(character)
            return BattleState.VICTORY
        return BattleState.RUNNING
        
