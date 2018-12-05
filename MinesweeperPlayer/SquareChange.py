from Square import *

class SquareChange:
    """
    Class containing the changes that occurred on the game field.
    """
    
    old_square = None
    new_square = None
    row_index = -1
    column_index = -1

    def __init__(self, old_square, new_square, row_index, column_index):
        self.old_square = old_square
        self.new_square = new_square
        self.row_index = row_index
        self.column_index = column_index