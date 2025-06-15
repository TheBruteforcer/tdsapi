from customtkinter import *
from json import loads, dumps
from Widgets import Entries
from Proccesors.Database.db import *
from PIL import Image
from time import localtime
from Views import Sessions, Dashboard, Exams
import customtkinter as ctk
import tkinter as tk
def go(frame : CTkScrollableFrame):
    for widget in frame.winfo_children():
        widget.destroy()
    ss = CTkFrame(frame, fg_color='white')
    sessions_listview = CTkScrollableFrame(ss, height=500)
    ref.execute('SELECT * FROM Sessions')
    sessions = ref.fetchall()
    if sessions == []:
        CTkLabel(sessions_listview, text='', image=CTkImage(Image.open('TDSAssets/General/calender.png'), size=(120,120))).pack(pady=(150,5))
        CTkLabel(sessions_listview, text= 'لا توجد حصص هنا', font=('Cairo Medium',23)).pack()
    else:
        for session in sessions:
            ff = CTkFrame(sessions_listview, fg_color='white')
            ff.pack(fill=X, padx=5,pady=5)
            CTkLabel(ff, text=session[1], font=('Cairo Medium', 20)).pack(pady=5,padx=15, side=RIGHT)
            CTkButton(ff, text='تفاصيل', font=('Cairo Medium', 18), command=lambda sss = session : Desc(frame, sss)).pack(pady=5, padx=15,side=LEFT)
    kew = Entries.UpperLabeledEntry(ss, 'بحث عن حصة')
    kew.pack(fill=BOTH,padx=10, pady=(10,0))
    def SearchSession(event):
        if event.widget.get() == '':
            for x in sessions_listview.winfo_children():
                x.destroy()
            ref.execute('SELECT * FROM Sessions')
            sessions = ref.fetchall()
            if sessions == []:
                CTkLabel(sessions_listview, text='', image=CTkImage(Image.open('TDSAssets/General/calender.png'), size=(120,120))).pack(pady=(150,5))
                CTkLabel(sessions_listview, text= 'لا توجد حصص هنا', font=('Cairo Medium',23)).pack()
            else:
                for session in sessions:
                    ff = CTkFrame(sessions_listview, fg_color='white')
                    ff.pack(fill=X, padx=5,pady=5)
                    CTkLabel(ff, text=session[1], font=('Cairo Medium', 20)).pack(pady=5,padx=15, side=RIGHT)
                    CTkButton(ff, text='تفاصيل', font=('Cairo Medium', 18), command=lambda sss = session : Desc(frame, sss)).pack(pady=5, padx=15,side=LEFT)
        else:
            try:
                int(event.widget.get())
                for x in sessions_listview.winfo_children():
                    x.destroy()
                ref.execute(f'SELECT * FROM Sessions WHERE ID = "{event.widget.get()}"')
                sessions = ref.fetchall()
                for session in sessions:
                    ff = CTkFrame(sessions_listview, fg_color='white')
                    ff.pack(fill=X, padx=5,pady=5)
                    CTkLabel(ff, text=session[1], font=('Cairo Medium', 20)).pack(pady=5,padx=15, side=RIGHT)
                    CTkButton(ff, text='تفاصيل', font=('Cairo Medium', 18), command=lambda sss = session : Desc(frame, sss)).pack(pady=5, padx=15,side=LEFT)
            except:
                for x in sessions_listview.winfo_children():
                    x.destroy()
                ref.execute(f'SELECT * FROM Sessions WHERE Title LIKE "%{event.widget.get()}%"')
                sessions = ref.fetchall()
                for session in sessions:
                    ff = CTkFrame(sessions_listview, fg_color='white')
                    ff.pack(fill=X, padx=5,pady=5)
                    CTkLabel(ff, text=session[1], font=('Cairo Medium', 20)).pack(pady=5,padx=15, side=RIGHT)
                    CTkButton(ff, text='تفاصيل', font=('Cairo Medium', 18), command=lambda sss = session : Desc(frame, sss)).pack(pady=5, padx=15,side=LEFT)
        if len(sessions_listview.winfo_children()) == 0:
                CTkLabel(sessions_listview, text='', image=CTkImage(Image.open('TDSAssets/General/error.png'), size=(90,90))).pack(pady=(60,5))
                CTkLabel(sessions_listview, text= 'هذه المحاضرة غير موجودة', font=('Cairo Medium',19)).pack()
    kew.entry.bind('<KeyRelease>', SearchSession)
    sessions_listview.pack(pady=10, fill=BOTH, expand=True, padx=20)
    ss.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)



    statics = CTkFrame(frame, fg_color='white')
    statics.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
    def back():
        for x in frame.winfo_children():
            x.destroy()
        Dashboard.Dashboard(frame).pack(fill=BOTH, expand=True)
    CTkButton(statics, text='انشاء حصة مباشرة', font=('Cairo Medium', 25),command=lambda:Sessions.Session(frame),text_color='black', fg_color='#80C4E9', hover=False, image=CTkImage(Image.open('TDSAssets/General/pencil.png'), size=(90,90)), compound='top').pack(fill=X, padx=20, pady=(25,5), ipady=12)
    CTkButton(statics, text='الرجوع الي الصفحة الرئيسية', font=('Cairo Medium', 25),text_color='black', fg_color='#80C4E9', hover=False, image=CTkImage(Image.open('TDSAssets/General/backbutton.png'), size=(90,90)), compound='top', command=lambda:back()).pack(fill=X, padx=20, pady=5, ipady=12)


    

    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(0, weight=1)
    frame.rowconfigure(1, weight=2)


