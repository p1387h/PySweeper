class Square:
    """
    A square inside the Minesweeper game. Can either be checked (=clicked)
    or unchecked (=no clicked). Different fields contain different values.
    """

    center_coordinates = None
    value = None
    is_bomb = None
    is_unchecked = None

    def __init__(self, center_coordinates = (0, 0), value = -1, is_bomb = False, is_unchecked = True):
        self.center_coordinates = center_coordinates
        self.value = value
        self.is_bomb = is_bomb
        self.is_unchecked = is_unchecked