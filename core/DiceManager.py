
import random
from collections import deque
from core.Models import RollState

class DiceManager:
    def __init__(self, seed: int | None = None):
        self.random = random.Random(seed)
        self.queue = deque()

    def schedule_result(self, val: int):
        self.queue.append(val)

    def roll_dice(self, sides: int, state: RollState = RollState.NEUTRAL) -> int:
        if self.queue:
            return self.queue.popleft()
        if state == RollState.ADVANTAGE:
            return max(self.random.randint(1, sides), self.random.randint(1, sides))
        elif state == RollState.DISADVANTAGE:
            return min(self.random.randint(1, sides), self.random.randint(1, sides))
        else:
            return self.random.randint(1, sides)