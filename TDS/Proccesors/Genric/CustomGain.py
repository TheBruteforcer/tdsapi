from customtkinter import *
from json import dumps, loads
from Proccesors.Database.db import *
from Widgets import Entries
from AlphaControllers.EntryValidators import CheckBlank
from PIL import Image
from time import localtime
from datetime import datetime
from tkinter import ttk
from tkinter import StringVar

def AddCustomGain(session_data):
    popup = CTkToplevel()
    popup.geometry('500x550')
    popup.attributes('-topmost', True)
    popup.resizable(0,0)
    popup.title('اضافة ربح')
    title = CTkFrame(popup, fg_color='transparent')
    title.pack(pady=(20,15))
    CTkLabel(title, text='', image=CTkImage(Image.open('TDSAssets/General/note.png'), size=(90,90))).pack(padx=10, pady=(30,10), side=RIGHT)
    CTkLabel(title, text='اضافة ربح جديد', font=('FF Shamel Family Sans One Bold', 30)).pack(side=RIGHT, pady=(30,0), padx=(50,0))
    title_entry = Entries.UpperLabeledEntry(popup, 'عنوان الربح , بيع ملازم مثلًا')
    title_entry.pack(fill=X, padx=25, pady=(20,10))
    price = Entries.UpperLabeledEntry(popup, 'المبلغ الوارد')
    price.pack(fill=X, padx=25, pady=10)

    # Student ID entry (optional)
    student_id_entry = Entries.UpperLabeledEntry(popup, 'معرف الطالب (اختياري)')
    student_id_entry.pack(fill=X, padx=25, pady=(10, 5))

    def apply():
        if (CheckBlank(title_entry.entry), CheckBlank(price.entry)):
            now = datetime.now()
            today = now.strftime('%d \\ %m \\ %Y')
            time_str = now.strftime('%I:%M %p')
            date_with_time = f'{today} - {time_str}'
            gain_title = title_entry.get_input()
            student_id = student_id_entry.get_input().strip()
            if student_id:
                gain_title = f"{gain_title} (ID:{student_id})"
            ref.execute('INSERT INTO Gains VALUES (?,?,?, ?)', (session_data[0], gain_title, price.get_input(), date_with_time))
            conn.commit()
            popup.destroy()
    CTkButton(popup, text='اتمام الإضافة', font=('Cairo Medium', 20), command=apply).pack(fill=X, pady=20,padx=35)
