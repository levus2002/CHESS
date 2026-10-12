
import numpy as np

from Model.Dataclasses import Action
from Model.GameModel import GameModel
from Persistence.Type import Type


PIECE_INDEX = {
    Type.Pawn: 0,
    Type.Knight: 1,
    Type.Bishop: 2,
    Type.Rook: 3,
    Type.Queen: 4,
    Type.King: 5,
}

SPECIAL_INDEX = {
    None: 0,
    "double": 1,
    "KingCastle": 2,
    "QueenCastle": 3,
    "en_passant": 4,
}

PROMOTION_INDEX = {
    None: 0,
    "N": 1,
    "B": 2,
    "R": 3,
    "Q": 4,
}


def encode_state(game: GameModel, player_id: int) -> np.ndarray:
    state = np.zeros((29, 14, 14), dtype=np.float32)

    # Acting player first, then the others in turn order.
    order = [
        (player_id - 1 + offset) % 4 + 1
        for offset in range(4)
    ]

    for relative_index, pid in enumerate(order):
        player = game.players[pid]

        for figure in player.Figures:
            channel = relative_index * 6 + PIECE_INDEX[figure.Type]
            state[channel, figure.X, figure.Y] = 1.0

            if figure.HasMoved:
                state[24, figure.X, figure.Y] = 1.0

        # Entire plane is 1 if this player is still active.
        if not player.IsDefeated:
            state[25 + relative_index, :, :] = 1.0

    return state


def encode_action(game: GameModel, action: Action) -> np.ndarray:
    features = np.zeros(15, dtype=np.float32)

    features[0] = action.from_row / 13.0
    features[1] = action.from_col / 13.0
    features[2] = action.to_row / 13.0
    features[3] = action.to_col / 13.0

    target = game.board.get_figure(action.to_row, action.to_col)
    if target is not None or action.special == "en_passant":
        features[4] = 1.0

    # Special move one-hot
    features[5 + SPECIAL_INDEX[action.special]] = 1.0

    # Promotion one-hot
    features[10 + PROMOTION_INDEX[action.promotion]] = 1.0

    return features
