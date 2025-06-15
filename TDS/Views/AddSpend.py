from customtkinter import *
from json import dumps
from Views import Dashboard
from Widgets import Entries
from time import localtime
from AlphaControllers import EntryValidators
from Proccesors.Database.db import *
def apply(frame : CTkFrame):
    for i in frame.winfo_children():
        i.destroy()
    frame2 = CTkFrame(frame, fg_color='White')
    frame2.pack(fill=BOTH, expand=True)
    CTkLabel(frame2, text='      بيانات الصرف       ', font=('Cairo Medium', 22), anchor='e', fg_color='#f6f9fc').pack(fill=X, ipadx=10, ipady=5)
    
    name = Entries.UpperLabeledEntry(frame2, "وصف المصروف , إيجار قاعة مثلًا")
    name.pack(pady=(10,10), fill=X, padx=10)
    cn = Entries.UpperLabeledEntry(frame2, "المبلغ المصروف , 100 جنيه مثلًا")
    cn.pack(pady=10, fill=X, padx=10)
    fq = Entries.UpperLabeledEntry(frame2, "اسم الموظف الصارف , عبدالحميد مثلًا")
    fq.pack(pady=20, fill=X, padx=20)
    def back():
        for x in frame.winfo_children():
            x.destroy()
        Dashboard.Dashboard(frame).pack(fill=BOTH, expand=True)
        
    def add():
        if (
            EntryValidators.CheckBlank(name.entry),
            EntryValidators.CheckBlank(cn.entry),
            EntryValidators.CheckBlank(fq.entry),
        ):
            today = f'{localtime().tm_mday} \ {localtime().tm_mon} \ {localtime().tm_year}'
            ref.execute(
                """
                    INSERT INTO Spends VALUES (?,?,?,?)
                """,
                (cn.get_input(), today, dumps({'inf' : name.get_input(), 'nm' : fq.get_input()}), 'No')
                )
            conn.commit()
            back()
    AddButton = CTkButton(frame2,command=add, fg_color='#13b272', hover_color='#13b271', text='تأكيد', font=('Cairo Medium', 17), text_color='white')
    AddButton.pack(fill=X, padx=20, pady=(20,10), ipady=2)

    CancelButton = CTkButton(frame2, fg_color='#fc5f7d',command = lambda:back(), hover_color='#fc5f7d', text='الغاء الأمر', font=('Cairo Medium', 17), text_color='white')
    CancelButton.pack(fill=X, padx=20, pady=(0,20), ipady=2)
