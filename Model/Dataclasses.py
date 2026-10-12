
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class Action:
    from_row: int
    from_col: int
    to_row: int
    to_col: int
    special: str | None = None
    promotion: str | None = None

@dataclass
class MoveResult:
    player_id: int
    captured_value: int = 0
    captured_player_active: bool = False
    promotion_value: int = 0

@dataclass
class Experience:
    state: np.ndarray
    action: np.ndarray
    reward: float
    next_state: np.ndarray | None
    next_actions: list[np.ndarray]
    done: bool