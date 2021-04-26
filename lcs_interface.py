import tkinter as tk

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
        self._root = tk.Tk()
        self._root.attributes("-fullscreen", True)
        self._root.bind("<Escape>", self._on_escape_clicked)

        self.frames = {0: StatisticsUI(root=self._root,
                                       change_frame_cb=self._on_change_frame_clicked),
                       1: StandaloneUI(root=self._root,
                                       change_frame_cb=self._on_change_frame_clicked)}
        self.active_frame = 1

    def start_gui(self):
        self._root.title("LVS")
        self._root.geometry(
            f'{self._window_height}x{self._window_width}+{self._window_position_height}+{self._window_position_width}')
        self._on_change_frame_clicked()
        self._root.configure(bg="white")
        self._root.mainloop()

    def _on_escape_clicked(self, event=None):
        self._root.attributes("-fullscreen", False)

    def _on_change_frame_clicked(self):
        self.frames[self.active_frame].grid_forget()
        self.active_frame = 0 if self.active_frame == 1 else 1
        frame = self.frames[self.active_frame]
        frame.grid(row=0, column=0)
