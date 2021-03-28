from tkinter import *
from functools import *
import numpy as np

root = Tk()
root.title("LVS")
root.geometry('900x600+600+400')

# def func():
#     if button["state"] == NORMAL:
#         button.config(state=DISABLED, bg="red")
#     else:
#         button.config(state=NORMAL, bg="green")
#
#         button = Button(text='Кнопощка', state=DISABLED, font="Courier 20")
#         button.pack()
#         b = Button(text="Активировать", command=func)
#         b.pack()
# class Example(Frame):
#
#     def __init__(self):
#         super().__init__()
#         self.initUI()
#
#     def initUI(self):
#         self.master.title("Цвета")
#         self.pack(fill=BOTH, expand=1)
#
#         canvas = Canvas(self)
#         canvas.create_rectangle(
#             30, 10, 120, 80,
#             outline="#fb0", fill="#fb0"
#         )
#
#         canvas.create_rectangle(
#             150, 10, 240, 80,
#             outline="#f50", fill="#f50"
#         )
#
#         canvas.create_rectangle(
#             270, 10, 370, 80,
#             outline="#05f", fill="#05f"
#         )
#
#         canvas.pack(fill=BOTH, expand=1)
def func(buttons):
    buttons.configure(bg="red")

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

        text = ('OY',i+1)
        lbl = Label(root, text=text,font='Times 7').place(x=x1, y=y1-20, height=15, width=25)
        button1.append(Button(root,  bg='#008000'))
        button1[i].place(x=x1, y=y1, height=15, width=15)
        button2.append(Button(root,  bg='#FF0000',command=lambda f=button1[i]: button1[i].pressed(f)))
        button2[i].place(x=x2, y=y1, height=15, width=15)
        button3.append(Button(root,  bg='#FFA500'))
        button3[i].place(x=x1, y=y2, height=15, width=15)
        button4.append(Button(root,  bg='#C71585'))
        button4[i].place(x=x2, y=y2, height=15, width=15)
        #button1[0].configure(bg='red')
        x1 = x1 + 50
        x2 = x2 + 50
    return button1, button2, button3, button4







ex = rectangle(3)

line_A_btn = Button(root, text='Линия А',bg='#008000')
line_A_btn.place(x=20,y=100, height=20, relwidth=0.89)
line_B_btn = Button(root, text='Линия B',bg='#FF0000').place(x=20,y=140, height=20, relwidth=0.89)






root.mainloop()

