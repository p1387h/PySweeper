from Window import *
from Square import *
from pathlib import Path

import cv2
import numpy as np
import imutils
import os
import logging as l

_unchecked_keys = [
    "udark", "umedium", "ulight"
]
_checked_keys = [
    "c0", "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8"
]

class OpenCV:
    """
    Class used for extracting information from the window the 
    Minesweeper game is currently running in by performing 
    template matching.
    """

    # Properties used for displaying the OpenCV results in a separate window.
    _show_template_matching_results = True
    _unchecked_window_name = "Unchecked Window Result"
    _checked_window_name = "Checked Window Result"
    _unchecked_image = None
    _checked_image = None

    # Paths to the templates that are being used for template matching.
    _template_paths = {
        _unchecked_keys[0]: "resources/squares_unchecked/square_dark.png",
        _unchecked_keys[1]: "resources/squares_unchecked/square_medium.png",
        _unchecked_keys[2]: "resources/squares_unchecked/square_light.png",
        _checked_keys[0]: "resources/squares_checked/square_empty.png",
        _checked_keys[1]: "resources/squares_checked/square_1.png",
        _checked_keys[2]: "resources/squares_checked/square_2.png",
        _checked_keys[3]: "resources/squares_checked/square_3.png",
        _checked_keys[4]: "resources/squares_checked/square_4.png",
        _checked_keys[5]: "resources/squares_checked/square_5.png",
        _checked_keys[6]: "resources/squares_checked/square_6.png",
        _checked_keys[7]: "resources/squares_checked/square_7.png",
        _checked_keys[8]: "resources/squares_checked/square_8.png",
    }
    _used_unchecked_template_key = _unchecked_keys[0]

    # {key: template, ...}
    _templates = {}

    # Thresholds for the different kinds of template matchings that 
    # are performed by this class.
    _thresholds = {
        _unchecked_keys[0]: 0.735,
        _unchecked_keys[1]: 0.735,
        _unchecked_keys[2]: 0.735,
        _checked_keys[0]: 0.875,
        _checked_keys[1]: 0.63,
        _checked_keys[2]: 0.55,
        _checked_keys[3]: 0.69,
        _checked_keys[4]: 0.69,
        _checked_keys[5]: 0.6,
        _checked_keys[6]: 0.69,
        _checked_keys[7]: 0.69,
        _checked_keys[8]: 0.75,
    }

    # Mapped values for the different squares.
    _mapped_values = {
        _checked_keys[0]: 0,
        _checked_keys[1]: 1,
        _checked_keys[2]: 2,
        _checked_keys[3]: 3,
        _checked_keys[4]: 4,
        _checked_keys[5]: 5,
        _checked_keys[6]: 6,
        _checked_keys[7]: 7,
        _checked_keys[8]: 8,
    }

    # Coordinates / dimensions of the game field that can be used for 
    # template matching.
    _coord_top_left = None
    _coord_bottom_right = None

    def __init__(self):
        self.load_templates()

    def load_templates(self):
        """
        Function for loading the templates from the resource folder.
        """

        self._templates.clear()
        current_dir = os.getcwd()

        l.info("Loading templates...")

        # Check all paths and their corresponding templates.
        for key, path in self._template_paths.items():
            try:
                complete_path = str(Path(current_dir) / path)
                template = cv2.imread(complete_path, 0)
                
                l.debug(f"- {path}")
                self._templates[key] = template
            except Exception as e:
                l.error(f"Exception while loading {path}: {e}")

    def init_image_coordinates(self, image):
        """
        Function for initializing the top left and bottom right coordinates of the 
        game's field. This uses the unchecked squares in order to determine the 
        dimensions of the field.
        """

         # Extract the needed information from the image and apply them.
        ratio, points, template = list(self.extract_unchecked(image).values())[0]
        
        # Update is performed using all unchecked points in order to 
        # address all possible squares.
        top_corner_points = self.convert_to_corners(points, self._used_unchecked_template_key)
        self.update_image_coordinates(top_corner_points, *map(lambda x: int(x * ratio), template.shape[::-1]))

    def update_image_coordinates(self, points, additional_width = 0, additional_height = 0):
        """
        Function for updating the top left and bottom right coordinates of the 
        game's field.
        """

        # Find top left and bottom right coordinates.
        top_left = None
        bottom_right = None

        for point in points:
            point_bottom_x = point[0] + additional_width
            point_bottom_y = point[1] + additional_height

            if top_left is None:
                top_left = point
            if bottom_right is None:
                bottom_right = point_bottom_x, point_bottom_y

            if point[0] < top_left[0]:
                top_left = point[0], top_left[1]
            if point[1] < top_left[1]:
                top_left = top_left[0], point[1]
            if point_bottom_x >= bottom_right[0]:
                bottom_right = point_bottom_x, bottom_right[1]
            if point_bottom_y >= bottom_right[1]:
                bottom_right = bottom_right[0], point_bottom_y

        l.info("Updating field dimensions to {}, {}".format(top_left, bottom_right))

        self._coord_top_left = top_left
        self._coord_bottom_right = bottom_right

    def prepare_image(self, image, use_canny = False, canny_params = (50, 200), use_cropped_image = False):
        """
        Function for converting a taken screenshot of the game's
        window into a usable form.
        """

        # Crop the image if necessary. Can be used for correctly match 
        # numbers on the screen.
        if use_cropped_image:
            image = image.crop((*self._coord_top_left, *self._coord_bottom_right))

        # Convert PIL image to opencv one.
        open_cv_image = np.array(image) 
        # Convert RGB to BGR 
        open_cv_image = open_cv_image[:, :, ::-1].copy() 
        # Grayscale the image in order to work with the loaded template.
        gray_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

        # Usage of the canny edge detection algorithm is advised when 
        # matching numbers.
        if use_canny:
            gray_image = cv2.Canny(gray_image, *canny_params)
        
        return (open_cv_image, gray_image)

    def is_finished(self, image):
        pass

    def get_field_information(self, image):
        """
        Function for extracting the game information (values, bombs, checked / unchecked)
        from a provided image.
        """
        
        l.debug("Extracting field information...")

        # The coordinates need to be set once in order for the checked 
        # template matching to properly work.
        if self._coord_top_left is None or self._coord_bottom_right is None:
            self.init_image_coordinates(image)

        # Results of the different template matchings must be combined in order to 
        # properly display them all.
        results_unchecked = self.extract_unchecked(image)
        results_checked = self.extract_checked(image)
        results = {**results_unchecked, **results_checked}

        # Filter all points based on their coordinates such that no points 
        # of the same type overlap.
        filtered_results = {}
        for key in results.keys():
            l.debug("Filtering for key '{}'".format(key))

            ratio, points, template = results[key]
            tolerance = int(ratio * max(*template.shape[::-1]))
            width, height = template.shape[::-1]
            filtered_points = self.filter_points(points, width, height, distance_tolerance = tolerance)
            filtered_results[key] = ratio, filtered_points, template

        # Create a matrix of squares that represents the game field.
        square_tuples = self.transform_into_square_tuples(filtered_results)
        square_matrix = self.transform_into_square_matrix(square_tuples)

        # Crude display of the result.
        l.debug("Extraction results: {} rows with {} columns".format(len(square_matrix), list(map(lambda x: len(x), square_matrix))))
        for row in square_matrix:
            line = ""
            for column in row:
                if column.is_unchecked:
                    line += " "
                else:
                    line += str(column.value)
            l.debug(line)

        # OpenCV window for template matching results.
        if self._show_template_matching_results:
            self._unchecked_image = self.prepare_image(image)[0]
            self._checked_image = self.prepare_image(image)[0]

            for key, (ratio, points, template) in filtered_results.items():
                if key in _unchecked_keys:
                    self.display_centers(self._unchecked_image, points)
                elif key in _checked_keys:
                    self.display_centers(self._checked_image, points)

            cv2.imshow(self._unchecked_window_name, self._unchecked_image)
            cv2.imshow(self._checked_window_name, self._checked_image)
            cv2.moveWindow(self._unchecked_window_name, 10, 10)
            cv2.moveWindow(self._checked_window_name, 650, 10)
            cv2.waitKey(1)

        return square_matrix

    def transform_into_square_tuples(self, template_matching_results):
        """
        Function for transforming all points into Squares. Does NOT remove 
        the ratio and template information since they are needed later on.
        """

        square_tuples = []

        for key in template_matching_results.keys():
            ratio, points, template = template_matching_results[key]
            for point in points:
                square = Square(point)

                if key in _unchecked_keys:
                    square.is_unchecked = True
                    square.value = None
                elif key in _checked_keys:
                    square.is_unchecked = False
                    square.value = self._mapped_values[key]
                square_tuples.append((ratio, template, square))

        return square_tuples

    def transform_into_square_matrix(self, square_tuples):
        """
        Function for creating a matrix (list of lists) that represents the 
        game's field (accessible by: [row][column]).
        """

        # Sorted by rows (Y).
        sorted_square_tuples = sorted(square_tuples, key = lambda square_tuple: square_tuple[2].center_coordinates[1])

        # Y values can differ. Therefore they must be normalized for each row 
        # such that only a single value exists for each one.
        template_heights = map(lambda tuple: tuple[1].shape[0] * tuple[0], square_tuples)
        # The distance at which rows are combined.
        combine_distance = int(max(*template_heights) / 2)
        adjusted_squares = []
        current_row_y = None
        current_row_index = 0

        for square_tuple in sorted_square_tuples:
            ratio, template, square = square_tuple

            # First entry to be adjusted.
            if current_row_y is None:
                current_row_y = square.center_coordinates[1]
                adjusted_squares.append([square])
            else:
                square_y = square.center_coordinates[1]
                y_difference = square_y - current_row_y

                # Same row (works the same if the square_y is smaller than the 
                # current_row_y).
                if y_difference < combine_distance:
                    square.center_coordinates = square.center_coordinates[0], current_row_y
                    adjusted_squares[current_row_index].append(square)
                # Next row below the current one.
                else:
                    current_row_index += 1
                    current_row_y = square.center_coordinates[1]
                    adjusted_squares.append([square])

        # Sort by columns (X)
        # Note:
        # The X values still differ from row to row as only the Y ones are normalized!
        for row in adjusted_squares:
            row.sort(key = lambda square: square.center_coordinates[0])

        return adjusted_squares

    def display_squares(self, open_cv_image, adjusted_squares, color = (0, 0, 255)):
        """
        Function for displaying squares in a single window.
        """

        for rect in adjusted_squares:
            cv2.rectangle(open_cv_image, rect[0], rect[1], color, 1)

    def display_centers(self, open_cv_image, centers, color = (255, 0, 0), radius = 2):
        """
        Function for displaying centers in a single window.
        """

        for center in centers:
            circle_center = (center[0] - radius // 2, center[1] - radius // 2)
            cv2.circle(open_cv_image, circle_center, radius, color, -1)

    def extract_unchecked(self, image):
        """
        Function for extracting all points matching the unchecked template 
        as well as the scling ratio for them.
        """

        result = self.extract(image, [self._used_unchecked_template_key])
        return result;

    def extract_checked(self, image):
        """
        Function for extracting all points matching the checked template 
        as well as the scling ratio for them.
        """

        result_empty = self.extract(image, _checked_keys[:1])
        result_numbers = self.extract(image, _checked_keys[1:], use_canny = True, canny_params = (275, 320), use_cropped_image = True)

        # Adjust the points since a cropped image is used. The coordinates 
        # received previously do not match the uncropped image.
        # item[0] == key
        # item[1] == value == tuple
        mapping_function = lambda item: (item[0], (item[1][0], self.adjust_cropped_points(item[1][1]), item[1][2]))
        adjusted_result_numbers = list(map(mapping_function, result_numbers.items()))

        result = {**result_empty, **dict(adjusted_result_numbers)}
        return result

    def extract(self, image, keys, adjust_points_to_match_image = True, use_canny = False, canny_params = (50, 200), use_cropped_image = False):
        """
        Function for extracting points by applying a template match on 
        a provided image with a templated accessible via the provided 
        key.
        """

        results = {}

        for key in keys:
            template = self._templates[key]

            l.debug("Extracting: {}".format(key))

            # Use the opencv template matching for finding the desired points.
            open_cv_image, gray_image = self.prepare_image(image, use_canny = use_canny, canny_params = canny_params, use_cropped_image = use_cropped_image)
            points, ratio = self.match_scaling_with_template(key, gray_image, use_canny = use_canny, canny_params = canny_params)

            # When adjusting the points, only the points themselves are of interest 
            # since the ratio is also returned (template shape * ratio = used shape).
            if adjust_points_to_match_image:
                points, width, height = self.adjust_template_values_based_on_ratio(points, ratio, key)

            results[key] = ratio, points, template

        return results

    def match_scaling_with_template(self, template_key, gray_image, convert_to_center = True, use_canny = False, canny_params = (50, 200)):
        """
        Function for matching the image with the template accessible by 
        the provided template_key. This function scales the image in 
        order to match different window sizes with the same template.
        """

        threshold = self._thresholds[template_key]
        best_matching = None
        template = self._templates[template_key]
        template_height, template_width = template.shape[:2]

        ## Gradually scale the image down.
        #for scale in np.linspace(0.1, 1.0, 20)[::-1]:
        #    # Resize the image in order to match the template's size.
        #    # shape[1] is the width of the image
        #    resized_gray_image = imutils.resize(gray_image, int(gray_image.shape[1] * scale))
        #    ratio = gray_image.shape[1] / float(resized_gray_image.shape[1])

        #    # Image must not be smaller than the template.
        #    if resized_gray_image.shape[0] < template_height or resized_gray_image.shape[1] < template_width:
        #        break

        #    # Usage of the canny edge detection algorithm is advised when 
        #    # matching numbers.
        #    if use_canny:
        #        template = cv2.Canny(template, *canny_params)

        #    # Template matching.
        #    result = cv2.matchTemplate(resized_gray_image, template, cv2.TM_CCOEFF_NORMED)
        #    locations = np.where(result >= threshold)
        #    points = list(zip(*locations[::-1]))

        #    # All of the squares must be matched (Error prone!).
        #    if best_matching is None or len(best_matching[0]) < len(points):
        #        best_matching = points, ratio

        # Usage of the canny edge detection algorithm is advised when 
        # matching numbers.
        if use_canny:
            template = cv2.Canny(template, *canny_params)

        # Template matching.
        result = cv2.matchTemplate(gray_image, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        points = list(zip(*locations[::-1]))
        best_matching = points, 1.0

        l.debug("Best matching: {} points, {} ratio".format(len(best_matching[0]), best_matching[1]))

        # Top left corner can be converted to the center of the template.
        if convert_to_center:
            l.debug("Converting corners to centers...")
            centers = self.convert_to_centers(best_matching[0], template_key)
            best_matching = centers, best_matching[1]

        return best_matching

    def convert_to_centers(self, points, template_key):
        """
        Function for converting a collection of points (top left) to 
        centers using a template.
        """

        template = self._templates[template_key]
        template_width, template_height = template.shape[::-1]
        centers = list(map(lambda point: (point[0] + template_width // 2, point[1] + template_height // 2), points))

        return centers

    def convert_to_corners(self, points, template_key):
        """
        Function for converting a collection of points (centers) to 
        top left corner points using a template.
        """

        template = self._templates[template_key]
        template_width, template_height = template.shape[::-1]
        corners = list(map(lambda point: (point[0] - template_width // 2, point[1] - template_height // 2), points))

        return corners

    def adjust_template_values_based_on_ratio(self, points, ratio, template_key):
        """
        Function for adjusting the existing template's values based on a 
        returned ratio. The points and sizes received from the template 
        matching must be changed to match the base image dimensions. A 
        template matching a region of the image while the latter is scaled 
        down must be scaled up in order to properly match it again.
        """

        template = self._templates[template_key]
        template_width, template_height = template.shape[::-1]
        
        adjusted_points = list(map(lambda point: (int(point[0] * ratio), int(point[1] * ratio)), points))
        adjusted_width = int(template_width * ratio)
        adjusted_height = int(template_height * ratio)

        return adjusted_points, adjusted_width, adjusted_height

    def adjust_cropped_points(self, points):
        """
        Function for applying the offset created by template matching 
        a cropped image. Since the positions returned by this do not 
        correctly match the uncropped image, the corrdinates must be 
        adjusted.
        """

        adjusted_points = list(map(lambda point: (point[0] + self._coord_top_left[0], point[1] + self._coord_top_left[1]), points))
        return adjusted_points

    def filter_points(self, points, width, height, distance_tolerance = 6):
        """
        Function for filtering the points based on the distance to one another 
        such that only a single point for each square remains.
        """

        l.debug("Filtering {} points...".format(len(points)))

        # Calculate the dimensions of the available space.
        total_width = self._coord_bottom_right[0] - self._coord_top_left[0]
        total_height = self._coord_bottom_right[1] - self._coord_top_left[1]

        # Generate cubes based on the desired distance between the points.
        cube_side_length = int(distance_tolerance / 2)
        cube_count_x = total_width // cube_side_length
        cube_count_y = total_height // cube_side_length

        # Cube matrix.
        cubes = []
        # +1 in both cases to make sure no out of bound exceptions are thrown.
        for row in range(0, cube_count_y + 1):
            cubes.append([None for column in range(0, cube_count_x + 1)])

        for point in points:
            # max is used to prevent accessing indices from the last position (i.e. -1)
            new_x = max(0, point[0] - self._coord_top_left[0])
            new_y = max(0, point[1] - self._coord_top_left[1])
            index_x = new_x // cube_side_length
            index_y = new_y // cube_side_length
            cube = cubes[index_y][index_x]
            
            # Check the neighbouring cubes.
            neighbours = [cube]
            left_x = index_x - 1
            center_x = index_x
            right_x = index_x + 1
            top_y = index_y - 1
            center_y = index_y
            bottom_y = index_y + 1

            # Checks are needed since Python does not throw exceptions when 
            # accessing indices like -1 etc. but instead reads elements from 
            # the end of the list.
            # Left side of the target.
            if left_x >= 0:
                if top_y >= 0:
                    neighbours.append(cubes[top_y][left_x])
                if center_y >= 0:
                    neighbours.append(cubes[center_y][left_x])
                if bottom_y < len(cubes):
                    neighbours.append(cubes[bottom_y][left_x])
            # Top and bottom of the target.
            if center_x >= 0:
                if top_y >= 0:
                    neighbours.append(cubes[top_y][center_x])
                if bottom_y < len(cubes):
                    neighbours.append(cubes[bottom_y][center_x])
            # Right side of the target.
            if right_x < len(cubes[0]):
                if top_y >= 0:
                    neighbours.append(cubes[top_y][right_x])
                if center_y >= 0:
                    neighbours.append(cubes[center_y][right_x])
                if bottom_y < len(cubes):
                    neighbours.append(cubes[bottom_y][right_x])

            # Neighbours and the target must be checked in order to determine 
            # whether the point can be used.
            point_is_acceptable = True
            for other_point in neighbours:
                if other_point is not None:
                    point_is_acceptable = False
                    break
            if point_is_acceptable:
                cubes[index_y][index_x] = point

        # Extract all points from the cubes.
        filtered_points = []
        for row in cubes:
            for stored_point in row:
                if stored_point is not None:
                    filtered_points.append(stored_point)

        l.debug("{} points remain after filtering.".format(len(filtered_points)))
        return filtered_points