def Desc(frame:CTkScrollableFrame,session_data):
    for x in frame.winfo_children():
        x.destroy()
    ss = CTkFrame(frame, fg_color='white')
    ss.grid(row=0, column=1, sticky='nsew', padx=10, pady=10, rowspan=3)
    
    CTkLabel(ss, text='', image=CTkImage(Image.open('TDSAssets/General/done_unthemed.png'), size=(100,100))).pack(pady=(200,10))
    CTkLabel(ss,text=session_data[1], font=('FF Shamel Family Sans One Bold', 25)).pack(pady=10)
    CTkLabel(ss,text=f"عدد الحضور : {session_data[4]}", font=('FF Shamel Family Sans One Book', 18)).pack(pady=10)

    


    statics = CTkFrame(frame, fg_color='white')
    statics.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
    percentage = CTkFrame(statics, fg_color='white')
    yattend = CTkFrame(percentage, fg_color='transparent')
    yattend.pack(fill=BOTH, side=RIGHT,pady=(10,10),padx=(0,35))
    nattend = CTkFrame(percentage, fg_color='transparent')
    nattend.pack(fill=BOTH, side=RIGHT, pady=(10,10),padx=(0,35))
    nattend2 = CTkFrame(percentage, fg_color='transparent')
    nattend2.pack(fill=BOTH, side=RIGHT, pady=(10,10),padx=(0,35))
    circular = CTkFrame(yattend, fg_color='#36BA98', corner_radius=180, width=100, height=100)
    circular.pack(pady=(15,10))
    attendplbl = CTkLabel(circular, text='73%', font=('Arial', 45, 'bold'), text_color='white')
    attendplbl.pack(fill=BOTH, expand=True, padx=25,pady=43)
    CTkLabel(yattend, text='صحة الحصة', font=('Cairo Medium', 20)).pack()
    circular = CTkFrame(nattend, fg_color='#36BA98', corner_radius=180, width=100, height=100)
    circular.pack(pady=(15,10))
    attendplbl = CTkLabel(circular, text='90%', font=('Arial', 45, 'bold'), text_color='white')
    attendplbl.pack(fill=BOTH, expand=True, padx=25,pady=43)
    CTkLabel(nattend, text="نسبة الحضور", font=('Cairo Medium', 20)).pack()
    circular = CTkFrame(nattend2, fg_color='orange', corner_radius=180, width=100, height=100)
    circular.pack(pady=(15,10))
    nattendplbl = CTkLabel(circular, text='10%', font=('Arial', 45, 'bold'), text_color='white')
    nattendplbl.pack(fill=BOTH, expand=True, padx=25,pady=43)
    CTkLabel(nattend2, text="نسبة الغياب", font=('Cairo Medium', 20)).pack()
    ref.execute('SELECT * FROM Students WHERE Badges = ?', (session_data[10],))
    studentsnum = len(ref.fetchall())
    ref.execute('SELECT * FROM Sessions WHERE ID = ?', (session_data[0],))
    session_data2 = ref.fetchone()
    new_attends = int(session_data2[4])
    ref.execute(f'UPDATE Sessions SET Attendance = "{new_attends}" WHERE ID = "{session_data[0]}"')
    today = f'{localtime().tm_mday} \ {localtime().tm_mon} \ {localtime().tm_year}'

    ref.execute('SELECT * FROM Sessions WHERE ID = ?', (session_data[0],))
    session_data3 = ref.fetchone()

    per = ( new_attends / studentsnum ) * 100
    attendplbl.configure(text=f"{int(per)}%")
    nattendplbl.configure(text=f"{100-int(per)}%")
    percentage.pack()
    statics2 = CTkFrame(frame, fg_color='white')
    statics2.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
    pp = CTkFrame(statics2, fg_color='transparent')
    pp.pack()
    allspends = 0
    ref.execute('SELECT * FROM Spends')
    for spend in ref.fetchall():
        try:
            if loads(spend[3])['session-info']['id'] == session_data[0]:
                allspends += int(spend[0])
        except:
            pass
    spends = CTkFrame(pp, fg_color='transparent')
    spends.pack(fill=X, padx=10,pady=(60,60), side=RIGHT)
    CTkLabel(spends, text='', image=CTkImage(Image.open('TDSAssets/General/red_down.png'), size=(50,50))).pack(side=RIGHT, padx=10, pady=5)
    CTkLabel(spends, text='المصروفات', font=('Cairo Medium', 24)).pack(side=RIGHT, padx=10)
    CTkLabel(spends, text=f'{allspends:,} EGP', font=('Cairo Medium', 24)).pack(side=RIGHT,  padx=10)
    allgains7 = 0
    ref.execute('SELECT * FROM Gains WHERE ID = ?', (session_data[0],))
    for gain in ref.fetchall():
        allgains7 += int(gain[2])
    gains = CTkFrame(pp, fg_color='transparent')
    gains.pack(fill=X, padx=(0,20),pady=(60,60), side=RIGHT)
    CTkLabel(gains, text='', image=CTkImage(Image.open('TDSAssets/General/green_up.png'), size=(50,50))).pack(side=RIGHT, padx=10, pady=5)
    CTkLabel(gains, text='الأرباح', font=('Cairo Medium', 24)).pack(sid=RIGHT, padx=10)
    CTkLabel(gains, text=f'{allgains7:,} EGP', font=('Cairo Medium', 24)).pack(sid=RIGHT,  padx=10)
    statics3 = CTkFrame(frame, fg_color='white')
    statics3.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)

    
    CTkButton(statics3, text='الرجوع', image=CTkImage(Image.open('TDSAssets/General/backbutton.png'), size=(60,60)),font=('Cairo Medium', 20), compound=TOP, command=lambda:go(frame)).pack(ipady=10, fill=X, padx=10, pady=10,expand=True, side=RIGHT)
    CTkButton(statics3, text='الذهاب لرؤية احصائيات الامتحانات',command=lambda:Exams.go(frame), image=CTkImage(Image.open('TDSAssets/General/test.png'), size=(60,60)),font=('Cairo Medium', 20), compound=TOP).pack(ipady=10, fill=X, padx=10, pady=10,expand=True, side=RIGHT)


    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(0, weight=1)
    frame.rowconfigure(1, weight=1)
    frame.rowconfigure(2, weight=1)