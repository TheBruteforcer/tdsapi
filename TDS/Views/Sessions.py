from customtkinter import *
from PIL import Image
from Proccesors.Database.db import *
from Proccesors.Genric import AttendService, Loaders, SessionSpendManager, ExtractFA, CustomGain, CompleteSession
from Widgets import Entries
from awesometkinter import RadialProgressbar
from ServicesApplier.TestManagment.Quiz import QuizApplier
from time import localtime
from Proccesors.AutoProcessors.AttendanceProcess import AProccess
import json
from AlphaControllers import EntryValidators
from Views import Dashboard, SessionsSettings, AddStdForm
import tkinter.messagebox as messagebox

# --- Custom Add Student Form for Session ---
def SessionAddStdForm(parent, group_name, on_success=None):
    """
    Custom Add Student Form for session mode.
    Sets the group/badge automatically for the new student.
    Calls on_success callback after adding.
    """
    def after_add(student_id):
        try:
            ref.execute("UPDATE Students SET Group = ?, Badges = ? WHERE ID = ?", (group_name, group_name, student_id))
            conn.commit()
            if on_success:
                on_success()
            messagebox.showinfo("تم", "تم إضافة الطالب وتعيين المجموعة بنجاح!")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تعيين المجموعة: {str(e)}")
    AddStdForm.apply(parent, after_add=after_add)

