from customtkinter import *
from json import dumps, loads
from Proccesors.Database.db import *
from Widgets.Entries import *
from PIL import Image
from time import localtime
from Widgets import Entries
from AlphaControllers import EntryValidators
from Proccesors.Genric import SessionSpendManager
from Views import whatsapptool
class QuizApplier:
    def __init__(self, session_data, frame=None, spends_frame=None):
        self.session_data = session_data
        self.lv = spends_frame
        self.frame = frame
        ref.execute("PRAGMA database_list;")
        team = ((ref.fetchone()[2]).split("\\")[-1]).replace(".db", "")
        conn_checker = connect("Application.db")
        ref_checker  = conn_checker.cursor()
        ref_checker.execute("SELECT * FROM PGroups WHERE Name = ?", (team,))
        type = ref_checker.fetchone()[2]
        if type == "بالحصة":
            self.qpath = 7
            self.apath = 10
        else:
            self.qpath = 7
            self.apath = 10
            
    def ShowCreationPopUp(self):
        self.popup = CTkToplevel()
        self.popup.attributes('-topmost', True)
        self.popup.title('انشاء امتحان')
        self.popup.geometry(f'400x550')
        header_frame = CTkFrame(self.popup, fg_color='transparent')
        header_frame.pack(pady=30)
        CTkLabel(header_frame, text='', image=CTkImage(Image.open('TDSAssets/General/test.png'), size=(70,70))).pack(padx=10, pady=5, side=RIGHT)
        CTkLabel(header_frame, text='انشاء امتحان قصير', font=('Cairo Medium', 30)).pack(side=RIGHT)

        self.quiz_title = UpperLabeledEntry(self.popup, 'عنوان الامتحان')
        self.quiz_title.pack(fill=X, padx=20, pady=10)
        self.quiz_max = UpperLabeledEntry(self.popup, 'الدرجة النهائية')
        self.quiz_max.pack(fill=X, padx=20, pady=10)
        self.quiz_prize = UpperLabeledEntry(self.popup, 'جائزة الامتحان , اللي مقفلين بس. سيب الخانه فاضيه لو مش هتدي جايزه')
        CTkButton(self.popup, text='انشاء الامتحان',command=self.ApplyQuiz, font=('Cairo Medium', 18), width=300).pack(padx=30, fill=X,pady=20)
        self.popup_size = (self.popup.winfo_height(), self.popup.winfo_width)
    def UpdateQuizFrame(self):
        for xyz in self.frame.winfo_children():
            xyz.destroy()
        qfm = CTkFrame(self.frame, fg_color='transparent')
        qfm.pack(side=RIGHT, fill=BOTH, expand=True, pady=5,padx=10)
        CTkLabel(qfm, text='', image=CTkImage(Image.open('TDSAssets/General/test.png'), size=(90,90))).pack(padx=10, pady=(30,10))
        ref.execute('SELECT * FROM Sessions WHERE ID = ?', (self.session_data[0],))
        quiz_data = loads(ref.fetchone()[self.qpath])
        CTkLabel(qfm, text=quiz_data['title'], font=('Cairo Medium',29)).pack(pady=(20,0))
        CTkButton(qfm, text="رصد الدرجات",command=lambda:self.AddDegrees(), font=('Cairo Medium',18)).pack(pady=(18,0), fill=X)

    def AddDegrees(self):
        ref.execute('SELECT * FROM Sessions WHERE ID = ?', (self.session_data[0],))
        quiz_data = loads(ref.fetchone()[self.qpath])
        self.addDegrees_popup = CTkToplevel()
        self.addDegrees_popup.title(f'رصد درجات امتحان {quiz_data["title"]}')
        self.addDegrees_popup.attributes('-topmost', True)
        header_frame = CTkFrame(self.addDegrees_popup, fg_color='transparent')
        header_frame.pack(pady=30)
        CTkLabel(header_frame, text='', image=CTkImage(Image.open('TDSAssets/General/test.png'), size=(70,70))).pack(padx=(10,10), pady=5, side=RIGHT)
        CTkLabel(header_frame, text='رصد الدرجات', font=('Cairo Medium', 30)).pack(side=RIGHT)

        kew = Entries.UpperLabeledEntry(self.addDegrees_popup, 'ادخل اسم الطالب \ الكود الخاص بيه')
        kew.pack(pady=(30,10),fill=X, padx=20)
        self.res = CTkScrollableFrame(self.addDegrees_popup, width=400)
        self.res.pack(fill=BOTH,expand=True, padx=30, pady=(0,20))
        kew.entry.bind('<KeyRelease>', self.Search)
        CTkLabel(self.res, text='', image=CTkImage(Image.open('TDSAssets/General/star.png'), size=(90,90))).pack(pady=(30,5))
        CTkLabel(self.res, text='ستظهر النتائج هنا بعد البحث', font=('Cairo Medium',17)).pack()
    def Search(self, event):
        if event.widget.get() == '':
            for xyz in self.res.winfo_children() :
                xyz.destroy()
            CTkLabel(self.res, text='', image=CTkImage(Image.open('TDSAssets/General/star.png'), size=(90,90))).pack(pady=(30,5))
            CTkLabel(self.res, text='ستظهر النتائج هنا بعد البحث', font=('Cairo Medium',17)).pack()
            return
        try:
            int(event.widget.get())
            ref.execute(f'SELECT * FROM Students WHERE ID = "{event.widget.get()}"')
            for x in self.res.winfo_children():
                x.destroy()
            for y in ref.fetchall():
                attendance_list = loads(y[6])
                try:
                    if any(d.get(self.session_data[1]) == 'Attended.' for d in attendance_list):
                        ff = CTkFrame(self.res, fg_color='#FEFBD8')
                        ff.pack(fill=X, padx=10, pady=5)
                        ff2 = CTkFrame(ff,fg_color='transparent')
                        ff2.pack(fill=X)
                        CTkLabel(ff2, text=y[1], font=('Cairo Medium', 17)).pack(side=RIGHT, padx=(3,7), pady=3)
                        CTkLabel(ff2, text=f'    كود الطالب : {y[0]}    ', fg_color='#FFD35A', font=('Cairo Medium', 15)).pack(side=RIGHT, pady=3, padx=10)
                        bt = CTkButton(ff2, text='رصد الدرجة', font=('Cairo Medium', 15))
                        bt.configure(command=lambda ID=ff, std = y, bt=bt: self.EditDegree(ID, std, bt))
                        bt.pack(side=LEFT, padx=5, pady=3)
                        for a in loads(y[7]):
                            try:
                                if a['session-data']['title'] == self.session_data[1]:
                                    bt.configure(state='disabled')
                                    descfrm = CTkFrame(ff,fg_color='transparent')
                                    descfrm.pack(fill=X, padx=7, pady=5)
                                    CTkLabel(descfrm, text=f'الدرجة : {a["degree"]}', font=('Cairo Medium',17), text_color='green').pack(side=RIGHT)
                            except:
                                pass
                except Exception as e:
                    print(e)
            if len(self.res.winfo_children()) == 0:
                CTkLabel(self.res, text='', image=CTkImage(Image.open('TDSAssets/General/error.png'), size=(90,90))).pack(pady=(30,5))
                CTkLabel(self.res, text= 'هذا الطالب غير حاضر او غير موجود', font=('Cairo Medium',17)).pack()

        except:
            ref.execute(f'SELECT * FROM Students WHERE Name LIKE "%{event.widget.get()}%"')
            for x in self.res.winfo_children():
                x.destroy()
            for y in ref.fetchall():
                attendance_list = loads(y[6])
                if any(d.get(self.session_data[1]) == 'Attended.' for d in attendance_list):
                    ff = CTkFrame(self.res, fg_color='#FEFBD8')
                    ff.pack(fill=X, padx=10, pady=5)
                    ff2 = CTkFrame(ff,fg_color='transparent')
                    ff2.pack(fill=X)
                    CTkLabel(ff2, text=y[1], font=('Cairo Medium', 17)).pack(side=RIGHT, padx=(3,7), pady=3)
                    CTkLabel(ff2, text=f'    كود الطالب : {y[0]}    ', fg_color='#FFD35A', font=('Cairo Medium', 15)).pack(side=RIGHT, pady=3, padx=10)
                    bt = CTkButton(ff2, text='رصد الدرجة', font=('Cairo Medium', 15))
                    bt.configure(command=lambda ID=ff, std = y, bt=bt: self.EditDegree(ID, std, bt))
                    bt.pack(side=LEFT, padx=5, pady=3)
                    for a in loads(y[7]):
                        try:
                            if a['session-data']['title'] == self.session_data[1]:
                                bt.configure(state='disabled')
                                descfrm = CTkFrame(ff,fg_color='transparent')
                                descfrm.pack(fill=X, padx=7, pady=5)
                                CTkLabel(descfrm, text=f'الدرجة : {a["degree"]}', font=('Cairo Medium',17), text_color='green').pack(side=RIGHT)
                        except:
                            pass
            if len(self.res.winfo_children()) == 0:
                CTkLabel(self.res, text='', image=CTkImage(Image.open('TDSAssets/General/error.png'), size=(90,90))).pack(pady=(30,5))
                CTkLabel(self.res, text= 'هذا الطالب غير حاضر او غير موجود', font=('Cairo Medium',17)).pack()

    def EditDegree(self, parent, student_data, bt):
        bt.configure(state='disabled')
        new_frame = CTkFrame(parent, fg_color='transparent')
        new_frame.pack(pady=5,fill=X, padx=7)
        degree = CTkEntry(new_frame, placeholder_text='الدرجة الجديدة', font=('Cairo Medium', 15), justify='right')
        degree.pack(fill=X, padx=(5,0), side=RIGHT, expand=True)
        def ApplyChanges():
            deg = degree.get()
            try:
                float(deg)
                ref.execute('SELECT * FROM Sessions WHERE ID = ?', (self.session_data[0],))
                self.session_data = ref.fetchone()
                if int(deg) <= int(loads(self.session_data[self.qpath])['max']):
                    new_frame.destroy()
                    ref.execute('SELECT * FROM Students WHERE ID = ?', (student_data[0], ))
                    student = ref.fetchone()
                    student_quizes = loads(student[7])
                    ref.execute('SELECT * FROM Sessions WHERE ID = ?', (self.session_data[0],))
                    self.session_data = ref.fetchone()
                    student_quizes.append(
                        {
                            'title' : loads(self.session_data[self.qpath])['title'],
                            'session-data' : {'id':self.session_data[0] , 'title':self.session_data[1]},
                            'degree' : deg
                        }
                    )
                    ref.execute('UPDATE Students SET Tests = ? WHERE ID = ?', (dumps(student_quizes), student_data[0]))
                    new_quizSession = loads(self.session_data[self.qpath])
                    new_quizSession['degrees'].append({student_data[1] : deg})
                    ref.execute('UPDATE Sessions SET Quiz = ? WHERE ID = ?', (dumps(new_quizSession), self.session_data[0]))
                    conn.commit()
                    helper = whatsapptool.WhatsAppHelper()
                    helper.SendMessage({"type" : "ExmDeg", "std_name" : student[1], "extitle" : loads(self.session_data[self.qpath])['title'], "exdeg" : deg, "exmax" : int(loads(self.session_data[self.qpath])['max'])},student[3])
                    helper.SendMessage({"type" : "ExmDeg", "std_name" : student[1], "extitle" : loads(self.session_data[self.qpath])['title'], "exdeg" : deg, "exmax" : int(loads(self.session_data[self.qpath])['max'])},student[4])
                    #####################################################################
                    ###########################3
                    ######################################33
                    ####################################33
                    descfrm = CTkFrame(parent,fg_color='transparent')
                    descfrm.pack(fill=X, padx=7, pady=5)

                    CTkLabel(descfrm, text=f'الدرجة : {deg}', font=('Cairo Medium',17), text_color='green').pack(side=RIGHT)

                else:
                    error = CTkToplevel()
                    error.title('حدث خطأ')
                    error.attributes('-topmost', True)
                    error.lift()
                    CTkLabel(error, text='', image=CTkImage(Image.open('TDSAssets/General/error.png'), size=(30,30))).pack(pady=(30,5), side=RIGHT)
                    CTkLabel(error, text= 'الدرجة اللي انت كتبتها اكبر من الدرجة النهائية', font=('Cairo Medium',17)).pack(side=RIGHT)
            except Exception as e:
                print(e)
                error = CTkToplevel()
                error.title('حدث خطأ')
                error.attributes('-topmost', True)
                error.lift()

                CTkLabel(error, text='', image=CTkImage(Image.open('TDSAssets/General/error.png'), size=(30,30))).pack(pady=(30,5), side=RIGHT)
                CTkLabel(error, text= 'اكتب رقم في الخانة ومتكتبش حروف', font=('Cairo Medium',17)).pack(side=RIGHT)
        CTkButton(new_frame, text='تأكيد', command=ApplyChanges, font=('Cairo Medium', 14)).pack(side=RIGHT)

    def QuizInfo(self):
        ref.execute('SELECT * FROM Sessions WHERE ID = ?', (self.session_data[0]))
        quiz_data = loads(ref.fetchone()[self.qpath])
        self.QuizInf_popup = CTkToplevel()
        self.QuizInf_popup.title(f'تفاصيل الإمتحان')
        self.QuizInf_popup.attributes('-topmost', True)


    def ApplyQuiz(self):
        if (EntryValidators.CheckBlank(self.quiz_title.entry), EntryValidators.CheckBlank(self.quiz_max.entry)):
            quiz_data = {
                'title': self.quiz_title.get_input(),
                'max': self.quiz_max.get_input(),
                'prize': self.quiz_prize.get_input(),
                'degrees': []
            }
            print("Quiz Data:", quiz_data)
            print("Session Data ID:", self.session_data[0])
            ref.execute('UPDATE Sessions SET Quiz = ? WHERE ID = ?', (dumps(quiz_data), self.session_data[0]))
            conn.commit()
            for x in self.popup.winfo_children():
                x.destroy()
            CTkLabel(self.popup, text='', image=CTkImage(Image.open('TDSAssets/General/ask.png'), size=(100,100))).pack(pady=(50,10))
            CTkLabel(self.popup, text='تم انشاء الامتحان , هل تريد حساب مطبوعات الإمتحان ؟', font=('Cairo Medium', 20), wraplength=300).pack(padx=30)
            attendance_num = 0
            ref.execute('SELECT * FROM Students')
            for x in ref.fetchall():
                attendance_list = loads(x[6])
                if any(d.get(self.session_data[1]) == 'Attended.' for d in attendance_list):
                    attendance_num += 1

            def back():
                self.popup.destroy()

            def printSpends():
                for x in self.popup.winfo_children():
                    x.destroy()
                CTkLabel(self.popup, text='', image=CTkImage(Image.open('TDSAssets/General/folder.png'), size=(100,100))).pack(pady=(50,10))
                CTkLabel(self.popup, text='حساب مصروفات طباعة الورق', font=('Cairo Medium', 20), wraplength=300).pack(padx=30)
                papers_num = Entries.UpperLabeledEntry(self.popup, 'عدد ورقات الامتحان')
                papers_num.pack(fill=X, pady=(20,10), padx=10)
                paper_price = Entries.UpperLabeledEntry(self.popup, 'سعر الورقة الواحدة')
                paper_price.pack(fill=X, pady=(0,67), padx=10)
                def apply():
                    if (
                        EntryValidators.CheckBlank(papers_num.entry),
                        EntryValidators.CheckBlank(paper_price.entry)
                    ):
                        today = f'{localtime().tm_mday} \ {localtime().tm_mon} \ {localtime().tm_year}'
                        ref.execute('SELECT * FROM Sessions WHERE ID = ?', (self.session_data[0],))
                        ref.execute('INSERT INTO Spends Values (?,?,?,?)', (f"{(int(papers_num.get_input()) * int( paper_price.get_input()) * int(ref.fetchone()[4]))}", today, dumps({"inf" : "طباعة ورق امتحان", 'nm':'عام'}), dumps({'stats':'session', 'session-info':{'id':self.session_data[0], 'title' : self.session_data[1]}})))
                        conn.commit()
                        SessionSpendManager.LoadSpendsForSession(self.lv, self.session_data)
                        self.popup.destroy()
                CTkButton(self.popup, text='تأكيد', command=apply,font=('Cairo Medium', 18), fg_color='#399918', hover=False).pack(fill=X, pady=(10,10), padx=10)

            CTkButton(self.popup, text='نعم , ادخل عدد الورقات والسعر', font=('Cairo Medium', 18),command=printSpends, fg_color='#399918', hover=False).pack(fill=X, pady=(160,10), padx=10)
            CTkButton(self.popup, text='لا , شــــــــكـــــرًا', font=('Cairo Medium', 18), command=back, fg_color='#EF5A6F', hover=False).pack(fill=X, pady=(0,10), padx=10)

            self.UpdateQuizFrame()