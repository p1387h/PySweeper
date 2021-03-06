from Square import *

class SquareWrapper:
    """
    Wrapper class for Squares. Needed for calculating scores and values 
    based on the current state of the game (i.e. possibilities of picking 
    a bomb) and keeping them stored in a container.
    """
    
    square = None

    # The value that the square has after removing all bomb squares. 
    effective_value = -1
    # Flag for reducing the effective value of adjacent squares. Once 
    # a square is decided to contain a bomb, no more reductions must 
    # take place.
    # Can be interpreted as "is a bomb".
    has_reduced_neighbours = False
    adjacent_bombs = []
    adjacent_safe_squares = []
    # Lower score == better since it resembles the possibility of a bomb
    # being chosen. Is between 0 and 8.
    score = 0
    # The score with which each unchecked score affects its neighbours.
    _unchecked_score_effect = 1

    # The squares that are affected by this one. This includes all 
    # squares (X) around this one (O). I.e.:
    # X X X
    # X O X
    # X X X
    _affected_square_coordinates = []
    _affected_square_wrappers = {}

    # The row and column index of the suqare itself. Can be used for 
    # checking whether to react to an update.
    coordinates = -1, -1

    def __init__(self, square, affected_square_coordinates, coordinates):
        self.square = square
        self.effective_value = square.value
        self._affected_square_coordinates = affected_square_coordinates
        self.coordinates = coordinates

        # Must be initialized here since they are otherwise shared between 
        # all instances.
        self._affected_square_wrappers = {}
        self.adjacent_bombs = []
        self.adjacent_safe_squares = []

    def map_wrappers(self, wrappers):
        """
        Function for mapping the previously set coordinates of the other 
        square wrappers to the specific instances. Provides an easy way 
        for the wrappers to interact with one another without providing 
        the map each time.
        """

        for coordinate in self._affected_square_coordinates:
            self._affected_square_wrappers[coordinate] = wrappers[coordinate]

    def update_effective_value(self):
        """
        Function for updating the effective values for each wrapper based 
        on the direct neighbours of this square. Each neighbour reduces the 
        values of neighbouring tiles if necessary (if itself is a bomb).
        """

        if self.is_value_completely_assigned():
            for wrapper in self.extract_unchecked_neighbours():
                if not wrapper.has_reduced_neighbours:
                    wrapper.has_reduced_neighbours = True
                    wrapper.reduce_neighbours()

    def is_value_completely_assigned(self):
        """
        Function for checking if a square has completely matched its value with 
        unchecked neighbouring squares. All remaining squares are bombs.
        """

        # Unchecked or 0 are ignored.
        result = False

        if not(self.square.value is None) and self.square.value > 0:
            unchecked_count = len(self.extract_unchecked_neighbours())
            bomb_count = self.square.value
            result = unchecked_count == bomb_count
        return result

    def extract_unchecked_neighbours(self):
        """
        Function for extracting all unchecked neighbours from this square.
        """

        return list(filter(lambda wrapper: wrapper.square.is_unchecked, self._affected_square_wrappers.values()))

    def reduce_neighbours(self):
        """
        Function for reducing the effective value of each neighbour. Needed 
        if the current square contains a bomb.
        """

        for wrapper in self._affected_square_wrappers.values():
            wrapper.reduce_effective_value(self)

    def reduce_effective_value(self, bomb_square_wrapper):
        """
        Function for reducing the effective value of this square. Must 
        be called when an adjacent square is considered to be a bomb.
        """

        self.adjacent_bombs.append(bomb_square_wrapper)

        if not self.effective_value is None:
            self.effective_value -= self._unchecked_score_effect

            # All remaining squares are safe.
            if self.effective_value == 0:
                for safe_square in filter(lambda wrapper: not(wrapper in self.adjacent_bombs) and wrapper.square.is_unchecked, self._affected_square_wrappers.values()):
                    self.adjacent_safe_squares.append(safe_square)

    def update_score(self, indices, max_indices):
        """
        Function for updating the score of this square as well as the scores 
        around this one.
        """

        self.update_own_score(*indices, *max_indices)
        self.update_neighbour_scores()

    def update_neighbour_scores(self):
        """
        Function for updating the scores of neighbours.
        """

        neighbours = self.extract_unchecked_neighbours()
        score_for_each = 0

        # Unchecked squares.
        if self.effective_value is None:
            score_for_each = self._unchecked_score_effect
        # Checked squares without value.
        elif self.effective_value == 0:
            score_for_each = 0
        else:
            score_for_each = self.effective_value / len(neighbours)

        for wrapper in neighbours:
            wrapper.score += score_for_each

    def update_own_score(self, row_index, column_index, max_row_index, max_column_index):
        """
        Function for updating the score of this square based on its location.
        Squares on the edge must be given extra points since they cant be updated 
        by the non existent squares outside the game field. I.e.:
        O = outside
        X = inside the game field
        T = target field

        O O O
        O T X
        O X X

        Due to all squares updating their neighbours, the target square (T) would 
        not receive scores from five sources (O).
        """

        extra_score_multiplier = 0

        # Left / Right
        if column_index == 0 or column_index == max_column_index:
            extra_score_multiplier += 3

            # Left-Top / Left-Bottom / Right-Top / Right-Bottom
            if row_index == 0 or row_index == max_row_index:
                extra_score_multiplier += 2
        # Top / Bottom
        elif row_index == 0 or row_index == max_row_index:
            extra_score_multiplier += 3

        # Apply the effect of outside fields to the square's score.
        extra_score = self._unchecked_score_effect * extra_score_multiplier
        self.score += extra_score