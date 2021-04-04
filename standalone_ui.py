import tkinter as tk


class StandaloneUI(tk.Frame):
    def __init__(self, root, change_frame_cb, height, width):
        super().__init__(root, height=height, width=width)
        self.change_frame_button = tk.Button(root, height=10, width=10, text='Change frame', command=change_frame_cb)
        self.change_frame_button.pack()
        self.text = tk.Label(root, text='Standalone here')
        self.text.pack()
