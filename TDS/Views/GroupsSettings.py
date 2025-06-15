from customtkinter import *
from Proccesors.Database.db import *
from PIL import Image
from Views import Dashboard

def show(frame : CTkScrollableFrame, group_name : str):
    ref.execute("SELECT * FROM Students")
    stds = ref.fetchall()
    for std in stds:
        droosin = loads(std[12])
        droosinlst = [droosini["name"] for droosini in droosin]
        print("filtred list : ",droosinlst)
        print("Option : ",(group_name.strip()).split("|")[1])
        print("Non Filtred : ",droosin)
        if ((group_name.strip()).split("|")[1]).strip() in droosinlst:
            print((group_name.strip()).split("|")[1])
            ref.execute("UPDATE Students SET Badges = ? WHERE ID = ?", (group_name.strip(), std[0]))
    ref.connection.commit()
    for x in frame.winfo_children():
        x.destroy()
    ref.execute('SELECT * FROM Students WHERE Badges = ?', (group_name,))
    students_joined = len(ref.fetchall())
    title = CTkFrame(frame)
    title.pack(side=TOP, fill=X, padx=10, pady=10)
    CTkLabel(title, text='', image=CTkImage(Image.open('TDSAssets/Banking/bank_ico.png'), size=(60, 60))).pack(side=RIGHT, pady=10, padx=(15, 10))
    tt = CTkFrame(title, fg_color='transparent')
    tt.pack(side=RIGHT)
    CTkLabel(tt, text=f'{group_name}', font=('Cairo Medium', 20), compound='right', anchor='e').pack(fill=X)
    CTkLabel(tt, text=f'عدد الطلاب  :  {students_joined}', font=('Cairo Medium', 17), compound='right', anchor='e').pack(fill=X)
    def back():
        for x in frame.winfo_children():
            x.destroy()
        Dashboard.Dashboard(frame).pack(fill=BOTH, expand=True)
    CTkButton(title, text='العودة الي الصفحة الرئيسية', font=('Cairo Medium', 17), command=back).pack(side=LEFT, padx=15)
    students_listview = CTkScrollableFrame(frame, label_text='الطلاب', label_font=('Cairo Medium', 16), height=500)
    students_listview.pack(fill=X, padx=10, pady=10)

    def list_students():
        ref.execute('SELECT * FROM Students WHERE Badges = ?', (group_name,))
        students = ref.fetchall()
        for student in students:
            ff = CTkFrame(students_listview, fg_color='white')
            ff.pack(fill=X, padx=5,pady=5)
            CTkLabel(ff, text=student[1], font=('Cairo Medium', 19)).pack(pady=5,padx=10,side=RIGHT)
    list_students()