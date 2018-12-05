from Window import *
from Game import *

import logging as l

class GameManager:
    """
    Manager for all game related actions. This class is the central 
    point of action and contains the core gameplay loop for interacting 
    with the application.
    """

    _window = Window()
    _game = Game()

    def run(self):
        """
        Fuction for starting the central gameplay loop.
        """

        l.info("Starting the GameManager")

        while not self._game.is_finished():
            if self._window.is_open():
                # TODO: Remove
                input("Waiting for input...")

                self._game.update(self._window)

                if self._game.has_changed():
                    self._game.reset_field_state()
            else:
                l.critical("The Minesweeper window must be opened in order for this program to work.")
