from customtkinter import *
from PIL import Image
from Widgets import Entries
from Proccesors.Database.db import *
from AlphaControllers.EntryValidators import CheckBlank
from json import dumps, loads
from time import localtime
def AddSpend(listview, session_data):
    popup = CTkToplevel()
    popup.geometry('400x520')
    popup.attributes('-topmost', True)
    CTkLabel(popup, text='', image=CTkImage(Image.open('TDSAssets/General/red_bag.png'), size=(100,100))).pack(pady=(40,10))
    CTkLabel(popup, text='اضافة مصروف للحصة', font=('Cairo Medium', 23)).pack(pady=(0, 10))
    qnt = Entries.UpperLabeledEntry(popup, 'المبلغ المصروف')
    qnt.pack(pady=(5,10), fill=X, padx=10)
    desc = Entries.UpperLabeledEntry(popup, 'وصف المصروف')
    desc.pack(pady=(0,10), fill=X, padx=10)
    name = Entries.UpperLabeledEntry(popup, 'اسم الصارف')
    name.pack(pady=(0,10), fill=X, padx=10)
    def apply():
        if (
            CheckBlank(qnt.entry),
            CheckBlank(desc.entry),
            CheckBlank(name.entry),
        ):
            today = f'{localtime().tm_mday} \ {localtime().tm_mon} \ {localtime().tm_year}'
            ref.execute('INSERT INTO Spends Values (?,?,?,?)', (qnt.get_input(), today, dumps({"inf" : desc.get_input(), 'nm':name.get_input()}), dumps({'stats':'session', 'session-info':{'id':session_data[0], 'title' : session_data[1]}})))
            conn.commit()
            for child in listview.winfo_children():
                child.destroy()
            LoadSpendsForSession(listview, session_data)
            popup.destroy()
    CTkButton(popup, text='تأكيد', font=('Cairo Medium' ,18), fg_color='#399918', command=apply).pack(fill=X, padx=20, pady=(5,0))
def LoadSpendsForSession(listview : CTkScrollableFrame ,session_data : tuple):
    for x in listview.winfo_children():
        x.destroy()
    ref.execute('SELECT * FROM Spends')
    for x in ref.fetchall():
        try:
            if loads(x[3])['session-info']['id'] == session_data[0]:
                ff = CTkFrame(listview, fg_color='white')
                ff.pack(padx=5, pady=5, fill=X)
                CTkLabel(ff, text='', image=CTkImage(Image.open('TDSAssets/General/red_down.png'), size=(40, 40))).pack(pady=5, padx=5, side=RIGHT)
                CTkLabel(ff, text=loads(x[2])['inf'], font=('Cairo Medium', 20)).pack(side=RIGHT, padx=10)
                CTkLabel(ff, text=loads(x[2])['nm'], font=('Cairo Medium', 20), text_color='green').pack(side=RIGHT, padx=10)
                CTkLabel(ff, text=f'E£ {int(x[0]):,}', font=('Cairo Medium', 18)).pack(side=RIGHT, padx=10)
        except:
            pass
