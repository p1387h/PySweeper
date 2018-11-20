from Window import *

import cv2
import numpy as np
import imutils
import os, sys
import logging as l

class OpenCV:
    """
    Class used for extracting information from the window the 
    Minesweeper game is currently running in by performing 
    template matching.
    """

    _template_paths = ["resources\\squares_unchecked\\square_dark.png"]
    # [(template_information, (width, height)), ...]
    _templates = []

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
        for path in self._template_paths:
            try:
                complete_path = os.path.join(current_dir, path)
                template = cv2.imread(complete_path, 0)
                # [0] == width, [1] == height
                shape = template.shape[::-1]
                
                l.debug(f"- Loaded template {shape} from: {complete_path}")
                self._templates.append((template, shape))
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

        return gray_image

    def is_finished(self, image):
        pass

    def get_field_information(self, image):
        gray_image = self.prepare_image(image)

    def extract_unchecked(self, image):
        pass

    def extract_checked(self, image):
        pass
