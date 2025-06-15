from customtkinter import *
from Proccesors.Database.db import *
from json import dumps, loads
from PIL import Image
from Views import Dashboard, GroupsSettings
from Widgets import Entries

def show(frame : CTkFrame):
    for x in frame.winfo_children():
        x.destroy()
    for widget in frame.winfo_children():
        widget.destroy()
    ss = CTkFrame(frame, fg_color='white')
    sessions_listview = CTkScrollableFrame(ss, height=700)
    ref.execute('SELECT * FROM Groups')
    sessions = ref.fetchall()
    if sessions == []:
        CTkLabel(sessions_listview, text='', image=CTkImage(Image.open('TDSAssets/General/calender.png'), size=(120,120))).pack(pady=(150,5))
        CTkLabel(sessions_listview, text= 'لا توجد مجموعات هنا', font=('Cairo Medium',23)).pack()
    else:
        for group in sessions:
            ff = CTkFrame(sessions_listview,fg_color="white")
            ff.pack(fill=X, padx=5,pady=3)
            CTkLabel(ff, text=group[0], font=('Cairo Medium', 25)).pack(side=RIGHT, padx=15,pady=13)
            CTkButton(ff, text="تفاصيل", font=('Cairo Medium', 20), command=lambda gn = group[0] :GroupsSettings.show(frame, gn)).pack(side=LEFT)
    sessions_listview.pack(pady=10, fill=BOTH, expand=True, padx=20)
    ss.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)

    statics = CTkFrame(frame, fg_color='white')
    statics.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
    def back():
        for x in frame.winfo_children():
            x.destroy()
        Dashboard.Dashboard(frame).pack(fill=BOTH, expand=True)
    def AddNewGroup():
        xshow1 = CTkToplevel()
        xshow1.attributes("-topmost", True)
        xshow1.title("إضافة مرحلة جديدة")
        ref.execute("PRAGMA database_list;")
        team = ((ref.fetchone()[2]).split("\\")[-1]).replace(".db", "")
        Form = CTkScrollableFrame(xshow1, height=500, width=450)

        if True:
            CTkLabel(Form, text="إضافة مادة", font=("Cairo Medium", 23)).pack(pady=10)
            
            name = Entries.UpperLabeledEntry(
                Form,
                "اسم المادة"
            )
            name.pack(pady=5, padx=14, fill=X)
            time = Entries.UpperLabeledEntry(
                Form,
                "معاد الحصص"
            )
            time.pack(pady=(15,5), padx=14, fill=X)
            price = Entries.UpperLabeledEntry(
                Form,
                "سعر التجزئة"
            )
            price.pack(pady=(15,5), padx=14, fill=X)
            def add():
                '''
                CREATE TABLE IF NOT EXISTS InvSessions (
                    ID    INTEGER,
                    Name  TEXT,
                    JoinedNumber INTEGER,
                    PayQuantity  INTEGER,
                    Time         TEXT
                );
                '''
                ref.execute('SELECT * FROM Groups')
                print(ref.fetchall())
                print(f"{time.get_input()} | {name.get_input()}")
                ref.execute("INSERT INTO Groups VALUES (?)", (f"{time.get_input()} | {name.get_input()}",))    
                ref.execute('SELECT * FROM Groups')
                ref.execute("INSERT INTO InvSessions VALUES (?, ?, ?, ?, ?)", (len(ref.fetchall()) + 1 , name.get_input(), 0, int(price.get_input()), time.get_input()))
                ref.connection.commit()
                
                ref.execute('SELECT * FROM Groups')
                for x in sessions_listview.winfo_children():
                    x.destroy()
                for group in ref.fetchall():
                    ff = CTkFrame(sessions_listview, fg_color='White')
                    ff.pack(fill=X, padx=5,pady=3)
                    CTkLabel(ff, text=group[0], font=('Cairo Medium', 27)).pack(side=RIGHT, padx=15,pady=3)
                    CTkButton(ff, command=lambda gn = group[0] :GroupsSettings.show(frame, gn), text='تفاصيل', font=('Cairo Medium', 20)).pack(side=LEFT, padx=15, pady=3)
            
            CTkButton(Form, font=("Cairo Medium", 20), text="إضافة المادة", command = add).pack(side=BOTTOM,fill=X, padx=15, pady=(50,0))
            Form.pack(padx=10, pady=10, fill=X)
            
    CTkButton(statics, text='انشاء مجموعة جديدة', font=('Cairo Medium', 25),command=AddNewGroup,text_color='black', fg_color='#80C4E9', hover=False, image=CTkImage(Image.open('TDSAssets/General/pencil.png'), size=(90,90)), compound='top').pack(fill=X, padx=20, pady=(25,5), ipady=12)
    CTkButton(statics, text='الرجوع الي الصفحة الرئيسية', font=('Cairo Medium', 25),text_color='black', fg_color='#80C4E9', hover=False, image=CTkImage(Image.open('TDSAssets/General/backbutton.png'), size=(90,90)), compound='top', command=lambda:back()).pack(fill=X, padx=20, pady=5, ipady=12)


    

    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(0, weight=1)
    frame.rowconfigure(1, weight=2)