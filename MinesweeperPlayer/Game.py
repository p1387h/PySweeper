from Square import *
from Window import *
from OpenCV import *
from SquareChange import *

class Game:
    """
    Container class for all game relevant information. This class 
    stores all informations regarding the current state of the 
    game like the individual fields or changes that occurred (i.e.
    after clicking a square).
    """

    _open_cv = OpenCV()

    # The initial square locations at the beginning of the game.
    _initial_squares = []
    # The width of a single square on the game field.
    _initial_square_width = 0

    # The current field.
    current_field_info = None
    # The fields whose state differed during the comparion.
    changed_fields = []

    is_finished = False

    def __init__(self):
        self._open_cv = OpenCV()

    def update_field_dimensions(self, window):
        """
        Function for udpating the game's field dimesions like number of squares, 
        rows, columns and the individual size of each square.
        """

        l.debug("Updating field dimensions...")

        image = window.get_window_image()
        self._initial_squares = self._open_cv.get_field_information(image)

        distances = []
        for row in self._initial_squares:
            prev_next_tuples = zip(row[:-1], row[1:])
            distances += list(map(lambda tuple: tuple[1].center_coordinates[0] - tuple[0].center_coordinates[0], prev_next_tuples))

        # Minimum since the distance is compared in such a way that the program 
        # tests if a square can be inserted based on the distance between two 
        # coordinates.
        self._initial_square_width = min(distances)

    def update(self, window):
        """
        Function for updating the current state of the game. The field as well as any 
        other relevenat information (changes, etc.) are gathered here.
        """

        # Update the field information using OpenCV.
        l.debug("Getting window image...")
        image = window.get_window_image()
        l.debug("Getting field information...")
        self.is_finished = self._open_cv.is_finished(image)

        if not self.is_finished:
            new_field_info = self._open_cv.get_field_information(image)
            self.fill_empty_spaces(new_field_info)
            self.compare_and_update_field_info(new_field_info)

    def fill_empty_spaces(self, field_info):
        l.debug("Filling empty spaces with zeroes...")

        # Fill any empty spots with the previously extracted coordinates such that 
        # the result is the complete game field.
        for row_index in range(0, len(self._initial_squares)):
            for column_index in range(0, len(self._initial_squares[row_index])):
                stored = self._initial_squares[row_index][column_index]
                checked_stored = Square(stored.center_coordinates, 0, False)
                
                # Empty fields at the ends must be added manually.
                if column_index >= len(field_info[row_index]):
                    field_info[row_index].append(checked_stored)
                else:
                    new = field_info[row_index][column_index]
                    difference_x = abs(new.center_coordinates[0] - stored.center_coordinates[0])

                    # Distance greater than the previously calculated distance means 
                    # that an entry is missing here.
                    if difference_x >= self._initial_square_width:
                        field_info[row_index].insert(column_index, checked_stored)

        # Crude display of the result.
        l.debug("Filling results: {} rows with {} columns".format(len(field_info), list(map(lambda x: len(x), field_info))))
        for row in field_info:
            line = ""
            for column in row:
                if column.is_unchecked:
                    line += "?"
                else:
                    line += str(column.value)
            l.debug(line)

    def compare_and_update_field_info(self, field_info):
        """
        Function for updating the collection of fields that changed compared 
        to the stored ones.
        """

        l.debug("Checking for differences...")

        # Previous changes must be reset.
        self.changed_fields.clear()
        change_occurred = False

        # First update cycle.
        if self.current_field_info is None:
            self.current_field_info = field_info
            change_occurred = True

            l.info("Field state initialized.")
        # Each square must be compared in order to determine whether 
        # a change occurred. Checking the field representing the checked 
        # property is enough since the values of the squares do not change.
        else:
            # Row and column count match the entire game.
            for row_index in range(0, len(self.current_field_info)):
                for column_index in range(0, len(self.current_field_info[row_index])):
                    old_square = self.current_field_info[row_index][column_index]
                    new_square = field_info[row_index][column_index]

                    if old_square.is_unchecked and not new_square.is_unchecked:
                        l.debug("Field state differs at [{}][{}]. value={}".format(row_index, column_index, new_square.value))

                        # Keep track of the changes on the field.
                        square_change = SquareChange(old_square, new_square, row_index, column_index)
                        self.changed_fields.append(square_change)
                        change_occurred = True

            # Update the field state such that the new one can be 
            # retrieved.
            self.current_field_info = field_info

        if change_occurred:
            l.info("Field state differs.")

        return change_occurred