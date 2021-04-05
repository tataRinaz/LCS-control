import tkinter as tk

from lcs import LCS
from states import DeviceState

state_to_color = {
    DeviceState.WORKING: '#00FF00',
    DeviceState.DENIAL: '#0000FF',
    DeviceState.BUSY: '#FF0000',
    DeviceState.FAILURE: '#FF0000',
    DeviceState.BLOCKED: '#FFFF00',
    DeviceState.GENERATOR: '#00FFFF',
    DeviceState.UNBLOCKING: '#FF00FF',
    DeviceState.INITIAL: '#FFFFFF'
}
options_map = {
    'Рабочее': DeviceState.WORKING,
    'Отказ': DeviceState.DENIAL,
    'Занят': DeviceState.BUSY,
    'Сбой': DeviceState.FAILURE,
    'Заблокирован': DeviceState.BLOCKED,
    'Генератор': DeviceState.GENERATOR,
    'Разблокирован': DeviceState.UNBLOCKING,
    'ИЗначальное': DeviceState.INITIAL
}
state_to_name = {value:key for key, value in options_map.items()}

class TerminalDeviceView(tk.Frame):
    def __init__(self, root, device_index, devices_cb):
        super().__init__(root)
        self.index = device_index
        self.devices_cb = devices_cb

        terminals = devices_cb()
        terminals[self.index].set_state_change_callback(self._recolor_on_state)

        options = ['Рабочее', 'Отказ', 'Занят', 'Сбой', 'Заблокирован', 'Генератор']

        self.device_state = tk.StringVar()
        self.states_option_menu = tk.OptionMenu(self, self.device_state, *options)
        self.states_option_menu.grid(row=0, column=0)
        self.states_change_button = tk.Button(self, text='Выбрать', command=self._process_state_change)
        self.states_change_button.grid(row=0, column=1)
        self._process_state_change()

        self.device_state_view = tk.Frame(self, bg='#000000', width=10, height=10)
        self.device_state_view.grid(row=1, column=0)

    def _process_state_change(self):
        devices = self.devices_cb()

        value = self.device_state.get()

        if len(value) != 0:
            devices[self.index].change_state(options_map[value])
            self._recolor_on_state()

    def _recolor_on_state(self):

        devices = self.devices_cb()
        state = devices[self.index].state
        self.device_state.set(state_to_name[state])
        self.device_state_view.configure(bg=state_to_color[state])


class StandaloneUI(tk.Frame):
    def __init__(self, root, change_frame_cb):
        super().__init__(root)
        self._change_frame_button = tk.Button(self, text='Перейти к статистической модели', command=change_frame_cb)
        self._change_frame_button.grid(column=0, row=0)

        terminals_count = 4
        self._lcs = LCS(terminals_count=terminals_count, probabilities=[0, 0, 0, 0])
        self._terminal_views = []
        row = 1
        column = 0
        for i in range(terminals_count):
            terminal_view = TerminalDeviceView(self, i, self._lcs.get_terminals)
            terminal_view.grid(row=row, column=column)
            self._terminal_views.append(terminal_view)

            column += 1
            if column == 4:
                column = 0
                row += 1

        self._start_button = tk.Button(self, text='Запустить ЛВС', command=self._on_start_clicked)
        self._start_button.grid(row=row + 1, column=0)
        self._clear_button = tk.Button(self, text='Очистить ЛВС', command=self._on_clear_clicked)
        self._clear_button.grid(row=row + 1, column=1)

    def _on_start_clicked(self):
        self._lcs.process()

    def _on_clear_clicked(self):
        self._lcs = LCS(4, [0, 0, 0, 0])