class Session:
    def __init__(self, frame : CTkScrollableFrame):
        self.frame = frame
        self.create(frame)
    def create(self, frame : CTkFrame):
        for widget in frame.winfo_children():
            widget.destroy()
        title = CTkFrame(frame, fg_color='transparent')
        title.pack(pady=40)
        CTkLabel(title, text='', image=CTkImage(Image.open('TDSAssets/General/board.png'), size=(90,90))).pack(side=RIGHT, padx=(5,0), pady=5)
        CTkLabel(title, text='بدء حصة جديدة', font=('Cairo Medium', 40)).pack(side=RIGHT, padx=4, pady=(0,8))
        self.sstitle = Entries.UpperLabeledEntry(frame, 'عنوان الحصه')
        self.sstitle.pack(fill=X, padx=120, pady=(30,10))
        self.duration = Entries.SdidedEntryLabel(frame, 'مدة الحصة', 'ساعة')
        self.duration.pack(fill=X, padx=130, pady=(30,10))
        self.price = Entries.SdidedEntryLabel(frame, 'سعر الحصة', "جنيه")
        self.price.pack(fill=X, padx=130, pady=(30,10))
        self.repId = Entries.UpperLabeledEntry(frame, 'هل هذه الحصه تعتبر معاد أخر لحصه اخرى ؟ لو اه اكتب معرف الحصه هنا او اتركه فارغ')
        self.repId.pack(fill=X, padx=120, pady=(30,10))
        ref.execute('SELECT * FROM GROUPS')
        choices = [x[0] for x in ref.fetchall()]
        self.choice = StringVar(value = "اختر المجموعه")
        CTkOptionMenu(frame, values=choices, variable=self.choice, font=('Cairo Meidum', 25)).pack(pady=10, padx=130, fill=X, ipadx=10,ipady=10)
        btns = CTkFrame(frame,fg_color='transparent')
        btns.pack(fill=X, pady=(20,10), padx=130)
        def back():
            for x in frame.winfo_children():
                x.destroy()
            SessionsSettings.go(self.frame)
        CTkButton(btns, text='دخول الحصة',command=self.applysessionDat, font=('Cairo Medium', 19), fg_color='#399918', hover_color='#508D4E').pack(fill=X, pady=5, padx=2, side=RIGHT, expand=True)
        CTkButton(btns, text='الغاء',command=back, font=('Cairo Medium', 19), fg_color='#FF7777', hover_color='#FFAAAA').pack(pady=5, padx=2, side=LEFT)
        CTkLabel(frame, text='* بمجرد الضغط علي دخول الحصه , سوف تدخل الى ادارة الحصه مباشرةً', font=('Cairo Medium',16), text_color='red').pack()

    def applysessionDat(self):
        if True:
            if (
                EntryValidators.CheckBlank(self.sstitle.entry),
                EntryValidators.CheckBlank(self.duration.entry),
                EntryValidators.CheckBlank(self.price.entry)
            ):
                ref.execute('SELECT * FROM Sessions')
                lists = ref.fetchall()
                lists.reverse() 
                try:
                    id = int(lists[0][0]) + 1
                except:
                    id = '1'
                today = f'{localtime().tm_mday} \ {localtime().tm_mon} \ {localtime().tm_year}'
                ref.execute(
                    'INSERT INTO Sessions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                    (
                        id,
                        self.sstitle.get_input(),
                        self.duration.get_input(),
                        self.price.get_input(),
                        '0',
                        id,
                        id,
                        json.dumps([]),
                        json.dumps(
                            [
                                {'title' : "عد فلوس الحصه", 'done' : 'no'},
                                {'title' : "عد الطلاب في القاعة", 'done' : 'no'},
                                {'title' : "راجع الحضور", 'done' : 'no'}
                            ]
                        ),
                        today,
                        self.choice.get(),
                        self.repId.get_input()
                    )
                )
                conn.commit()
                self.moderateSession(id)
                ref.execute("SELECT * FROM Students")
                stds = ref.fetchall()
                # Normalize group name comparison for badge setting
                def normalize_group_name(name):
                    return name.strip().lower()
                selected_group = normalize_group_name(self.choice.get())
                for std in stds:
                    droosin = loads(std[12])
                    droosinlst = [normalize_group_name(droosini["name"]) for droosini in droosin]
                    if selected_group in droosinlst:
                        ref.execute("UPDATE Students SET Badges = ? WHERE ID = ?", (self.choice.get(), std[0]))
                conn.commit()
                self.moderateSession(id)
    def moderateSession(self, id):
        parent = self.frame.nametowidget(self.frame.winfo_parent())
        hints = CTkFrame(parent, fg_color='white', corner_radius=0)
        hints.pack(fill=X,side=BOTTOM)
        CTkLabel(hints, text='', image=CTkImage(Image.open('TDSAssets/General/bulb.png'), size=(40,40))).pack(side=RIGHT, padx=(5,15), pady=7)
        CTkLabel(hints, text='كمل مهمة عد الفلوس في اخر الحصة واعمل الامتحان القصير بعد ما تتأكد ان بنسبة قليلة هيجيلك طالب تحضره', font=('Cairo Medium', 17)).pack(side=RIGHT, padx=10)
        CTkButton(hints, text='X', font=('Arial', 16,'bold'), command=lambda:hints.destroy(), width=40).pack(side=LEFT, padx=10,pady=5)
        ref.execute('SELECT * FROM Sessions WHERE ID = ?', (id,))
        session_data = ref.fetchone()
        def reload_session_data():
            global session_data
            ref.execute('SELECT * FROM Sessions WHERE ID = ?', (id,))
            session_data = ref.fetchone()
        for x in self.frame.winfo_children():
            x.destroy()
        parent = CTkFrame(self.frame, fg_color='transparent')
        parent.pack(fill=BOTH, expand=True)
        info_frame = CTkFrame(parent, fg_color='white', border_width=2, border_color='#8D493A')
        CTkLabel(info_frame, text=session_data[1], font=('Cairo Medium',30)).pack(pady=(60,10))
        CTkLabel(info_frame, text=f'كود الحصه : {session_data[0]}', font=('Cairo Medium',18)).pack()
        AttendsNum = CTkLabel(info_frame, text=f'عدد الحاضرين : {session_data[4]}', text_color='#131842', font=('Cairo Medium', 18))
        AttendsNum.pack(pady=0)
        CTkLabel(info_frame, text=f'مدة الحصة : {session_data[2]}', font=('Cairo Medium',18)).pack(pady=(0,5))
        attend = CTkFrame(parent, fg_color='white', border_width=2, border_color="#399918")
        secfm = CTkFrame(attend, fg_color='transparent')
        secfm.pack(side=RIGHT, fill=BOTH, expand=True, pady=5,padx=10)
        CTkLabel(secfm, text='', image=CTkImage(Image.open('TDSAssets/General/student3.png'), size=(110,110))).pack(padx=10, pady=(30,10))
        attendslbl1 = CTkLabel(secfm, text='عدد الحضور : 0', font=('Cairo Medium', 30))
        attendslbl1.pack()
        percentage = CTkFrame(parent, fg_color='white')
        yattend = CTkFrame(percentage, fg_color='transparent')
        yattend.pack(fill=BOTH, expand=True, side=RIGHT,pady=(40,10),padx=(0,10))
        nattend = CTkFrame(percentage, fg_color='transparent')
        nattend.pack(fill=BOTH, expand=True, side=RIGHT, pady=(40,10),padx=(10,0))
        circular = CTkFrame(yattend, fg_color='#36BA98', corner_radius=180, width=100, height=100)
        circular.pack(pady=(15,10))
        attendplbl = CTkLabel(circular, text='0%', font=('Arial', 45, 'bold'), text_color='white')
        attendplbl.pack(fill=BOTH, expand=True, padx=25,pady=43)
        CTkLabel(yattend, text='نسبة الحضور', font=('Cairo Medium', 20)).pack()
        circular2 = CTkFrame(nattend, fg_color='#E76F51', corner_radius=180, width=100, height=100)
        circular2.pack(pady=(15,10))
        nattendplbl = CTkLabel(circular2, text='100%', font=('Arial', 45, 'bold'), text_color='white')
        nattendplbl.pack(fill=BOTH, expand=True, padx=25,pady=43)
        CTkLabel(nattend, text='نسبة الغياب', font=('Cairo Medium', 20)).pack()
        AProccess(session_data, attendslbl1, AttendsNum, attendplbl, nattendplbl)
        CTkButton(secfm, text='تحضير طالب جديد',command=lambda : AttendService.Apply(session_data, attendslbl1, AttendsNum, attendplbl, nattendplbl), font=('Cairo Medium',18)).pack(pady=(20,5), fill=X)
        def show_adding_form():
            xshowed = CTkToplevel()
            xshowed.geometry("800x500")
            xshowedscrll = CTkScrollableFrame(xshowed, fg_color="white")
            xshowedscrll.pack(fill=BOTH, expand=True)
            # Use the custom session add student form with live preview
            SessionAddStdForm(xshowedscrll, session_data[10], on_success=lambda: AProccess(session_data, attendslbl1, AttendsNum, attendplbl, nattendplbl))
        CTkButton(secfm, text='إضافة طالب جديد',command=show_adding_form, font=('Cairo Medium',18)).pack(pady=(0, 20), fill=X)
        quiz = CTkFrame(parent, fg_color='white')
        qfm = CTkFrame(quiz, fg_color='transparent')
        qfm.pack(side=RIGHT, fill=BOTH, expand=True, pady=5,padx=10)
        CTkLabel(qfm, text='', image=CTkImage(Image.open('TDSAssets/General/test.png'), size=(90,90))).pack(padx=10, pady=(30,10))
        CTkLabel(qfm, text='لم يتم انشاء امتحانات', font=('Cairo Medium', 30)).pack()
        printage = CTkFrame(parent, fg_color='white')
        pfm = CTkFrame(printage, fg_color='transparent')
        pfm.pack(side=RIGHT, fill=BOTH, expand=True, pady=5,padx=10)
        CTkLabel(pfm, text='', image=CTkImage(Image.open('TDSAssets/General/printer.png'), size=(90,90))).pack(padx=10, pady=(30,10))
        CTkLabel(pfm, text='استخراج مستلزمات للحضور', font=('Cairo Medium', 30)).pack()
        latest_spends = CTkScrollableFrame(parent,  label_text='أخر المصروفات',height=300, label_font=('Cairo Medium', 16))
        reload_session_data()
        CTkButton(pfm, text="انشاء", font=('Cairo Medium',18), command=lambda : ExtractFA.Pop(latest_spends, session_data[0])).pack(pady=(40,20), fill=X)
        spend = CTkFrame(parent, fg_color='white')
        sfm = CTkFrame(spend, fg_color='transparent')
        sfm.pack(side=RIGHT, fill=BOTH, expand=True, pady=5,padx=10)
        CTkLabel(sfm, text='', image=CTkImage(Image.open('TDSAssets/General/ui_red_bag.png'), size=(110,110))).pack(padx=10, pady=(30,10))
        CTkLabel(sfm, text='المالية', font=('Cairo Medium', 30)).pack()
        notes = CTkScrollableFrame(parent)
        notes.grid(row=2, column=0, columnspan=2, sticky='nsew', pady=5,padx=5)
        ref.execute('SELECT * FROM Sessions WHERE ID = ?', (id,))
        session_data = ref.fetchone()
        latest_spends.grid(row=2, column=2, sticky='nsew',pady=5,padx=5)
        SessionSpendManager.LoadSpendsForSession(latest_spends, session_data)
        CTkButton(sfm, text="اضافة مصروف جديد", font=('Cairo Medium',18), command=lambda : SessionSpendManager.AddSpend(latest_spends, session_data)).pack(pady=10, fill=X)
        CTkButton(sfm, text="اضافة ربح جديد", font=('Cairo Medium',18), command=lambda : CustomGain.AddCustomGain(session_data)).pack(pady=(0,20), fill=X)
        CTkButton(qfm, text="انشاء امتحان",command=lambda:QuizApplier(session_data, quiz, latest_spends).ShowCreationPopUp(), font=('Cairo Medium',18)).pack(pady=(40,20), fill=X)
        endframe = CTkFrame(parent, fg_color='white', corner_radius=25)
        titling_frame = CTkFrame(endframe, fg_color='transparent')
        titling_frame.pack(side=RIGHT, padx=20,pady=10, fill=Y)
        CTkLabel(titling_frame, text='', image=CTkImage(Image.open('TDSAssets/General/settings.png'), size=(100,100))).pack(padx=10, pady=(10,10))
        CTkLabel(titling_frame, text='إعدادات الحصة', font=('FF Shamel Family Sans One Bold', 16)).pack(padx=(5,0))
        buttons_frame = CTkFrame(endframe, fg_color='white', corner_radius = 25)
        buttons_frame.pack(fill=Y, padx=10, pady=10, side=LEFT)
        CTkButton(buttons_frame, text='انهاء الحصة', font=('FF Shamel Family Sans One Bold', 19), image=CTkImage(Image.open('TDSAssets/General/backbutton.png'), size=(60,60)), compound=TOP, command=lambda:CompleteSession.complete(parent, session_data)).pack(fill=BOTH, padx=(20,0), pady=20)
        endframe.grid(row=3, column=0, columnspan=3, sticky='nsew', pady=10)
        quiz.grid(row=1, column=0, sticky='nsew', pady=5,padx=5)
        printage.grid(row=1, column=1, sticky='nsew', pady=5,padx=5)
        percentage.grid(row=0, column=2, sticky='nsew', pady=5,padx=5)
        info_frame.grid(row=0, column=0, sticky='nsew', pady=5,padx=5)
        attend.grid(row=0, column=1, sticky='nsew', pady=5,padx=5)
        spend.grid(row=1, column=2, sticky='nsew', pady=5,padx=5)
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(2, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        parent.rowconfigure(2, weight=1)