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

        if self._window.is_open():
            self._game.update(self._window)
        else:
            l.critical("The Minesweeper window must be opened in order for this program to work.")
