from core.Bases import IBattleContext
from core.Enums import BattleState

class BattleJudge:
    def rule(self, context: 'IBattleContext') -> 'BattleState':
        characters = context.get_characters()
        
        team_1_alive = any(c.is_alive() for c in characters if c.team == 1)
        team_2_alive = any(c.is_alive() for c in characters if c.team == 2)
        
        if team_1_alive and team_2_alive:
            return BattleState.RUNNING
        elif team_1_alive and not team_2_alive:
            return BattleState.VICTORY
        elif not team_1_alive and team_2_alive:
            return BattleState.DEFEAT
        else:
            return BattleState.DRAW
