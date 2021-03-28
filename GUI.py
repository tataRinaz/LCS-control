from tkinter import *
from states import DeviceState
from terminal_device import TerminalDevice
import lcs

COLOR = 'grey'


class MainWindow:

    def __init__(self, window_height: int, window_width: int, window_position_height: int, window_position_width: int):
        self.window_height = window_height
        self.window_width = window_width
        self.window_position_height = window_position_height
        self.window_position_width = window_position_width
        self.buttons = []
        self.root = Tk()

    def start_gui(self):
        self.root.title("LVS")
        self.root.geometry(
            f'{self.window_height}x{self.window_width}+{self.window_position_height}+{self.window_position_width}')
        self.root.mainloop()

    def init_gui(self):


class TerminalDeviceButton(Button):

    def __init__(self, root, button_height: int, button_width: int, button_position_x1: int, button_position_y1: int,
                 color, state, terminal_device
                 ):
        super().__init__(root, bg=COLOR, command=self.on_button_click)
        self.root = root
        self.pending_color = color
        self.current_state = DeviceState.INITIAL
        self.current_color = COLOR
        self.pending_state = state
        self.terminal_device = terminal_device
        self.place(x=button_position_x1, y=button_position_y1, height=button_height, width=button_width)

    def on_button_click(self):
        self.current_color, self.pending_color = self.pending_color, self.current_color
        self.current_state, self.pending_state = self.pending_state, self.current_state
        self.process_current_state()

    def process_current_state(self):
        self.configure(bg=self.current_color)
        self.terminal_device.change_state(self.current_state)


def rectangle(N):
    button1 = []
    button2 = []
    button3 = []
    button4 = []
    x1 = 0
    y1 = 20
    x2 = 20
    y2 = 40
    for i in range(N):
        text = ('OY', i + 1)
        lbl = Label(root, text=text, font='Times 7').place(x=x1, y=y1 - 20, height=15, width=25)
        button1.append(Button(root, bg='#008000'))
        button1[i].place(x=x1, y=y1, height=15, width=15)
        button2.append(Button(root, bg='#FF0000', command=lambda f=button1[i]: button1[i].pressed(f)))
        button2[i].place(x=x2, y=y1, height=15, width=15)
        button3.append(Button(root, bg='#FFA500'))
        button3[i].place(x=x1, y=y2, height=15, width=15)
        button4.append(Button(root, bg='#C71585'))
        button4[i].place(x=x2, y=y2, height=15, width=15)
        # button1[0].configure(bg='red')
        x1 = x1 + 50
        x2 = x2 + 50
    return button1, button2, button3, button4


ex = rectangle(3)

line_A_btn = Button(root, text='Линия А', bg='#008000')
line_A_btn.place(x=20, y=100, height=20, relwidth=0.89)
line_B_btn = Button(root, text='Линия B', bg='#FF0000').place(x=20, y=140, height=20, relwidth=0.89)

root.mainloop()
