import win32gui, win32api, win32con
import pyscreenshot as ImageGrab
import time as t

class Window:
    """
    Class for interacting with the Minesweeper game itself. Used for
    extracting information from it by calling system level functions 
    and interacting with the application itself.
    """

    _window_name = "Minesweeper"
    _hwnd = None

    def __init__(self):
        if self.is_open():
            self.update_window_handle()

    def is_open(self):
        """
        Function for checking if the Minesweeper window is actually 
        openend. Must be used since otherwise the window specific 
        actions throw exceptions.
        """

        open = True
        # Test wheter the window is actually open.
        try:
            self.update_window_handle()
            hwnd = self.get_window_handle()
            bounds = self.get_window_bounds()
            pass
        except Exception:
            open = False
        return open

    def update_window_handle(self):
        """
        Function for updating the window handle to the Minesweeper game.
        """

        self._hwnd = self.get_window_handle();

    def get_window_bounds(self):
        """
        Function for retrieving the game's bounds. These are returned in 
        a Tuple as follows:
        (topleft, topright, bottomright, bottomleft)
        """

        rect = win32gui.GetWindowRect(self._hwnd)
        return rect[0], rect[1], rect[2], rect[3]

    def get_window_handle(self):
        """
        Function for retrieving the window handle to the Minesweeper 
        window.
        """

        return win32gui.FindWindow(None, self._window_name)

    def focus_window(self):
        """
        Function for focusing the Minesweeper game's window.
        """

        win32gui.SetForegroundWindow(self._hwnd)

    def get_window_image(self):
        """
        Function for retrieving an image of the Minesweeper game's 
        window in the PIL (Pillow) format.
        """

        bounds = self.get_window_bounds()

        self.focus_window()
        # Time needed for the window to appear on top.
        t.sleep(0.001)
    
        image = ImageGrab.grab(bbox=(bounds))
        return image

    def move_mouse(self, pos, is_relative = True, x_offset = -8, y_offset = -48):
        """
        Function for moving the mouse on the screen.
        """

        if is_relative:
            # Magic numbers include the offset created by taking an image of 
            # the whole application window, which also includes the upper 
            # menu bar. The windows client to screen function on the other 
            # hand does not take these in consideration, which is why a 
            # manual offset must be applied here.
            pos = win32gui.ClientToScreen(self._hwnd, (pos[0] + x_offset, pos[1] + y_offset))

        win32api.SetCursorPos(pos)

    def click_mouse(self, pos):
        """
        Function for performing a mouseclick on the screen.
        """

        self.move_mouse(pos)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, *pos, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, *pos, 0, 0)