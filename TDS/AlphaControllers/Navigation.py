from customtkinter import *
from threading import Thread
def ClearWidget(widget):
        for x in widget.winfo_children():
            x.destroy()