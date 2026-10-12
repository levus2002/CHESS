
import torch
from torch import nn


class MoveScorer(nn.Module):
    def __init__(
        self,
        state_size: int = 29 * 14 * 14,
        action_size: int = 15
    ):
        super().__init__()

        state_out = 256
        action_out = 64

        self.state_net = nn.Sequential(
            nn.Linear(state_size, 512),
            nn.ReLU(),
            nn.Linear(512, state_out),
            nn.ReLU(),
        )

        self.action_net = nn.Sequential(
            nn.Linear(action_size, 64),
            nn.ReLU(),
            nn.Linear(64, action_out),
            nn.ReLU(),
        )

        self.head = nn.Sequential(
            nn.Linear(state_out + action_out, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

    def forward(
        self,
        state_batch: torch.Tensor,
        action_batch: torch.Tensor
    ) -> torch.Tensor:
        # Accept encoded board states: (batch, 29, 14, 14)
        state_batch = state_batch.flatten(start_dim=1)

        s = self.state_net(state_batch)
        a = self.action_net(action_batch)

        x = torch.cat([s, a], dim=-1)
        return self.head(x).squeeze(-1)
