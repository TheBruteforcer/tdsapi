from customtkinter import *
from json import loads, dumps, load
from Proccesors.Database.db import *
from Views import Dashboard
from PIL import Image
from Widgets import Entries
from time import localtime
def Apply(parent : CTkScrollableFrame):
    for x in parent.winfo_children():
        x.destroy()
    
    choice = StringVar(value='اختر المجموعه او متختارش لو هتطبع عام')
    # -- MLPowerSelection -- #
    def Selection(stringvar, entries):
        if stringvar.get() == '0':
            ref.execute('INSERT INTO Spends VALUES (?,?,?,?)', ((int(entries[1].get_input()) * int(entries[2].get_input())), f'{localtime().tm_mday} \ {localtime().tm_mon} \ {localtime().tm_year}', dumps({'inf':'مستلزمات للطلاب', 'nm':'النظام'}), None))
            conn.commit()
            for x in parent.winfo_children():
                x.destroy()
            ff = CTkFrame(parent, fg_color='white', corner_radius=10)
            ff.pack(fill=BOTH, padx=10,pady=10,expand=True)
            CTkLabel(ff, text='', image=CTkImage(Image.open('TDSAssets/General/done_unthemed.png'), size=(100,100))).pack(pady=(200,10))
            CTkLabel(ff,text='تم بنجاح', font=('FF Shamel Family Sans One Bold', 25)).pack(pady=10)
#            CTkLabel(ff, text=f'تم الحساب\nالعدد المطبق : {info["higher_than_average"]} \n العدد المهمل : {info["lower_than_average"]}', font=('FF Shamel Family Sans One Book', 20)).pack(pady=5)
            def back():
                    for x in parent.winfo_children():
                        x.destroy()
                    Dashboard.Dashboard(parent).pack(fill=BOTH, expand=True)
            CTkButton(ff, text='تمام , شكرًا', font=('Cairo Medium', 20), command=back).pack(fill=X,padx=50,pady=(40,200))

        else:
            ref.execute("PRAGMA database_list;")
            ref.execute("SELECT * FROM Students")
            stds = ref.fetchall()
            for std in stds:
                droosin = loads(std[12])
                droosinlst = [droosini["name"] for droosini in droosin]
                print("filtred list : ",droosinlst)
                print("Option : ",(choice.get().strip()).split("|")[1])
                print("Non Filtred : ",droosin)
                if ((choice.get().strip()).split("|")[1]).strip() in droosinlst:
                    print((choice.get().strip()).split("|")[1])
                    ref.execute("UPDATE Students SET Badges = ? WHERE ID = ?", (choice.get().strip(), std[0]))
            ref.connection.commit()
            team = ((ref.fetchone()[2]).split("\\")[-1]).replace(".db", "")
            
            # Sanitize group name for file path
            sanitized_group = choice.get().strip().replace("|", "_").replace(" ", "_")
            
            with open(f'{team}/cache_{sanitized_group}.json', 'r') as infofile:
                 info = load(infofile) 
            ref.execute('INSERT INTO Spends VALUES (?,?,?,?)', ((int(entries[1].get_input()) * int(info['higher_than_average'])), f'{localtime().tm_mday} \ {localtime().tm_mon} \ {localtime().tm_year}', dumps({'inf':'مستلزمات للطلاب', 'nm':'النظام'}), None))
            conn.commit()
            for x in parent.winfo_children():
                x.destroy()
            ff = CTkFrame(parent, fg_color='white', corner_radius=10)
            ff.pack(fill=BOTH, padx=10,pady=10,expand=True)
            CTkLabel(ff, text='', image=CTkImage(Image.open('TDSAssets/General/done_unthemed.png'), size=(100,100))).pack(pady=(200,10))
            CTkLabel(ff,text='تم بنجاح', font=('FF Shamel Family Sans One Bold', 25)).pack(pady=10)
            CTkLabel(ff, text=f'تم الحساب\nالعدد المطبق : {info["higher_than_average"]} \n العدد المهمل : {info["lower_than_average"]}', font=('FF Shamel Family Sans One Book', 20)).pack(pady=5)
            def back():
                    for x in parent.winfo_children():
                        x.destroy()
                    Dashboard.Dashboard(parent).pack(fill=BOTH, expand=True)
            CTkButton(ff, text='تمام , شكرًا', font=('Cairo Medium', 20), command=back).pack(fill=X,padx=50,pady=(40,200))

    # -- GUI -- #
    # --- Form --- #
    # ---- Titling Frame ---- #
    Title = CTkFrame(parent, fg_color='white', corner_radius=10)
    CTkLabel(Title, text='', image=CTkImage(Image.open('TDSAssets/General/tag.png'), size=(60,60))).pack(side=RIGHT, padx=10, pady=10)
    CTkLabel(Title, text='إصدار مستلزمات للطلاب', font=('Cairo Medium', 25)).pack(side=RIGHT, padx=10, pady=10)
    Title.pack(fill=X, pady=10, padx=20)
    #END ---- Titling Frame ---- #
    # ---- Form Frame ---- #
    Form = CTkFrame(parent, fg_color='white', corner_radius=10, height=600)
    FAName = Entries.UpperLabeledEntry(Form, 'اسم المستلزم')
    FAName.pack(fill=X, padx=30, pady=30)
    FAPrice = Entries.UpperLabeledEntry(Form, 'سعر المستلزم')
    FAPrice.pack(fill=X, padx=30, pady=0)
    FAQnt = Entries.UpperLabeledEntry(Form, 'العدد')
    ref.execute('SELECT * FROM GROUPS')
    FAQnt.pack(fill=X, padx=30, pady=30)
    choices = [x[0] for x in ref.fetchall()]

    CTkOptionMenu(Form, values=choices, variable=choice).pack(pady=10, padx=40, fill=X)
    SelectionFrame = CTkFrame(Form, fg_color='transparent')
    SelectionFrame.pack()
    chk = StringVar(value='1')
    def Checked():
        if chk.get() == '1':
            FAQnt.entry.delete(0, END)
            FAQnt.entry.configure(fg_color='light grey', state='disabled')
        else:
            FAQnt.entry.delete(0, END)
            FAQnt.entry.configure(fg_color='white',  state='normal')
    Checked()
    CTkCheckBox(SelectionFrame, onvalue='1', offvalue='0',command=Checked,checkbox_height=30,variable=chk, checkbox_width=30,text='     تطبيق تقنية الإنتخاب     ', font=('Cairo Medium', 20)).pack(side=RIGHT, pady=(10,20))
    btns = CTkFrame(Form,fg_color='transparent')
    btns.pack(fill=X, pady=(50,10), padx=40)
    def back():
        for x in parent.winfo_children():
            x.destroy()
        Dashboard.Dashboard(parent).pack(fill=BOTH, expand=True)
    CTkButton(btns, text='تأكيد الإصدار',command=lambda:Selection(chk, (FAName, FAPrice, FAQnt)), font=('Cairo Medium', 19), fg_color='#399918', hover_color='#508D4E').pack(fill=X, pady=5, padx=2, side=RIGHT, expand=True)
    CTkButton(btns, text='الغاء',command=back, font=('Cairo Medium', 19), fg_color='#FF7777', hover_color='#FFAAAA').pack(pady=5, padx=2, side=LEFT)
    Form.pack(fill=BOTH, pady=10, padx=20)
    #END ---- Form Frame ---- #
    #END --- Form --- #
    #END -- GUI -- #


