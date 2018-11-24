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
                self._game.update(self._window)

                if self._game.has_changed():
                    self._game.reset_field_state()

                    # Crude display of the field state.
                    for row in self._game.current_field_info:
                        for column in row:
                            if column.is_unchecked:
                                print("  ", end = "")
                            else:
                                print("{} ".format(column.value), end = "")
                        print("")
            else:
                l.critical("The Minesweeper window must be opened in order for this program to work.")
