import tkinter as tk

from lcs import LCS
from states import DeviceState, LineState
from threading import Thread

state_to_color = {
    DeviceState.WORKING: 'green',
    DeviceState.DENIAL: 'red',
    DeviceState.BUSY: 'orange',
    DeviceState.FAILURE: 'yellow',
    DeviceState.BLOCKED: 'purple',
    DeviceState.GENERATOR: 'blue',
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
    def __init__(self, root, device_index, devices_cb, is_up):
        super().__init__(root, width=200, height=100)
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
        self.configure(highlightbackground="green", highlightcolor="green", highlightthickness=5)

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


class ControllerView(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self._text_label = tk.Label(self, text='Контроллер')
        self._text_label.grid(row=0, column=0)
        self.configure(highlightbackground="red", highlightcolor="red", highlightthickness=5,
                       bg="yellow")


class LCSRunThread(Thread):
    def __init__(self, task):
        Thread.__init__(self)
        self.task = task

    def run(self):
        try:
            self.task()
        except Exception as e:
            print(e)


CONNECTION_COLOR = "green"
INACTIVE_COLOR = "gray"


class DataLineView(tk.Frame):
    def __init__(self, root: tk.Frame, color):
        super().__init__(root)
        self._canvas = tk.Canvas(self, width=750, height=10)
        self._color = color
        self._fill_canvases()

    def _fill_canvases(self):
        self._canvas.create_line(0, 10, 750, 10, width=10, fill=self._color)
        self._canvas.grid(row=0, column=0)


class DataLineMarker:
    def __init__(self, root, row, colspan, name, color):
        self._data_line_view = DataLineView(root, color)
        self._data_line_view.grid(row=row, column=1, columnspan=colspan)
        self._text_label = tk.Label(root, text=name)
        self._text_label.grid(row=row, column=0)


class DataLineHolder:
    def __init__(self, root, min_row, colspan):
        self._root = root

        self._up_connectors = [tk.Canvas(root, height=100, width=50) for _ in range(colspan - 1)]
        self._grid_connectors(min_row)

        self._a_data_line = DataLineMarker(root, min_row + 1, colspan, 'A', CONNECTION_COLOR)
        self._b_data_line = DataLineMarker(root, min_row + 2, colspan, 'B', INACTIVE_COLOR)
        self._connect_to_a()

    def _grid_connectors(self, row):
        for index, _ in enumerate(self._up_connectors):
            self._up_connectors[index].grid(row=row, rowspan=3, column=index + 1)

    def _connect_to_a(self):
        for index, _ in enumerate(self._up_connectors):
            self._up_connectors[index].create_line(20, 0, 20, 40, fill=CONNECTION_COLOR, width=5)
            self._up_connectors[index].create_line(30, 35, 30, 100, fill=CONNECTION_COLOR, width=5)


class LCSView(tk.Frame):
    def __init__(self, root):
        super().__init__(root)

        terminals_count = 18
        self._lcs = LCS(terminals_count=terminals_count, probabilities=[0, 0, 0, 0])
        self._terminal_views = []
        column = 1
        current_row, next_row = 1, 6

        for i in range(terminals_count):
            terminal_view = TerminalDeviceView(self, i, self._lcs.get_terminals, current_row == 1)
            terminal_view.grid(row=current_row, column=column)
            self._terminal_views.append(terminal_view)

            current_row, next_row = next_row, current_row

            if current_row == 1:
                column += 1

        self._data_line_holder = DataLineHolder(self, min_row=2, colspan=column)
        self._controller_view = ControllerView(self)
        self._controller_view.grid(row=7, column=0)

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
