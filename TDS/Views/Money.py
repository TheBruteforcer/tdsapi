from customtkinter import *
from PIL import Image
from Views import Dashboard
from time import localtime
from Proccesors.Database.db import ref
from json import loads
from sqlite3 import *
import datetime
from collections import defaultdict
import re
"""
I need here some modifications in this code,
First check for mode by this code ..

`
    ref.execute("PRAGMA database_list;")
    team = ((ref.fetchone()[2]).split("\\")[-1]).replace(".db", "")
    conn_checker = connect("Application.db")
    ref_checker  = conn_checker.cursor()
    ref_checker.execute("SELECT * FROM PGroups WHERE Name = ?", (team,))
    type = ref_checker.fetchone()[2]
`
type is like a real value ("بالشهر", "بالحصة")
if type == "بالحصة"
don't change anything in logic of the code !
if type == "بالشهر"
modify the gains logic
 -> make a new logic of listing the gains
   -> list in the same customframe widget frame "ff"
    -> `
        ff = CTkFrame(spendslist2, fg_color='white')
        ff.pack(padx=5, pady=5, fill=X)
        CTkLabel(ff, text='', image=CTkImage(Image.open('TDSAssets/General/green_up.png'), size=(40, 40))).pack(pady=5, padx=5, side=RIGHT)
        CTkLabel(ff, text=session_title, font=('Cairo Medium', 20)).pack(side=RIGHT, padx=10)
        CTkLabel(ff, text=f'E£ {gain_info["total"]:,}', font=('Cairo Medium', 18)).pack(side=RIGHT, padx=10)
        CTkLabel(ff, text=f'الوقت : {gain_info["dates"][0]}', font=('Cairo Medium', 18)).pack(side=RIGHT, padx=10)
       `
    -> don't sum gains and view it in one customframe like the other logic
    -> this is gain table scheme :
     -> `
        CREATE TABLE IF NOT EXISTS Gains (
            ID   TEXT,
            Type TEXT,
            Qnt  TEXT,
            Date TEXT
        );
        ` 
    -> Type is in this scheme : `dumps({'title' : 'SPay', 'SName' : account_info[1]})`
    -> set the text of CTkLabel(ff, text=session_title, font=('Cairo Medium', 20)).pack(side=RIGHT, padx=10)
       to "دفع شهر للطالب {type_of_gain["SName"]}"
    -> then show the total.
"""


