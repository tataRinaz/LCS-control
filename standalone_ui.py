import tkinter as tk

from lcs import LCS, LCSType
from terminal_device import TerminalDevice
from states import DeviceState


class TerminalDeviceView(tk.Frame):
    def __init__(self, root, device_index, devices_cb):
        super().__init__(root)
        self.index = device_index
        self.devices_cb = devices_cb

        options = ['Рабочее', 'Отказ', 'Занят', 'Провал', 'Заблокирован', 'Генератор']

        self.device_state = tk.StringVar()
        self.states_option_menu = tk.OptionMenu(self, self.device_state, *options)
        self.states_option_menu.grid(row=0, column=0)
        self.states_change_button = tk.Button(self, text='Выбрать', command=self._process_state_change)
        self.states_change_button.grid(row=0, column=1)
        self._process_state_change()

        self.device_state_view = tk.Frame(self, bg='#000000', width=10, height=10)
        self.device_state_view.grid(row=1, column=0)

    def _process_state_change(self):
        options_map = {
            'Рабочее': DeviceState.WORKING,
            'Отказ': DeviceState.DENIAL,
            'Занят': DeviceState.BUSY,
            'Провал': DeviceState.FAILURE,
            'Заблокирован': DeviceState.BLOCKED,
            'Генератор': DeviceState.GENERATOR
        }
        devices = self.devices_cb()

        value = self.device_state.get()

        if len(value) != 0:
            devices[self.index].change_state(options_map[value])
            self._recolor_on_state()

    def _recolor_on_state(self):
        state_to_color = {
            DeviceState.WORKING: '#00FF00',
            DeviceState.DENIAL: '#0000FF',
            DeviceState.BUSY: '#FF0000',
            DeviceState.FAILURE: '#FF0000',
            DeviceState.BLOCKED: '#FFFF00',
            DeviceState.GENERATOR: '#00FFFF'
        }
        devices = self.devices_cb()
        state = devices[self.index].state
        self.device_state_view.configure(bg=state_to_color[state])


class StandaloneUI(tk.Frame):
    def __init__(self, root, change_frame_cb):
        super().__init__(root)
        self.change_frame_button = tk.Button(self, text='Change frame', command=change_frame_cb)
        self.change_frame_button.grid(column=0, row=0)

        terminals_count = 4
        self.lcs = LCS(terminals_count=terminals_count, probabilities=[0, 0, 0, 0])
        self.terminal_views = []
        row = 1
        column = 0
        for i in range(terminals_count):
            terminal_view = TerminalDeviceView(self, i, self.lcs.get_terminals)
            terminal_view.grid(row=row, column=column)
            self.terminal_views.append(terminal_view)

            column += 1
            if column == 7:
                column = 0
                row += 1

        self.start_button = tk.Button(self, text='Запустить ЛВС', command=self.on_start_clicked)
        self.start_button.grid(row=row + 1)

    def on_start_clicked(self):
        self.lcs.process()
