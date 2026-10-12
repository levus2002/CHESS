
from collections import deque
import random
import numpy as np
from Model.Dataclasses import Experience


class ReplayBuffer:
    def __init__(self, capacity: int = 10000):
        self.buffer = deque(maxlen = capacity)

    def add(
        self,
        state: np.ndarray,
        action: np.ndarray,
        reward: float,
        next_state: np.ndarray | None,
        next_actions: list[np.ndarray],
        done: bool
    ):
        experience = Experience(
            state,
            action,
            reward,
            next_state,
            next_actions,
            done
        )
        self.buffer.append(experience)

    def sample(self, batch_size: int) -> list[Experience]:
        return random.sample(self.buffer, batch_size)

    def __len__(self) -> int:
        return len(self.buffer)
