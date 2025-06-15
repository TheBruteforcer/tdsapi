import customtkinter as ctk

class SmoothScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Reduce the update frequency to reduce choppiness
        self.update_interval = 10  # in milliseconds
        
        # Schedule the first update
        self.after(self.update_interval, self.update_scroll)
    
    def update_scroll(self):
        # Perform any necessary updates
        self.update_idletasks()
        
        # Schedule the next update
        self.after(self.update_interval, self.update_scroll)
