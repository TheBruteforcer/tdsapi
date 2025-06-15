from customtkinter import *
from json import loads, dumps
from Widgets.Entries import *
from time import localtime
from AlphaControllers.EntryValidators import CheckBlank
from Proccesors.Database.db import *
from Proccesors.Genric.SessionSpendManager import *
from PIL import Image
def Pop(spends_frame, id):
    ref.execute('SELECT * FROM Sessions WHERE ID = ?', (id,) )
    sessison_data = ref.fetchone()
    popup = CTkToplevel()
    popup.geometry('570x500')
    popup.resizable(1,0)
    popup.attributes('-topmost', True)
    title = CTkFrame(popup, fg_color='transparent')
    title.pack(pady=20)
    def step_1(option):
            for x in popup.winfo_children():
                x.destroy()
            title = CTkFrame(popup, fg_color='transparent')
            title.pack(pady=(20,15))
            CTkLabel(title, text='', image=CTkImage(Image.open('TDSAssets/General/printer.png'), size=(90,90))).pack(padx=10, pady=(30,10), side=RIGHT)
            CTkLabel(title, text='استخراج مستلزمات للحضور', font=('Cairo Medium', 30)).pack(side=RIGHT)

            qnt = UpperLabeledEntry(popup, 'العدد')
            qnt.pack(fill=X, padx=30)
            val = StringVar()
            def toggle():
                if val.get() == 'y':
                    ref.execute('SELECT * FROM Sessions WHERE ID = ?', (id,))
                    ref.execute("PRAGMA database_list;")
                    team = ((ref.fetchone()[2]).split("\\")[-1]).replace(".db", "")
                    conn_checker = connect("Application.db")
                    ref_checker  = conn_checker.cursor()
                    ref_checker.execute("SELECT * FROM PGroups WHERE Name = ?", (team,))
                    type = ref_checker.fetchone()[2]
                    if type == "بالحصة":
                        aa = StringVar(value = sessison_data[4])
                    else:
                        aa = StringVar(value = sessison_data[3])
                        
                    
                    qnt.entry.configure(state='disabled', fg_color='light grey', textvariable = aa)
                    
                else:
                    qnt.entry.delete(0, END)
                    qnt.entry.configure(state='normal', fg_color='white')
            CTkCheckBox(popup, text='مطابقة عدد الحضور', font=('Cairo Medium', 16), onvalue='y', offvalue='n', variable=val, command=toggle).pack(pady=(20,0))
            price = UpperLabeledEntry(popup, 'سعر الوحدة')
            price.pack(fill=X, padx=30)
            name = UpperLabeledEntry(popup, 'اسم المستلزم')
            name.pack(fill=X, padx=30)
            def apply():
                if (
                    CheckBlank(price.entry),
                    CheckBlank(name.entry),
                ):
                    today = f'{localtime().tm_mday} \ {localtime().tm_mon} \ {localtime().tm_year}'
                    def get_total():
                        if val.get() == 'y':
                            return (int(price.get_input()) * int(sessison_data[4]))
                        else:
                            return (int(qnt.get_input()) * int(price.get_input()))

                    ref.execute('INSERT INTO Spends VALUES (?,?,?,?)', (get_total(),today ,dumps({'inf':f'{name.get_input()}', 'nm':"عام"}), dumps({"stats": "mstlzmat", "session-info": {"id": sessison_data[0], "title": sessison_data[1]}})))
                    conn.commit()
                    LoadSpendsForSession(spends_frame, sessison_data)
                    popup.destroy()
            CTkButton(popup, text='تأكيد', font=('Cairo Medium', 18), command=apply).pack(fill=X, padx=40, pady=(10,0))
    CTkLabel(title, text='', image=CTkImage(Image.open('TDSAssets/General/printer.png'), size=(90,90))).pack(padx=10, pady=(30,10), side=RIGHT)
    CTkLabel(title, text='استخراج مستلزمات للحضور', font=('Cairo Medium', 30)).pack(side=RIGHT)
    CTkButton(popup, text='طباعة ورق امتحان تاني', font=('Cairo Medium', 20),command=lambda:step_1('AQP'), image=CTkImage(Image.open('TDSAssets/General/folder.png'), size=(60,60)), compound=TOP).pack(pady=(0,20), fill=X, padx=30, ipady=20)
    CTkButton(popup, text='حاجة تانيه', font=('Cairo Medium', 20),command=lambda:step_1("ANTH"), image=CTkImage(Image.open('TDSAssets/General/lines.png'), size=(60,60)), compound=TOP).pack(pady=(0,20), fill=X, padx=30, ipady=20)
