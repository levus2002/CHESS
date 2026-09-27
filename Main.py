
import pygame as pg

from Model.Action import Action
from Model.GameModel import GameModel

from Persistence.Board import Board
from Persistence.Player import Player
from ui.boardpanel import BoardPanel
from ui.playerpanel import PlayerPanel
from ui.menubar import MenuBar
from ui.statusbar import StatusBar
from Controllers.ActionProvider import ActionProvider
from Controllers.RandomPlayer import RandomPlayer
import random



class App:
    FPS = 60
    AUTO_MOVE_DELAY = 500

    def __init__(self,):
        pg.init()
        self.board = Board()

        self.players: dict[int, Player] = {
            1: Player(1, "manual", "red"),
            2: Player(2, "manual", "blue"),
            3: Player(3, "manual", "green"),
            4: Player(4, "manual", "purple"),
        }
        self.game = GameModel(self.board, self.players)
        self.game.new_game()

        self.screen = pg.display.set_mode((1400, 900), pg.RESIZABLE)
        pg.display.set_caption("Four Player Chess")

        self.clock = pg.time.Clock()
        self.running = True

        # Autoplay
        self.action_providers: dict[int, ActionProvider] = {
            player_id: RandomPlayer()
            for player_id in self.players
        }
        self.auto_move_delay = self.AUTO_MOVE_DELAY
        self.next_auto_move = 0

        # Replay
        self.replay_mode = False
        self.replay_paused = False
        self.replay_actions: list[Action] = []
        self.replay_index = 0

        self._create_ui()



    # --------------------------------------------------
    # main loop
    # --------------------------------------------------

    def run(self):
        while self.running:
            dt = dt = self.clock.tick(self.FPS)

            self._sync_ui()
            self.handle_events()
            self.update(dt)
            self.render()

        pg.quit()
    
    def _update_clock(self, dt: int):
        if self.game.isgameover or self.replay_mode:
            return

        player = self.game.CurrentPlayer()

        player.time_ms = max(0, player.time_ms - dt)

        if player.time_ms == 0:
            player.IsDefeated = True
            self.status_bar.message = (
                f"PLAYER {self.game.current_player} is Defeated"
            )

            self.game._advance_turn()
            self._clear_board_selection()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                return

            if event.type == pg.VIDEORESIZE:
                self._resize_ui()
                continue

            for element in self.ui_elements:
                element.handle_event(event)

    def update(self, dt: int):
        self._update_clock(dt)
        now = pg.time.get_ticks()

        if self.replay_mode:
            self._update_replay(now)
        else:
            self._update_autoplay(now)

        for element in self.ui_elements:
            element.update(dt)

    def render(self):
        self.screen.fill((35, 35, 35))

        for element in self.ui_elements:
            element.render(self.screen)

        pg.display.flip()

    # --------------------------------------------------
    # Autoplay and replay
    # --------------------------------------------------

    def _update_autoplay(self, now: int):
        if self.game.isgameover:
            return

        if now < self.next_auto_move:
            return

        player = self.game.CurrentPlayer()

        if player.Control == "manual":
            return

        provider = self.action_providers.get(
            self.game.current_player
        )

        if provider is None:
            return

        action = provider.get_action(self.game)

        self.game.step(action)
        self._clear_board_selection()

        self.next_auto_move = now + self.auto_move_delay

    # --------------------------------------------------
    # Game management
    # --------------------------------------------------

    def new_game(self):
        self.replay_mode = False
        self.replay_paused = False
        self.replay_actions.clear()
        self.replay_index = 0

        self.game.new_game()
        self._clear_board_selection()

        self.next_auto_move = (
            pg.time.get_ticks() + self.auto_move_delay
        )

        self.status_bar.message = ""

    def _clear_board_selection(self):
        self.board_panel._clear_selection()

    # --------------------------------------------------
    # Player controls
    # --------------------------------------------------

    def change_control(self, player_id: int):
        if self.replay_mode:
            return
        player = self.game.get_player(player_id)
        if player.Control == "manual":
            player.Control = "random"
        else:
            player.Control = "manual"

        self.next_auto_move = (
            pg.time.get_ticks() + self.auto_move_delay
        )

    def load_agent(self, player_id: int):
        if self.replay_mode:
            return
        pass

    # --------------------------------------------------
    # Replay
    # --------------------------------------------------

    def start_replay(self, actions: list[Action]):
        self.game.new_game()
        self._clear_board_selection()

        self.replay_actions = list(actions)
        self.replay_index = 0

        self.replay_mode = True
        self.replay_paused = False

        self.next_auto_move = (
            pg.time.get_ticks() + self.auto_move_delay
        )

    def _update_replay(self, now: int):
        if self.replay_paused:
            return

        if now < self.next_auto_move:
            return

        if self.replay_index >= len(self.replay_actions):
            self.replay_paused = True
            return

        action = self.replay_actions[self.replay_index]

        self.game.step(action)
        self.replay_index += 1

        self.next_auto_move = now + self.auto_move_delay

    def toggle_replay_pause(self):
        if not self.replay_mode:
            return

        self.replay_paused = not self.replay_paused

        if not self.replay_paused:
            self.next_auto_move = (
                pg.time.get_ticks() + self.auto_move_delay
            )

    def open_replay(self):
        pass

    def save_game(self):
        pass



    # --------------------------------------------------
    # UI
    # --------------------------------------------------

    def _create_ui(self):
        width, height = self.screen.get_size()

        menu_height = 52
        status_height = 40
        panel_width = 280

        self.menu_bar = MenuBar(
            pg.Rect(0, 0, width, menu_height),
            buttons=["New Game", "Save Game", "Replay Game"],
            callbacks={
                "New Game": self.new_game,
                "Save Game": self.save_game,
                "Replay Game": self.open_replay,
                "PauseReplay": self.toggle_replay_pause,
            },
        )

        self.player_panel = PlayerPanel(
            rect=pg.Rect(
                0,
                menu_height,
                panel_width,
                height - menu_height - status_height,
            ),
            players=self.game.players,
            get_current_player=lambda: self.game.current_player,
            on_control_change=self.change_control,
            on_load_agent=self.load_agent,
        )

        self.board_panel = BoardPanel(
            rect=pg.Rect(
                panel_width,
                menu_height,
                width - panel_width,
                height - menu_height - status_height,
            ),
            game_model=self.game,
        )

        self.status_bar = StatusBar(
            rect=pg.Rect(
                0,
                height - status_height,
                width,
                status_height,
            ),
            game_model=self.game,
        )

        self.ui_elements = [
            self.menu_bar,
            self.player_panel,
            self.board_panel,
            self.status_bar,
        ]

    def _resize_ui(self):
        width, height = self.screen.get_size()

        menu_height = 52
        status_height = 40
        panel_width = 280

        self.menu_bar.rect = pg.Rect(
            0, 0, width, menu_height
        )

        self.player_panel.rect = pg.Rect(
            0,
            menu_height,
            panel_width,
            height - menu_height - status_height,
        )

        self.board_panel.rect = pg.Rect(
            panel_width,
            menu_height,
            width - panel_width,
            height - menu_height - status_height,
        )

        self.status_bar.rect = pg.Rect(
            0,
            height - status_height,
            width,
            status_height,
        )

    def _sync_ui(self):
        """Pass application-level display state to the UI."""
        self.menu_bar.replay_mode = self.replay_mode
        self.menu_bar.replay_paused = self.replay_paused

        self.player_panel.replay_mode = self.replay_mode
        self.board_panel.replay_mode = self.replay_mode









def main():
    App().run()


if __name__ == "__main__":
    main()