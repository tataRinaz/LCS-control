import tkinter as tk

from lcs import LCS
from states import DeviceState, LineState
from threading import Thread

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
    'Раб': DeviceState.WORKING,
    'Отк': DeviceState.DENIAL,
    'Зан': DeviceState.BUSY,
    'Сбой': DeviceState.FAILURE,
    'Блок': DeviceState.BLOCKED,
    'Ген': DeviceState.GENERATOR,
    'Разблок': DeviceState.UNBLOCKING
}
state_to_name = {value: key for key, value in options_map.items()}


class TerminalDeviceView(tk.Frame):
    def __init__(self, root, device_index, devices_cb):
        super().__init__(root)
        self.index = device_index
        self.devices_cb = devices_cb

        self.device_state_view = tk.Frame(self, bg='#000000', width=10, height=10)
        self.device_state_view.grid(row=1, column=0)

        options = ['Раб', 'Отк', 'Зан', 'Сбой', 'Блок', 'Ген']

        self.device_state = tk.StringVar()
        self.states_option_menu = tk.OptionMenu(self, self.device_state, *options)
        self.states_option_menu.grid(row=0, column=0)

        terminals = devices_cb()
        terminals[self.index].set_state_change_callback(self._recolor_on_state)
        terminals[self.index].change_state(DeviceState.WORKING)

        self._name_label = tk.Label(self, text=f'ОУ №{self.index}')
        self._name_label.grid(row=2, column=0)
        self.process_state_change()
        self.configure(highlightbackground="red", highlightcolor="red", highlightthickness=5)

    def process_state_change(self):
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


class WorkingLineState(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self._line_text_label = tk.Label(self)
        self._line_text_label.grid(row=0, column=0)
        self.on_line_state_changed(LineState.WORKING_LINE_A)

    def on_line_state_changed(self, state):
        line = 'Линия B' if state == LineState.WORKING_LINE_B else 'Линия А'
        state = 'Генерация' if state == LineState.GENERATION else 'Рабочая'
        self._line_text_label.configure(text=line + ': ' + state)


class LCSRunThread(Thread):
    def __init__(self, task):
        Thread.__init__(self)
        self.task = task

    def run(self):
        try:
            self.task()
        except Exception as e:
            print(e)


class LCSView(tk.Frame):
    def __init__(self, root):
        super().__init__(root)

        terminals_count = 18
        self._line_state_view = WorkingLineState(self)
        self._line_state_view.grid(row=0, column=0)
        self._lcs = LCS(terminals_count=terminals_count, probabilities=[0, 0, 0, 0],
                        line_state_change_handler=self._line_state_view.on_line_state_changed)
        self._terminal_views = []
        row = 1
        column = 0
        for i in range(terminals_count):
            terminal_view = TerminalDeviceView(self, i, self._lcs.get_terminals)
            terminal_view.grid(row=row, column=column)
            self._terminal_views.append(terminal_view)

            column += 1

        self.configure(highlightbackground="green", highlightcolor="green", highlightthickness=5)

    def get_terminal_views(self):
        return self._terminal_views

    def get_lcs_thread(self):
        return LCSRunThread(self._lcs.process)


class StandaloneUI(tk.Frame):
    def __init__(self, root, change_frame_cb):
        super().__init__(root)
        self._change_frame_button = tk.Button(self, text='Перейти к статистической модели', command=change_frame_cb)
        self._change_frame_button.grid(column=0, row=0)

        self._lcs_frame = LCSView(self)
        self._lcs_frame.grid(column=0, row=1)

        self._state_select_button = tk.Button(self, text='Применить состояния ОУ',
                                              command=self._on_state_select_clicked)
        self._state_select_button.grid(row=2, column=0)
        self._start_button = tk.Button(self, text='Запустить', command=self._on_start_clicked)
        self._start_button.grid(row=3, column=0)

    def _on_start_clicked(self):
        self._lcs_frame.get_lcs_thread().start()

    def _on_clear_clicked(self):
        self._lcs = LCS(4, [0, 0, 0, 0])

    def _on_state_select_clicked(self):
        for index in range(len(self._lcs_frame.get_terminal_views())):
            self._lcs_frame.get_terminal_views()[index].process_state_change()
