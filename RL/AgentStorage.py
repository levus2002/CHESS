
from pathlib import Path

import torch

from RL.MoveScorer import MoveScorer
from RL.DQNAgent import DQNAgent


class AgentStorage:
    @staticmethod
    def save(agent: DQNAgent, path: str | Path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(agent.model.state_dict(), path)

    @staticmethod
    def load(path: str, device: str = "cpu") -> DQNAgent:
        model = MoveScorer()
        state_dict = torch.load(
            path,
            map_location=device,
            weights_only=True,
        )
        model.load_state_dict(state_dict)
        model.eval()

        return DQNAgent(model, device=device)
