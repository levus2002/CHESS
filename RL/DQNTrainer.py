
import copy

import numpy as np
import torch
from torch import nn

from RL.MoveScorer import MoveScorer
from RL.ReplayBuffer import ReplayBuffer


class DQNTrainer:
    def __init__(
        self,
        model: MoveScorer,
        buffer: ReplayBuffer,
        device: str = "cpu",
        gamma: float = 0.99,
        learning_rate: float = 0.0001,
        batch_size: int = 64,
        target_update_interval: int = 500,
    ):
        self.model = model
        self.buffer = buffer
        self.device = torch.device(device)

        self.gamma = gamma
        self.batch_size = batch_size
        self.target_update_interval = target_update_interval
        self.update_count = 0

        # Keep the shared online model object intact
        self.model.to(self.device)

        # Independent copy
        self.target_model = copy.deepcopy(self.model)
        self.target_model.eval()

        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=learning_rate
        )
        self.loss_function = nn.SmoothL1Loss()

    def train_step(self) -> float | None:
        if len(self.buffer) < self.batch_size:
            return None

        experiences = self.buffer.sample(self.batch_size)

        states = torch.as_tensor(
            np.stack([e.state for e in experiences]),
            dtype=torch.float32,
            device=self.device
        )
        actions = torch.as_tensor(
            np.stack([e.action for e in experiences]),
            dtype=torch.float32,
            device=self.device
        )
        rewards = torch.tensor(
            [e.reward for e in experiences],
            dtype=torch.float32,
            device=self.device
        )
        predicted_q = self.model(states, actions)

        # Double DQN targets
        targets = rewards.clone()

        with torch.no_grad():
            for i, experience in enumerate(experiences):
                if experience.done:
                    continue

                if experience.next_state is None or not experience.next_actions:
                    raise ValueError(
                        "Nonterminal experience has no next state/actions"
                    )

                next_actions = torch.as_tensor(
                    np.stack(experience.next_actions),
                    dtype=torch.float32,
                    device=self.device
                )
                next_state = torch.as_tensor(
                    experience.next_state,
                    dtype=torch.float32,
                    device=self.device
                ).unsqueeze(0)

                next_states = next_state.expand(
                    len(experience.next_actions), -1, -1, -1
                )

                # Online network selects the best next action
                online_q = self.model(next_states, next_actions)
                best_index = torch.argmax(online_q).item()

                # Target network evaluates that action
                target_q = self.target_model(
                    next_states[best_index:best_index + 1],
                    next_actions[best_index:best_index + 1]
                )[0]

                targets[i] += self.gamma * target_q

        loss = self.loss_function(predicted_q, targets)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self.update_count += 1

        if self.update_count % self.target_update_interval == 0:
            self.target_model.load_state_dict(self.model.state_dict())

        return float(loss.item())
