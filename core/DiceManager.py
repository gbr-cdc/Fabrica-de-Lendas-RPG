
import random
from collections import deque
from core.Structs import RollResult
from core.Enums import RollState

class DiceManager:
    def __init__(self, seed: int | None = None):
        self.random = random.Random(seed)
        self.queue = deque()

    def schedule_result(self, val: int):
        self.queue.append(val)

    def roll_dice(self, sides: int, state: RollState = RollState.NEUTRAL) -> RollResult:
        if self.queue:
            value=self.queue.popleft()
            return RollResult(value, value, scheduled=True)
        elif state == RollState.ADVANTAGE:
            roll1 = self.random.randint(1, sides)
            roll2 = self.random.randint(1, sides)
            return RollResult(max(roll1, roll2), roll1, roll2, RollState.ADVANTAGE)
        elif state == RollState.DISADVANTAGE:
            roll1 = self.random.randint(1, sides)
            roll2 = self.random.randint(1, sides)
            return RollResult(min(roll1, roll2), roll1, roll2, RollState.DISADVANTAGE)
        else:
            roll = self.random.randint(1, sides)
            return RollResult(roll, roll, None, RollState.NEUTRAL)