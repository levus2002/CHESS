
import random

import numpy as np
import torch

from RL.MoveScorer import MoveScorer


class DQNAgent:
    def __init__(self, model: MoveScorer, device: str = "cpu"):
        self.model = model
        self.device = torch.device(device)
        self.model.to(self.device)

    def select_action(
        self,
        state: np.ndarray,
        actions: list[np.ndarray],
        epsilon: float = 0.0
    ) -> int:
        if not actions:
            raise ValueError("No legal actions available")

        if random.random() < epsilon:
            return random.randrange(len(actions))

        state_tensor = torch.as_tensor(
            state, dtype=torch.float32, device=self.device
        ).unsqueeze(0)

        action_tensor = torch.as_tensor(
            np.stack(actions), dtype=torch.float32, device=self.device
        )

        state_batch = state_tensor.expand(len(actions), -1, -1, -1)

        with torch.no_grad():
            q_values = self.model(state_batch, action_tensor)

        return int(torch.argmax(q_values).item())
