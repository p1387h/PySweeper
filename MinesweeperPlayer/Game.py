from Square import *
from FieldState import *
from Window import *
from OpenCV import *

class Game:
    """
    Container class for all game relevant information. This class 
    stores all informations regarding the current state of the 
    game like the individual fields or changes that occurred (i.e.
    after clicking a square).
    """

    _field = None
    _current_state = FieldState.UNCHANGED
    _open_cv = OpenCV()

    def __init__(self):
        pass

    def update(self, window):
        pass

    def compare_fields(self):
        pass

    def is_finished(self):
        return self._current_state is FieldState.FINISHED

    def has_changed(self):
        return self._current_state is FieldState.CHANGED