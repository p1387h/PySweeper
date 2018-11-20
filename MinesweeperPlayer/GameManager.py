from Window import *
from Game import *

import logging as l

class GameManager:
    _window = Window()
    _game = Game()

    def run(self):
        if self._window.is_open():
            pass
        else:
            l.critical("The Minesweeper window must be opened in order for this program to work.")
