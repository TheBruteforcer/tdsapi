import customtkinter as ctk
from PIL import Image
from Views import TeamSelector
from Widgets import Scrolls
from Proccesors.Database import db
from threading import Thread
from Cache.pp import main
from awesometkinter.bidirender import render_text
import tkinter as tk
from time import localtime
from Proccesors.Database.db import ref
from requests import *

ctk.set_appearance_mode('light')

class Application:
    def __init__(self):
        #db.change_distnation("Application.db")
        #Thread(target=db.Create).run()  
        self.loading_screen()
    
    def loading_screen(self):
        self.snk = ctk.CTk()
        app_width = 600
        app_height = 600

        # Load and keep a reference to the image
        logo_image = ctk.CTkImage(Image.open('TDSAssets/General/logo.png'), size=(200, 200))

        ctk.CTkLabel(self.snk, text='', image=logo_image).pack(pady=(150, 10))
        
        self.center_window(self.snk, app_width, app_height)
        self.snk.overrideredirect(True)
        stats = ctk.CTkLabel(self.snk, text=render_text('جاري التحميل'), font=('FF Shamel Family Sans One Bold', 20))
        stats.pack(pady=10)

        # Start caching in a background thread
        self.cache_thread = Thread(target=self.run_caching, daemon=True)
        self.cache_thread.start()

        # Check cache status every 100ms
        self.check_cache_status()
        
        self.snk.mainloop()
    
    def run_caching(self):
        """Run the caching process in background"""
        try:
            self.snk.after(0, self.update_status, render_text('جاري تحديث الذاكرة المؤقتة...'))
            main()
            self.snk.after(0, self.update_status, render_text('اكتمل تحديث الذاكرة المؤقتة'))
        except Exception as e:
            print(f"Caching error: {e}")
            self.snk.after(0, self.update_status, render_text('حدث خطأ في تحديث الذاكرة المؤقتة'))
        finally:
            # Set a flag to indicate caching is complete
            self.caching_complete = True
    
    def update_status(self, text):
        """Update the status label safely from any thread"""
        if hasattr(self, 'stats_label'):
            self.stats_label.configure(text=text)
    
    def check_cache_status(self):
        """Check if caching is complete and proceed to main app"""
        if hasattr(self, 'caching_complete') and self.caching_complete:
            # Wait a moment to show the completion message
            self.snk.after(1000, self.run_main_app)
        else:
            # Check again in 100ms
            self.snk.after(100, self.check_cache_status)
    
    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f'{width}x{height}+{x}+{y}')
    
    def run_main_app(self):
        for x in self.snk.winfo_children():
            x.destroy()
        self.snk.destroy()
        
        self.app = ctk.CTk()
        self.app.geometry('1200x660')
        self.app.configure()
        self.app.resizable(True, True)
        
        self.app.title('سيستم ادارة الدروس المتقدم')

        ss = Scrolls.SmoothScrollableFrame(self.app, fg_color='transparent')
        ss.pack(fill=ctk.BOTH, expand=True)
        TeamSelector.TeamView(ss).pack(fill=ctk.BOTH, expand=True)
        today = f'{localtime().tm_mday} \ {localtime().tm_mon} \ {localtime().tm_year}'
        self.app.mainloop()

Application()
