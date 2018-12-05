from Window import *
from Game import *
from DecisionMaker import *

import logging as l

class GameManager:
    """
    Manager for all game related actions. This class is the central 
    point of action and contains the core gameplay loop for interacting 
    with the application.
    """

    _window = Window()
    _game = Game()
    _decision_maker = DecisionMaker()

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
                    field = self._game.current_field_info

                    self._game.reset_field_state()
                    next_square = self._decision_maker.decide_next_square(field)
                    pass
            else:
                l.critical("The Minesweeper window must be opened in order for this program to work.")
