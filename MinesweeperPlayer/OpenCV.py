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

    def prepare_image(self, image):
        pass

    def is_finished(self, image):
        pass

    def get_field_information(self, image):
        pass

    def extract_unchecked(self, image):
        pass

    def extract_checked(self, image):
        pass
