import hashlib
import random
from typing import Any


class DeterministicRng:
    def __init__(self, seed: str):
        self.seed = seed
        self._random = random.Random(seed)

    def d6(self) -> int:
        return self._random.randint(1, 6)

    def randint(self, low: int, high: int) -> int:
        return self._random.randint(low, high)

    def choice(self, items: list[Any]) -> Any:
        return self._random.choice(items)

    def weighted_choice(self, options: list[tuple[Any, int]]) -> Any:
        total = sum(weight for _, weight in options)
        if total <= 0:
            raise ValueError("Weighted choice requires positive total weight")

        roll = self._random.randint(1, total)
        running_total = 0
        for option, weight in options:
            running_total += weight
            if roll <= running_total:
                return option
        return options[-1][0]


def derive_step_seed(
    campaign_seed: str,
    step_type: str,
    action_type: str,
    actor_key: str,
    sequence: int,
) -> str:
    raw = f"{campaign_seed}:{step_type}:{action_type}:{actor_key}:{sequence}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
