from Window import *
from Game import *
from DecisionMaker import *

import logging as l
import time as t

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

        l.info("Focusing the Window...")

        self._window.focus_window()
        # Time needed for the window to appear on top.
        t.sleep(0.25)

        l.info("Starting the GameManager...")
        input("Press any key to start.")

        while not self._game.is_finished:
            if self._window.is_open():
                # TODO: Remove
                #input("Waiting for input...")

                t.sleep(0.025)
                self.move_mouse_away()

                if self._decision_maker.do_safe_squares_exist():
                    # Perform all actions that are safe.
                    while self._decision_maker.do_safe_squares_exist():
                        t.sleep(0.025)
                        next_square = self._decision_maker.decide_next_square(field)
                        #self._window.click_mouse(next_square.center_coordinates)
                else:
                    # Update the current state of the game.
                    self._game.update(self._window)
                    field = self._game.current_field_info

                    next_square = self._decision_maker.decide_next_square(field)
                    #self._window.click_mouse(next_square.center_coordinates)
            else:
                l.critical("The Minesweeper window must be opened in order for this program to work.")

    def move_mouse_away(self):
        """
        Function for moving the mouse away from the game field in order 
        to prevent errors when taking screenshots.
        """

        self._window.move_mouse((0, 0), True, 0, 0)
