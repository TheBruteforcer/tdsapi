from customtkinter import *
def CheckBlank(entry : CTkEntry, frame : CTkScrollableFrame = None):
    if entry.get() == '':
        def on_type(event):
            entry.configure(border_color = '#13b272')
        entry.configure(border_color = '#ec2121')
        if CTkScrollableFrame != None:
            entry.update_idletasks()
            widget_y = entry.winfo_y()
            frame_height = frame.winfo_height()
            canvas_height = frame._parent_canvas.winfo_height()
            relative_position = widget_y / (frame_height - canvas_height)
            frame._parent_canvas.yview_moveto(relative_position)
        entry.bind("<KeyRelease>", on_type)
        return False
    else :
        return True
def SetGreenBorder(entry : CTkEntry):
    def on_type(event):
        if event.widget.get() == '':
            entry.configure(border_color='light grey')
            return
        entry.configure(border_color = '#13b272')
    entry.bind("<KeyRelease>", on_type)
def SetEnableButton(entry : CTkEntry, button : CTkButton, enabled_color : str):
    def on_type(event):
        if event.widget.get()!='':
            print(event.widget.get())
            if button.cget('state') == 'disabled':
                button.configure(fg_color = enabled_color, state='enabled')
        else:
            button.configure(fg_color = 'white', state='disabled')
    entry.bind("<KeyRelease>", on_type)
def UpdateOnKey(entry:CTkEntry, widget, type = 'normal'):
        def on_type(event):
            if type == 'normal':
                widget.configure(text = event.widget.get())
            if type == 'profile':
                widget.configure(text = event.widget.get()[0])
                print(event.widget.get())
        entry.bind("<KeyRelease>", on_type)