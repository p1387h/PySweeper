from Window import *

import cv2
import numpy as np
import imutils

class OpenCV:
    """
    Class used for extracting information from the window the 
    Minesweeper game is currently running in by performing 
    template matching.
    """

    _template_paths = []
    _templates = []

    def __init__(self):
        pass

    def load_templates(self):
        pass

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
