from Window import *
from pathlib import Path

import cv2
import numpy as np
import imutils
import os
import logging as l

class OpenCV:
    """
    Class used for extracting information from the window the 
    Minesweeper game is currently running in by performing 
    template matching.
    """

    _unchecked_window_name = "Unchecked Window Result"
    _checked_window_name = "Checked Window Result"

    _template_paths = {
        "udark": "resources/squares_unchecked/square_dark.png",
        "umedium": "resources/squares_unchecked/square_medium.png",
        "ulight": "resources/squares_unchecked/square_light.png",
        "c0": "resources/squares_checked/square_empty.png",
        "c1": "resources/squares_checked/square_1.png",
        "c2": "resources/squares_checked/square_2.png",
        "c3": "resources/squares_checked/square_3.png",
        "c4": "resources/squares_checked/square_4.png",
        "c5": "resources/squares_checked/square_5.png",
        "c6": "resources/squares_checked/square_6.png",
        "c7": "resources/squares_checked/square_7.png",
        "c8": "resources/squares_checked/square_8.png",
    }

    # {key: template, ...}
    _templates = {}

    # Thresholds for the different kinds of template matchings that 
    # are performed by this class.
    _unchecked_threshold = 0.725
    _checked_empty_threshold = 0.85
    _checked_number_threshold = 0.815

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

    def prepare_image(self, image):
        """
        Function for converting a taken screenshot of the game's
        window into a usable form.
        """

        # Convert PIL image to opencv one.
        open_cv_image = np.array(image) 
        # Convert RGB to BGR 
        open_cv_image = open_cv_image[:, :, ::-1].copy() 
        # Grayscale the image in order to work with the loaded template.
        gray_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        
        return (open_cv_image, gray_image)

    def is_finished(self, image):
        pass

    def get_field_information(self, image):
        """
        Function for extracting the game information (values, bombs, checked / unchecked)
        from a provided image.
        """
        
        # Extract the needed information from the image and apply them.
        unchecked_ratio, unchecked_points, unchecked_template = list(self.extract_unchecked(image).values())[0]
        
        centers = unchecked_points
        ratio = max(unchecked_ratio, unchecked_ratio)
        width, height = unchecked_template.shape[::-1]

        # Filter all points based on their coordinates such that no points overlap.
        tolerance = int(unchecked_ratio * max(*unchecked_template.shape[::-1]))
        filtered_points = self.filter_points(unchecked_points, width, height, distance_tolerance = tolerance)

        # Display the results in a window to verify them.
        open_cv_image, gray_image = self.prepare_image(image)
        self.display_centers(open_cv_image, filtered_points)
        cv2.imshow(self._unchecked_window_name, open_cv_image)
        cv2.waitKey()

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

        return self.extract(image, ["udark"], self._unchecked_threshold)

    def extract_checked(self, image):
        """
        Function for extracting all points matching the checked template 
        as well as the scling ratio for them.
        """

        checked_keys = [
            "c0", "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8"
        ]
        result_empty = self.extract(image, checked_keys[:1], self._checked_empty_threshold)
        result_numbers = self.extract(image, checked_keys[1:], self._checked_number_threshold)
        result = {**result_empty, **result_numbers}

        return result

    def extract(self, image, keys, threshold, adjust_points_to_match_image = True):
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
            open_cv_image, gray_image = self.prepare_image(image)
            points, ratio = self.match_scaling_with_template(key, gray_image, threshold)

            # When adjusting the points, only the points themselves are of interest 
            # since the ratio is also returned (template shape * ratio = used shape).
            if adjust_points_to_match_image:
                points, width, height = self.adjust_template_values_based_on_ratio(points, ratio, key)

            results[key] = ratio, points, template

        return results

    def match_scaling_with_template(self, template_key, gray_image, threshold, convert_to_center = True):
        """
        Function for matching the image with the template accessible by 
        the provided template_key. This function scales the image in 
        order to match different window sizes with the same template.
        """

        best_matching = None
        template = self._templates[template_key]
        template_height, template_width = template.shape[:2]

        # Gradually scale the image down.
        for scale in np.linspace(0.1, 1.0, 20)[::-1]:
            # Resize the image in order to match the template's size.
            # shape[1] is the width of the image
            resized_gray_image = imutils.resize(gray_image, int(gray_image.shape[1] * scale))
            ratio = gray_image.shape[1] / float(resized_gray_image.shape[1])

            # Image must not be smaller than the template.
            if resized_gray_image.shape[0] < template_height or resized_gray_image.shape[1] < template_width:
                break

            # Template matching.
            result = cv2.matchTemplate(resized_gray_image, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= threshold)
            points = list(zip(*locations[::-1]))

            # All of the squares must be matched (Error prone!).
            if best_matching is None or len(best_matching[0]) < len(points):
                best_matching = points, ratio

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


    def filter_points(self, points, width, height, distance_tolerance = 6):
        """
        Fuction for filtering the points based on the distance to one another 
        such that only a single point for each square remains.
        """

        l.info("Filering points...")
        l.debug("{} points found.".format(len(points)))

        # Find top left and bottom right coordinates.
        top_left = None
        bottom_right = None

        for point in points:
            point_bottom_x = point[0] + width
            point_bottom_y = point[1] + height

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


        # Calculate the dimensions of the available space.
        total_width = bottom_right[0] - top_left[0]
        total_height = bottom_right[1] - top_left[1]

        # Generate cubes based on the desired distance between the points.
        cube_side_length = distance_tolerance / 2
        cube_count_x = int(total_width / cube_side_length)
        cube_count_y = int(total_height / cube_side_length)

        # Cube matrix.
        cubes = []
        # +1 in both cases to make sure no out of bound exceptions are thrown.
        for row in range(0, cube_count_y + 1):
            cubes.append([None for column in range(0, cube_count_x + 1)])

        for point in points:
            # max is used to prevent accessing indices from the last position (i.e. -1)
            new_x = max(0, point[0] - top_left[0])
            new_y = max(0, point[1] - top_left[1])
            index_x = new_x // int(cube_side_length)
            index_y = new_y // int(cube_side_length)
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
                if top_y > 0:
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