from Square import *
from FieldState import *
from Window import *

class Game:
    _field = None
    _current_state = FieldState.UNCHANGED

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