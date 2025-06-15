from customtkinter import *
import json
from Widgets import Entries
from Proccesors.Database.db import *
from PIL import Image
from threading import Thread
from time import localtime, sleep
from Views import StudentAccount

def Apply(session_data, attendslbl1, AttendsNum, attendplbl, nattendplbl):
    tt = CTkToplevel()
    tt.attributes('-topmost', True)
    tt.geometry('700x650')
    tt.title('تحضير طالب')
    title = CTkFrame(tt, fg_color='transparent')
    title.pack(pady=30)
    CTkLabel(title, text='', image=CTkImage(Image.open('TDSAssets/General/student3.png'), size=(90,90))).pack(padx=10, side=RIGHT)
    CTkLabel(title, text='تحضير طالب', font=('Cairo Medium',38)).pack(side=RIGHT, padx=(60,10))
    kew = Entries.UpperLabeledEntry(tt, 'ادخل اسم الطالب \ الكود الخاص بيه')
    kew.pack(pady=(30,10),fill=X, padx=20)
    res = CTkScrollableFrame(tt, height=400)
    res.pack(fill=X, padx=30)
    CTkLabel(res, text='', image=CTkImage(Image.open('TDSAssets/General/star.png'), size=(90,90))).pack(pady=(30,5))
    CTkLabel(res, text='ستظهر النتائج هنا بعد البحث', font=('Cairo Medium',17)).pack()
    def apply(id):
        MAX_RETRIES = 30
        retry_count = 0
        
        while retry_count < MAX_RETRIES:
            try:

                if True == "بالحصة":
                    gpath = 10
                    apath = 4
                else:
                    gpath = 10
                    apath = 4
                
                ref.execute(f'SELECT * FROM Students WHERE ID = "{id}"')
                std = ref.fetchone()
                attnds = json.loads(std[6])
                attnds.append({f"{session_data[1]}" : "Attended.", "enter_time" : f"{localtime().tm_min} : {localtime().tm_hour} "})
                attnds_json = json.dumps(attnds)
                
                # محاولة تنفيذ التحديث
                query = "UPDATE Students SET Attendance = ? WHERE ID = ?"
                ref.execute(query, (attnds_json, id))
                
                # باقي العمليات
                ref.execute('SELECT * FROM Students WHERE Badges = ?', (session_data[gpath],))
                studentsnum = len(ref.fetchall())
                ref.execute('SELECT * FROM Sessions WHERE ID = ?', (session_data[0],))
                session_data2 = ref.fetchone()
                new_attends = int(session_data2[apath]) + 1
                ref.execute(f'UPDATE Sessions SET Attendance = "{new_attends}" WHERE ID = "{session_data[0]}"')
                if std[10] == "BySession":
                    today = f'{localtime().tm_mday} \ {localtime().tm_mon} \ {localtime().tm_year}'
                    ref.execute('INSERT INTO Gains VALUES (?, ?, ?, ?)', (session_data2[0], None, session_data2[3], today))
                    
                # إذا نجحت كل العمليات، نقوم بتحديث الواجهة وإنهاء الحلقة
                conn.commit()
                
                # تحديث الواجهة
                attendslbl1.configure(text=f'عدد الحضور : {new_attends}')
                AttendsNum.configure(text=f'عدد الحضور : {new_attends}')
                per = (new_attends / studentsnum) * 100
                attendplbl.configure(text=f"{int(per)}%")
                nattendplbl.configure(text=f"{100-int(per)}%")
                
                # تحديث قائمة الطلاب
                ref.execute(f'SELECT * FROM Students WHERE ID = "{id}"')
                for x in res.winfo_children():
                    x.destroy()
                for y in ref.fetchall():
                    def normalize_group_name(name):
                        return name.strip().lower()
                    student_badge = normalize_group_name(y[8]) if y[8] else ""
                    session_group = normalize_group_name(session_data[10])
                    in_group = student_badge == session_group
                    if not in_group:
                        try:
                            droosin = json.loads(y[12]) if y[12] else []
                            droosinlst = [normalize_group_name(droosini["name"]) for droosini in droosin]
                            in_group = session_group in droosinlst
                        except Exception:
                            in_group = False
                    if in_group:
                        ff = CTkFrame(res, fg_color='#FEFBD8')
                        ff.pack(fill=X, padx=10, pady=5)
                        CTkLabel(ff, text=y[1], font=('Cairo Medium', 17)).pack(side=RIGHT, padx=(3,7), pady=3)
                        CTkLabel(ff, text=f'    كود الطالب : {y[0]}    ', fg_color='#FFD35A', font=('Cairo Medium', 15)).pack(side=RIGHT, pady=3, padx=10)
                        # Deserialize the JSON data
                        attendance_list = json.loads(y[6])
                        def openaccount(id):
                            tt = CTkToplevel()
                            tt.geometry("800x520")
                            tt.title("حساب الطالب")
                            tt.attributes("-topmost", True)
                            ss = CTkScrollableFrame(tt)
                            ss.pack(fill=BOTH, expand=True)
                            StudentAccount.ShowAccount(ss, id)
                        CTkButton(ff,command=lambda id = y: openaccount(id) , text='صفحة الطالب', font=('Cairo Medium', 15), fg_color='black').pack(side=LEFT, padx=5, pady=3)
                        # Check if the specific session is marked as 'Attended.'
                        if any(d.get(session_data[1]) == 'Attended.' for d in attendance_list):
                            CTkButton(ff, text='الطالب حاضر', font=('Cairo Medium', 15), state='disabled', fg_color='black').pack(side=LEFT, padx=5, pady=3)
                        else:
                            CTkButton(ff, text='تحضير الطالب', font=('Cairo Medium', 15), command=lambda ID=y[0]: apply(ID)).pack(side=LEFT, padx=5, pady=3)
                
                # إذا نجحت كل العمليات، نخرج من الحلقة
                break
                
            except Exception as e:
                retry_count += 1
                print(f"محاولة {retry_count} من {MAX_RETRIES}")
                print(f"خطأ: {str(e)}")
                
                if retry_count < MAX_RETRIES:
                    # انتظر قليلاً قبل المحاولة التالية
                    sleep(1)
                    continue
                else:
                    # إظهار رسالة خطأ للمستخدم
                    error_window = CTkToplevel()
                    error_window.title("خطأ")
                    error_window.geometry("400x200")
                    CTkLabel(error_window, 
                            text="حدث خطأ أثناء محاولة تسجيل الحضور\nالرجاء المحاولة مرة أخرى",
                            font=('Cairo Medium', 14)).pack(pady=20)
                    CTkButton(error_window, 
                             text="حسناً",
                             command=error_window.destroy,
                             font=('Cairo Medium', 14)).pack()
                    break

    def ontype_search(event):
        if event.widget.get() == '':
            for xyz in res.winfo_children() :
                xyz.destroy()
            CTkLabel(res, text='', image=CTkImage(Image.open('TDSAssets/General/star.png'), size=(90,90))).pack(pady=(30,5))
            CTkLabel(res, text='ستظهر النتائج هنا بعد البحث', font=('Cairo Medium',17)).pack()
            return

        gpath  =10
        try:
            int(event.widget.get()) 
            ref.execute(f'SELECT * FROM Students WHERE ID = "{event.widget.get()}"')
            for x in res.winfo_children():
                x.destroy()
            for y in ref.fetchall():
                def normalize_group_name(name):
                    return name.strip().lower()
                student_badge = normalize_group_name(y[8]) if y[8] else ""
                session_group = normalize_group_name(session_data[10])
                in_group = student_badge == session_group
                if not in_group:
                    try:
                        droosin = json.loads(y[12]) if y[12] else []
                        droosinlst = [normalize_group_name(droosini["name"]) for droosini in droosin]
                        in_group = session_group in droosinlst
                    except Exception:
                        in_group = False
                if in_group:
                    ff = CTkFrame(res, fg_color='#FEFBD8')
                    ff.pack(fill=X, padx=10, pady=5)
                    CTkLabel(ff, text=y[1], font=('Cairo Medium', 17)).pack(side=RIGHT, padx=(3,7), pady=3)
                    CTkLabel(ff, text=f'    كود الطالب : {y[0]}    ', fg_color='#FFD35A', font=('Cairo Medium', 15)).pack(side=RIGHT, pady=3, padx=10)
                    # Deserialize the JSON data
                    attendance_list = json.loads(y[6])
                    def openaccount(id):
                        tt = CTkToplevel()
                        tt.geometry("800x520")
                        tt.title("حساب الطالب")
                        tt.attributes("-topmost", True)
                        ss = CTkScrollableFrame(tt)
                        ss.pack(fill=BOTH, expand=True)
                        StudentAccount.ShowAccount(ss, id)
                    CTkButton(ff,command=lambda id = y: openaccount(id) , text='صفحة الطالب', font=('Cairo Medium', 15), fg_color='black').pack(side=LEFT, padx=5, pady=3)
                    # Check if the specific session is marked as 'Attended.'
                    if any(d.get(session_data[1]) == 'Attended.' for d in attendance_list):
                        CTkButton(ff, text='الطالب حاضر', font=('Cairo Medium', 15), state='disabled', fg_color='black').pack(side=LEFT, padx=5, pady=3)
                    else:
                        CTkButton(ff, text='تحضير الطالب', font=('Cairo Medium', 15), command=lambda ID=y[0]: apply(ID)).pack(side=LEFT, padx=5, pady=3)

        except:
            if len(event.widget.get()) >= 2:
                ref.execute(f'SELECT * FROM Students WHERE Name LIKE "%{event.widget.get()}%"')
                for x in res.winfo_children():
                    x.destroy()
                for y in ref.fetchall():
                    def normalize_group_name(name):
                        return name.strip().lower()
                    student_badge = normalize_group_name(y[8]) if y[8] else ""
                    session_group = normalize_group_name(session_data[10])
                    in_group = student_badge == session_group
                    if not in_group:
                        try:
                            droosin = json.loads(y[12]) if y[12] else []
                            droosinlst = [normalize_group_name(droosini["name"]) for droosini in droosin]
                            in_group = session_group in droosinlst
                        except Exception:
                            in_group = False
                    if in_group:
                        ff = CTkFrame(res, fg_color='#FEFBD8')
                        ff.pack(fill=X, padx=10, pady=5)
                        CTkLabel(ff, text=y[1], font=('Cairo Medium', 17)).pack(side=RIGHT, padx=(3,7), pady=3)
                        CTkLabel(ff, text=f'    كود الطالب : {y[0]}    ', fg_color='#FFD35A', font=('Cairo Medium', 15)).pack(side=RIGHT, pady=3, padx=10)
                        # Deserialize the JSON data
                        attendance_list = json.loads(y[6])
                        def openaccount(id):
                            tt = CTkToplevel()
                            tt.geometry("800x520")
                            tt.title("حساب الطالب")
                            tt.attributes("-topmost", True)
                            ss = CTkScrollableFrame(tt)
                            ss.pack(fill=BOTH, expand=True)
                            StudentAccount.ShowAccount(ss, id)
                        CTkButton(ff,command=lambda id = y: openaccount(id) , text='صفحة الطالب', font=('Cairo Medium', 15), fg_color='black').pack(side=LEFT, padx=5, pady=3)
                        # Check if the specific session is marked as 'Attended.'
                        if any(d.get(session_data[1]) == 'Attended.' for d in attendance_list):
                            CTkButton(ff, text='الطالب حاضر', font=('Cairo Medium', 15), state='disabled', fg_color='black').pack(side=LEFT, padx=5, pady=3)
                        else:
                            CTkButton(ff, text='تحضير الطالب', font=('Cairo Medium', 15), command=lambda ID=y[0]: apply(ID)).pack(side=LEFT, padx=5, pady=3)
            else:
                for x in res.winfo_children():
                    x.destroy()
                CTkLabel(res, text='اكتب حرفين او اكتر للبحث', font=('FF Shamel Family Sans One Bold', 20)).pack(pady=40)

    
    kew.entry.bind('<KeyRelease>', ontype_search)