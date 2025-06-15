from customtkinter import *
from AlphaControllers.EntryValidators import SetGreenBorder
import customtkinter as ctk
class SdidedEntryLabel(ctk.CTkFrame):
    def __init__(self, master,  placeholdertext, labeltext,**kwargs):
        super().__init__(master, fg_color='light grey', border_width=0, border_color='light grey', **kwargs)
        self.entry = ctk.CTkEntry(self, justify='right', font=('Cairo Medium', 15),placeholder_text=placeholdertext, border_width=1, border_color='light grey', corner_radius=0, fg_color='white')
        self.entry.pack(fill=ctk.BOTH, expand=True, side=ctk.RIGHT)
        labelframe = ctk.CTkFrame(self, corner_radius=0, border_color='light grey', border_width=1, fg_color='White')
        labelframe.pack(side=ctk.RIGHT, fill=ctk.Y)
        ctk.CTkLabel(labelframe, text=labeltext, font=('Cairo Medium', 13)).pack(padx=10, pady=2)
    def get_input(self):
        return self.entry.get()
class UpperLabeledEntry(CTkFrame):
    def __init__(self, master, labeltext):
        super().__init__(master, fg_color='transparent')
        CTkLabel(self, text=labeltext, font=('Cairo Medium', 14), text_color='#75799d', anchor='e').pack(fill=X,padx=10)
        self.entry = ctk.CTkEntry(self, justify='right', font=('Cairo Medium', 15), border_width=1, border_color='light grey', corner_radius=1, fg_color='white')
        self.entry.pack(pady=5, fill=X,padx=10)
        SetGreenBorder(self.entry)
    def get_input(self):
        return self.entry.get()
