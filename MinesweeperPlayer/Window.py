import win32gui, win32api, win32con
import pyscreenshot as ImageGrab
import time

class Window():
    _window_name = "Minesweeper"
    _hwdn = None

    def __init__(self):
        if self.is_open():
            self.update_window_handle()

    def is_open(self):
        open = True
        # Test wheter the window is actually open.
        try:
            hwnd = self.get_window_handle()
            bounds = self.get_window_bounds()
        except Exception:
            open = False
        return open

    def update_window_handle(self):
        self._hwnd = self.get_window_handle();

    def get_window_bounds(self):
        rect = win32gui.GetWindowRect(self._hwnd)
        # Topleft, topright, bottomright, bottomleft
        return rect[0], rect[1], rect[2], rect[3]

    def get_window_handle(self):
        return win32gui.FindWindow(None, self._window_name)

    def focus_window(self):
        win32gui.SetForegroundWindow(self._hwnd)

    def get_window_image(self):
        bounds = self._get_window_bounds(self._hwnd)

        focus_window(self._hwnd)
        # Time needed for the window to appear on top.
        time.sleep(.1)
    
        image = ImageGrab.grab(bbox=(bounds))
        return image

    def move_mouse(self, pos):
        win32api.SetCursorPos(pos)

    def click_mouse(self, pos):
        self.move_mouse(pos)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, *pos, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, *pos, 0, 0)