def show(frame: CTkFrame):
    def back():
        for x in frame.winfo_children():
            x.destroy()
        Dashboard.Dashboard(frame).pack(fill=BOTH, expand=True)

    def get_date_range(key):
        today = datetime.datetime.today()
        if key == 'يوم':
            start_date = end_date = today
        elif key == 'اسبوع':
            end_date = today - datetime.timedelta(days=today.weekday() + 1)
            start_date = end_date - datetime.timedelta(days=6)
        elif key == 'شهر':
            start_date = today.replace(day=1)
            next_month = today.replace(day=28) + datetime.timedelta(days=4)
            end_date = next_month - datetime.timedelta(days=next_month.day)
        elif key == 'سنة':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        else:
            start_date = end_date = today  # Default to today if key is not recognized
        return start_date, end_date

    def format_date(date):
        return f'{date.day:02d} \\ {date.month:02d} \\ {date.year}'

    def filter_data(key):
        key = key.strip()
        start_date, end_date = get_date_range(key)
        total_spends = 0
        total_gains = 0
        
        # Clear previous lists
        for x in spendslist.winfo_children():
            x.destroy()
        for x in spendslist2.winfo_children():
            x.destroy()
        for z in total.winfo_children():
            z.destroy()

        current_date = start_date
        spends = []
        gain_records_ = []

        # Fetch spends and gains for the date range
        while current_date <= end_date:
            formatted_date = format_date(current_date)
            print("DEBUG: Filtering with date string:", formatted_date)
            ref.execute('SELECT Date FROM Gains')
            print("DEBUG: Dates in DB:", [row[0] for row in ref.fetchall()])
            ref.execute(f'SELECT * FROM Spends WHERE Date LIKE "{formatted_date}%"')
            spends.extend(ref.fetchall())
            # Fetch gains where the date part matches
            ref.execute(f'SELECT * FROM Gains WHERE Date LIKE "{formatted_date}%"')
            gain_records = ref.fetchall() 
            gain_records_.extend(gain_records)
            current_date += datetime.timedelta(days=1)

        # --- Display Spends ---
        if spends:
            for x in spends:
                total_spends += int(x[0])
                ff = CTkFrame(spendslist, fg_color='white')
                ff.pack(padx=5, pady=5, fill=X)
                CTkLabel(ff, text='', image=CTkImage(Image.open('TDSAssets/General/red_down.png'), size=(40, 40))).pack(pady=5, padx=5, side=RIGHT)
                CTkLabel(ff, text=loads(x[2])['inf'], font=('Cairo Medium', 20)).pack(side=RIGHT, padx=10)
                CTkLabel(ff, text=loads(x[2])['nm'], font=('Cairo Medium', 20), text_color='green').pack(side=RIGHT, padx=10)
                CTkLabel(ff, text=f'E£ {int(x[0]):,}', font=('Cairo Medium', 18)).pack(side=RIGHT, padx=10)
                CTkLabel(ff, text=f'الوقت : {x[1]}', font=('Cairo Medium', 18)).pack(side=RIGHT, padx=10)
            CTkLabel(total, text=f'المجموع : {total_spends} جنيه مصري', font=('Cairo Medium', 18)).pack(side=RIGHT, pady=5, padx=20)
        else:
            CTkLabel(total, text='غير متوفر', font=('Cairo Medium', 18)).pack(side=RIGHT, pady=5, padx=20)
            ff = CTkFrame(spendslist, fg_color='transparent')
            ff.pack(pady=120)
            CTkLabel(ff, text='', image=CTkImage(Image.open('TDSAssets/General/red_bag.png'), size=(40, 40))).pack(pady=5, padx=5, side=RIGHT)
            CTkLabel(ff, text='ستظهر المصروفات هنا عند الإضافة', font=('Cairo Medium', 20)).pack(side=RIGHT, padx=10)

        # --- Display All Gains (Session and Monthly) ---
        # Group gains by session ID
        session_gains = defaultdict(list)
        for gain in gain_records_:
            session_id = str(gain[0])
            session_gains[session_id].append(gain)
        
        for session_id, gains in session_gains.items():
            if "C" in session_id:
                # Monthly payments: list each payment directly, no big frame
                for gain in gains:
                    amount = int(float(gain[2]))
                    date = gain[3]
                    try:
                        type_info = loads(gain[1]) if gain[1] else {}
                    except Exception:
                        type_info = {}
                    student_name = type_info.get("SName", "طالب غير معروف")
                    payment_frame = CTkFrame(spendslist2, fg_color='white', corner_radius=8)
                    payment_frame.pack(fill=X, padx=10, pady=3)
                    CTkLabel(payment_frame, text='', image=CTkImage(Image.open('TDSAssets/General/green_up.png'), size=(30, 30))).pack(side=RIGHT, padx=5)
                    CTkLabel(payment_frame, text=f'دفع شهر للطالب {student_name}', font=('Cairo Medium', 16)).pack(side=RIGHT, padx=10)
                    CTkLabel(payment_frame, text=f'E£ {amount:,}', font=('Cairo Medium', 15)).pack(side=RIGHT, padx=10)
                    CTkLabel(payment_frame, text=f'الوقت : {date}', font=('Cairo Medium', 15)).pack(side=RIGHT, padx=10)
                    total_gains += amount
            else:
                # Session or custom gains: use big frame
                ref.execute(f'SELECT Title FROM Sessions WHERE ID = ?', (session_id,))
                session_title = ref.fetchone()
                session_title = session_title[0] if session_title else (gains[0][1] if gains[0][1] else f'جلسة رقم ({session_id})')
                session_frame = CTkFrame(spendslist2, fg_color='#f5f5f5', corner_radius=15)
                session_frame.pack(fill=X, padx=5, pady=(15,5))
                title_bar = CTkFrame(session_frame, fg_color='#e0e0e0', corner_radius=10)
                title_bar.pack(fill=X, padx=0, pady=(0,5))
                CTkLabel(title_bar, text=session_title, font=('Cairo Medium', 20, 'bold')).pack(side=RIGHT, padx=15, pady=8)
                for gain in gains:
                    amount = int(float(gain[2]))
                    date = gain[3]
                    payment_frame = CTkFrame(session_frame, fg_color='white', corner_radius=8)
                    payment_frame.pack(fill=X, padx=10, pady=3)
                    session_id_inner = str(gain[0])
                    if gain[1] and not gain[1].startswith('{'):
                        # Custom gain (title in gain[1])
                        CTkLabel(payment_frame, text='', image=CTkImage(Image.open('TDSAssets/General/note.png'), size=(30, 30))).pack(side=RIGHT, padx=5)
                        match = re.search(r'\(ID:(\d+)\)', gain[1])
                        if match:
                            desc = gain[1].replace(match.group(0), '').strip()
                            student_id = match.group(1)
                            # Fetch student name by ID
                            ref.execute('SELECT Name FROM Students WHERE ID = ?', (student_id,))
                            student_row = ref.fetchone()
                            student_name = student_row[0] if student_row else f'غير معروف ({student_id})'
                            display_text = f'{desc} - الطالب: {student_name} (كود: {student_id})'
                        else:
                            display_text = gain[1]
                        CTkLabel(payment_frame, text=display_text, font=('Cairo Medium', 16)).pack(side=RIGHT, padx=10)
                    else:
                        # Session payment
                        ref.execute(f'SELECT Title FROM Sessions WHERE ID = ?', (session_id_inner,))
                        session_title_inner = ref.fetchone()
                        session_title_inner = session_title_inner[0] if session_title_inner else f'جلسة رقم ({session_id_inner})'
                        CTkLabel(payment_frame, text='', image=CTkImage(Image.open('TDSAssets/General/green_up.png'), size=(30, 30))).pack(side=RIGHT, padx=5)
                        CTkLabel(payment_frame, text=session_title_inner, font=('Cairo Medium', 16)).pack(side=RIGHT, padx=10)
                    CTkLabel(payment_frame, text=f'E£ {amount:,}', font=('Cairo Medium', 15)).pack(side=RIGHT, padx=10)
                    CTkLabel(payment_frame, text=f'الوقت : {date}', font=('Cairo Medium', 15)).pack(side=RIGHT, padx=10)
                    total_gains += amount
        CTkLabel(total, text=f'إجمالي الأرباح : {total_gains} جنيه مصري', font=('Cairo Medium', 18)).pack(side=RIGHT, pady=5, padx=20)

    for x in frame.winfo_children():
        x.destroy()
    
    title = CTkFrame(frame)
    title.pack(side=TOP, fill=X, padx=10, pady=10)
    CTkLabel(title, text='', image=CTkImage(Image.open('TDSAssets/General/green_bag.png'), size=(60, 60))).pack(side=RIGHT, pady=10, padx=(15, 10))
    tt = CTkFrame(title, fg_color='transparent')
    tt.pack(side=RIGHT)
    CTkLabel(tt, text='الماليات', font=('Cairo Medium', 25), compound='right', anchor='e').pack(fill=X)
    
    today = localtime()
    formatted_today = f'{today.tm_mday} \ {today.tm_mon} \ {today.tm_year}'
    
    CTkButton(title, text='العودة الي الصفحة الرئيسية', font=('Cairo Medium', 17), command=back).pack(side=LEFT, padx=15)
    
    listingfrm = CTkFrame(frame, fg_color='transparent')
    listingfrm.pack(fill=X, pady=10, padx=10)
    
    filterfrm = CTkFrame(listingfrm)
    filterfrm.pack(fill=X)
    filterI = StringVar(value='  يوم  ')
    fiss = CTkFrame(listingfrm, fg_color='transparent')
    fiss.pack(fill=X, expand=True)
    spendslist = CTkScrollableFrame(fiss, height=430, label_fg_color='#F4CE14', label_text='المصروفات', label_font=('Cairo Medium', 15))
    spendslist2 = CTkScrollableFrame(fiss, height=430, label_fg_color='#F4CE14', label_text='الأرباح', label_font=('Cairo Medium', 15))
    
    CTkLabel(filterfrm, text='فلترة في مدة زمنية', font=('Cairo Medium', 18)).pack(side=RIGHT, pady=5, padx=(0, 10))
    CTkOptionMenu(filterfrm, command=filter_data, variable=filterI, values=['  يوم  ', '  اسبوع  ', '  شهر  ', '  سنة  '], font=('Cairo Medium', 16), anchor='e').pack(side=LEFT, padx=10)

    total = CTkFrame(listingfrm)
    filter_data('يوم')
    
    spendslist2.pack(pady=10, fill=X, side=RIGHT, expand=True, padx=10)
    total.pack(fill=X)
