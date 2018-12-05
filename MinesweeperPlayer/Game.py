from Square import *
from FieldState import *
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

    _current_state = FieldState.UNCHANGED
    _open_cv = None

    # The current field.
    current_field_info = None
    # The fields whose state differed during the comparion.
    changed_fields = []

    def __init__(self):
        pass

    def update(self, window):
        # Force loading the logging configuration before any 
        # instances are generated.
        if self._open_cv is None:
            self._open_cv = OpenCV()

        # Update the field information using OpenCV.
        image = window.get_window_image()
        new_field_info = self._open_cv.get_field_information(image)
        self._current_state = self.compare_and_update_field_info(new_field_info)

    def compare_and_update_field_info(self, field_info):
        resulting_field_state = FieldState.UNCHANGED

        l.debug("Checking for differences...")

        # Previous changes must be reset.
        self.changed_fields.clear()

        # First update cycle.
        if self.current_field_info is None:
            self.current_field_info = field_info
            resulting_field_state = FieldState.CHANGED

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

                        resulting_field_state = FieldState.CHANGED

                        # Keep track of the changes on the field.
                        square_change = SquareChange(old_square, new_square, row_index, column_index)
                        self.changed_fields.append(square_change)

            # Update the field state such that the new one can be 
            # retrieved.
            self.current_field_info = field_info

        if resulting_field_state is FieldState.CHANGED:
            l.info("Field state differs.")

        return resulting_field_state

    def is_finished(self):
        return self._current_state is FieldState.FINISHED

    def has_changed(self):
        return self._current_state is FieldState.CHANGED

    def reset_field_state(self):
        self._current_state = FieldState.UNCHANGED