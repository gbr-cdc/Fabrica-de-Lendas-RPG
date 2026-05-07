from typing import TYPE_CHECKING
from core.BaseClasses import IBattleContext, IBattleJudge
from core.Enums import BattleState
from core.CharacterSystem import CharacterSystem

if TYPE_CHECKING:
    from core.Structs import BattleResult

class BattleJudge(IBattleJudge):
    def rule(self, context: 'IBattleContext', result: 'BattleResult') -> 'BattleState':
        characters = context.get_characters()
        
        team_1_alive = any(CharacterSystem.is_alive(c) for c in characters if c.team == 1)
        team_2_alive = any(CharacterSystem.is_alive(c) for c in characters if c.team == 2)
        
        state = BattleState.RUNNING
        if team_1_alive and team_2_alive:
            state = BattleState.RUNNING
        elif team_1_alive and not team_2_alive:
            state = BattleState.VICTORY
        elif not team_1_alive and team_2_alive:
            state = BattleState.DEFEAT
        else:
            state = BattleState.DRAW

        if state != BattleState.RUNNING:
            result.winners.clear()
            result.losers.clear()
            
            all_participants = characters + context.get_graveyard()
            
            if state == BattleState.VICTORY:
                result.winners = [c for c in all_participants if c.team == 1]
                result.losers = [c for c in all_participants if c.team == 2]
            elif state == BattleState.DEFEAT:
                result.winners = [c for c in all_participants if c.team == 2]
                result.losers = [c for c in all_participants if c.team == 1]
            elif state == BattleState.DRAW:
                # In a draw, everyone is a loser or winners is empty. 
                # Following common RPG logic: no winners.
                result.losers = all_participants

        return state
