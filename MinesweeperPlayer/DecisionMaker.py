from Square import *
from queue import Queue

import random
import logging as l

class DecisionMaker:
    """
    Class containing the logic for making click-decisions based on 
    the current state of the game.
    """

    _is_beginning_of_game = True
    _is_field_updated = False
    _safe_squares = Queue()

    def __init__(self):
        self.reset()

    def decide_next_square(self, field):
        """
        Function used for deciding which square should be clicked next.
        """

        next_square = None

        if self._is_beginning_of_game:
            self._is_beginning_of_game = False
            next_square = self.pick_random_square(field)
        elif self.do_safe_squares_exist():
            next_square = self.pick_safe_square()
            self._is_field_updated = False
        elif self._is_field_updated:
            next_square = self.pick_best_valued_square(field)
            self._is_field_updated = False
        else:
            self.update_field()
            self._is_field_updated = True
            next_square = self.decide_next_square(field)

        l.debug("Chose: {}".format(next_square.center_coordinates))

        return next_square

    def reset(self):
        """
        Reset function for all flags, queues etc.
        """

        self._is_beginning_of_game = True
        self._safe_squares = Queue()
        self._is_field_updated = False

    def do_safe_squares_exist(self):
        """
        Function for checking whether safe spots exist on the field.
        """

        return len(self._safe_squares) > 0

    def update_field(self):
        """
        Function for updating all information regarding the game's field like 
        safe spots or values.
        """

        pass

    def pick_random_square(self, field):
        """
        Function for picking a random square. Mostly used in at the beginning 
        of the game.
        """

        l.debug("Choosing random square.")

        row = random.randint(0, len(field) - 1)
        column = random.randint(0, len(field[row]) - 1)
        return field[row][column]

    def pick_safe_square(self):
        """
        Function for picking one of the safe squares. Only the ones that 
        are absolutely safe are returned here.
        """

        l.debug("Choosing safe square.")

        return self._safe_squares.get()

    def pick_best_valued_square(self, field):
        """
        Function for picking a square based on the general safety value of it.
        """

        l.debug("Choosing best valued square.")

        pass
