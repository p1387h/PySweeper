from Square import *
from SquareWrapper import *
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
    _best_valued_square_wrapper = None
    # HashSet of returned decisions such that squares are not chosen twice.
    _returned_decisions = set()

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
            self.update_field(field)
            self._is_field_updated = True
            next_square = self.decide_next_square(field)

        # Improve the results by keeping track of already chosen squares.
        self._returned_decisions.add(next_square)

        return next_square

    def reset(self):
        """
        Reset function for all flags, queues etc.
        """

        self._is_beginning_of_game = True
        self._safe_squares = Queue()
        self._is_field_updated = False
        self._best_valued_square = None
        self._returned_decisions = set()

    def do_safe_squares_exist(self):
        """
        Function for checking whether safe spots exist on the field.
        """

        return not self._safe_squares.empty()

    def update_field(self, field):
        """
        Function for updating all information regarding the game's field like 
        safe spots or values.
        """

        # Each square is being wrapped in order to allow callbacks when 
        # changing the total influence amount.
        wrapped_squares = {}
        for row_index in range(0, len(field)):
            for column_index in range(0, len(field[row_index])):
                square = field[row_index][column_index]
                affected_squares = []

                # All affected indices must be calculated.
                left_x = column_index - 1
                center_x = column_index
                right_x = column_index + 1
                top_y = row_index - 1
                center_y = row_index
                bottom_y = row_index + 1

                # Checks are needed since Python does not throw exceptions when 
                # accessing indices like -1 etc. but instead reads elements from 
                # the end of the list.
                # Left side of the target.
                if left_x >= 0:
                    if top_y >= 0:
                        affected_squares.append((top_y, left_x))
                    if center_y >= 0:
                        affected_squares.append((center_y, left_x))
                    if bottom_y < len(field):
                        affected_squares.append((bottom_y, left_x))
                # Top and bottom of the target.
                if center_x >= 0:
                    if top_y >= 0:
                        affected_squares.append((top_y, center_x))
                    if bottom_y < len(field):
                        affected_squares.append((bottom_y, center_x))
                # Right side of the target.
                if right_x < len(field[0]):
                    if top_y >= 0:
                        affected_squares.append((top_y, right_x))
                    if center_y >= 0:
                        affected_squares.append((center_y, right_x))
                    if bottom_y < len(field):
                        affected_squares.append((bottom_y, right_x))

                # First only create the instances.
                coordinates = row_index, column_index
                wrapper = SquareWrapper(square, affected_squares, coordinates)
                wrapped_squares[coordinates] = wrapper

        # Map each created instance to its neighbours such that all
        # neighbours can be directly accessed.
        for wrapper in wrapped_squares.values():
            wrapper.map_wrappers(wrapped_squares)

        # Update the values based on known bomb locations.
        for wrapper in wrapped_squares.values():
            wrapper.update_effective_value()

        # Collect all safe squares.
        safe_squares = set()
        for wrapper in wrapped_squares.values():
            for safe_square in wrapper.adjacent_safe_squares:
                safe_squares.add(safe_square)

        # Update all scores.
        max_row_index = max(map(lambda tuple: tuple[1], wrapped_squares.keys()))
        max_column_index = max(map(lambda tuple: tuple[0], wrapped_squares.keys()))
        for indices, wrapper in wrapped_squares.items():
            wrapper.update_score(indices, (max_row_index, max_column_index))

        # Move all wrappers to the collection of clickable ones.
        for wrapper in safe_squares:
            if not(wrapper.square in self._returned_decisions):
                self._safe_squares.put(wrapper)

        # Find the best valued square for clicking.
        best_valued_wrapper = None
        for wrapper in wrapped_squares.values():
            # Only unchecked ones that are no bombs.
            if wrapper.square.is_unchecked and not wrapper.has_reduced_neighbours:
                if best_valued_wrapper is None or wrapper.score < best_valued_wrapper.score:
                    best_valued_wrapper = wrapper
        self._best_valued_square_wrapper = best_valued_wrapper

    def pick_random_square(self, field):
        """
        Function for picking a random square. Mostly used in at the beginning 
        of the game.
        """

        l.debug("Choosing random square.")

        row = random.randint(0, len(field) - 1)
        column = random.randint(0, len(field[row]) - 1)

        l.debug("Chose: ({},{})".format(row, column))

        return field[row][column]

    def pick_safe_square(self):
        """
        Function for picking one of the safe squares. Only the ones that 
        are absolutely safe are returned here.
        """

        l.debug("Choosing safe square.")

        wrapper = self._safe_squares.get()
        
        l.debug("Chose: {}".format(wrapper.coordinates))

        return wrapper.square

    def pick_best_valued_square(self, field):
        """
        Function for picking a square based on the general safety value of it.
        """

        l.debug("Choosing best valued square.")
        l.debug("Chose: {}".format(self._best_valued_square_wrapper.coordinates))

        return self._best_valued_square_wrapper.square
