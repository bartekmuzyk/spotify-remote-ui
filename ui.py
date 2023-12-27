import tkinter as tk


class Sizing:
    SPACE_UNIT = 20
    PLAY_BUTTON_SIZE = 64


class CleanButton(tk.Button):
    def __init__(self, master, **kwargs):
        tk.Button.__init__(self, master, **kwargs)
        self.configure(bg="black", borderwidth=0, highlightthickness=0, activebackground="black",
                       activeforeground="white")
