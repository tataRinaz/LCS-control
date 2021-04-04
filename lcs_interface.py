from tkinter import *

from statistics_ui import StatisticsUI
from standalone_ui import StandaloneUI

COLOR = 'grey'
BUTTON_HEIGHT = 15
BUTTON_WIDTH = 15


class MainWindow:
    def __init__(self, window_height=900, window_width=600, window_position_height=600, window_position_width=400):
        self._window_height = window_height
        self._window_width = window_width
        self._window_position_height = window_position_height
        self._window_position_width = window_position_width
        self._buttons = []
        self._root = Tk()
        self._statistics_frame = StatisticsUI(root=self._root, height=self._window_height, width=self._window_width,
                                              change_frame_cb=self.on_change_frame_clicked)
        self._standalone_frame = StandaloneUI(root=self._root, height=self._window_height, width=self._window_width,
                                              change_frame_cb=self.on_change_frame_clicked)
        self._current_frame = self._standalone_frame
        self._pending_frame = self._statistics_frame

    def start_gui(self):
        self._root.title("LVS")
        self._root.geometry(
            f'{self._window_height}x{self._window_width}+{self._window_position_height}+{self._window_position_width}')
        self._current_frame.tkraise()
        self._root.mainloop()

    def on_change_frame_clicked(self):
        self._current_frame, self._pending_frame = self._pending_frame, self._current_frame
        self._current_frame.tkraise()
