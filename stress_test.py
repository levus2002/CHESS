from Model.GameModel import GameModel
from Persistence.Board import Board
from Persistence.Player import Player
from Controllers.RandomPlayer import RandomPlayer


MATCH_COUNT = 1000
MAX_MOVE_NUMBER = 100


def main():
    players = {pid: Player(pid) for pid in range(1, 5)}
    game = GameModel(Board(), players)

    providers = {
        pid: RandomPlayer()
        for pid in range(1, 5)
    }

    for match_number in range(1, MATCH_COUNT + 1):
        game.new_game()

        while not game.isgameover and game.move_number <= MAX_MOVE_NUMBER:
            player = game.CurrentPlayer()

            available_actions = game.movegen.get_all_moves(player.Figures)

            if not available_actions:
                player.IsDefeated = True
                game._advance_turn()
                continue

            action = providers[game.current_player].get_action(game)
            game.step(action)

        print(
            f"Match {match_number}/{MATCH_COUNT} finished | "
            f"Move number: {game.move_number} | "
            f"Game over: {game.isgameover}"
        )

    print("Stress test completed.")


if __name__ == "__main__":
    main()