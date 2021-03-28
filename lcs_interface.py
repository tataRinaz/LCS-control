from tkinter import *
from states import DeviceState
from terminal_device import TerminalDevice
import lcs

COLOR = 'grey'
BUTTON_HEIGHT = 15
BUTTON_WIDTH = 15


class MainWindow:
    def __init__(self, window_height=900, window_width=600, window_position_height=600, window_position_width=400):
        self._window_height = window_height
        self._window_width = window_width
        self._window_position_height = window_position_height
        self._window_position_width = window_position_width
        self._lcs = lcs.LCS(4, [0.01, 0.01, 0.02, 0.01])
        self._buttons = []
        self._root = Tk()
        self._start_button = Button(self._root, {"text": "Run"},
                                    command=self._on_start_called)
        self._init_buttons()
        self._init_gui()

    def _on_start_called(self):
        self._lcs.process()

    def _init_buttons(self):
        terminals = self._lcs.get_terminals()

        x1 = 0
        y1 = 20
        x2 = 20
        y2 = 40
        for terminal in terminals:
            self._buttons.append(
                TerminalDeviceButton(self._root, x=x1, y=y1, state=DeviceState.WORKING, color="#008000",
                                     terminal_device=terminal))
            self._buttons.append(
                TerminalDeviceButton(self._root, x=x1, y=y2, state=DeviceState.BLOCKED, color="#FF0000",
                                     terminal_device=terminal))
            self._buttons.append(TerminalDeviceButton(self._root, x=x2, y=y1, state=DeviceState.DENIAL, color="#FFA500",
                                                      terminal_device=terminal))
            self._buttons.append(
                TerminalDeviceButton(self._root, x=x2, y=y2, state=DeviceState.GENERATOR, color="#C71585",
                                     terminal_device=terminal))

            x1 += 50
            x2 += 50

    def start_gui(self):
        self._root.title("LVS")
        self._root.geometry(
            f'{self._window_height}x{self._window_width}+{self._window_position_height}+{self._window_position_width}')
        self._root.mainloop()

    def _init_gui(self):
        self._start_button.place(x=100, y=200, height=100, width=200)


class TerminalDeviceButton(Button):

    def __init__(self, root, x: int, y: int,
                 color, state, terminal_device: TerminalDevice,
                 height=BUTTON_HEIGHT, width=BUTTON_WIDTH):
        super().__init__(root, bg=COLOR, command=self.on_click)
        self.root = root
        self.pending_color = color
        self.current_state = DeviceState.INITIAL
        self.current_color = COLOR
        self.pending_state = state
        self.terminal_device = terminal_device
        self.place(x=x, y=y, height=height, width=width)

    def on_click(self):
        self.current_color, self.pending_color = self.pending_color, self.current_color
        self.current_state, self.pending_state = self.pending_state, self.current_state
        self.process_current_state()

    def process_current_state(self):
        self.configure(bg=self.current_color)
        self.terminal_device.change_state(self.current_state)
