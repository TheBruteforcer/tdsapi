from customtkinter import *
from json import loads, dumps, JSONDecodeError
from time import localtime
from Proccesors.Database.db import conn, ref
from Views import Dashboard, whatsapptool
from PIL import Image
from sqlite3 import *
from tkinter import messagebox
import datetime

CUSTOM_MONTHS = [8, 9, 10, 11, 12, 1]
CUSTOM_MONTH_NAMES = {
    8: 'أغسطس', 9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر', 1: 'يناير'
}

def get_custom_month_name(month):
    return CUSTOM_MONTH_NAMES.get(month, str(month))

def safe_load_json(data, default=None):
    """Safely load JSON data, returning a default value if loading fails"""
    if not data:
        return default
    try:
        result = loads(data)
        return result if isinstance(result, list) else default
    except JSONDecodeError:
        return default

def ShowAccount(parent: CTkScrollableFrame, account_info):
    # Create loading indicator
    loading_frame = CTkFrame(parent, fg_color="transparent", corner_radius=15, height=500, width=500, border_width=2, border_color="grey")
    loading_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
    CTkLabel(loading_frame, text="جاري تحميل البيانات . كن صبورًا", font=("Cairo Medium", 16)).pack(pady=(70,0))
    progress_bar = CTkProgressBar(loading_frame, mode="indeterminate")
    progress_bar.pack(pady=20, padx=20, fill=X)
    progress_bar.start()
    parent.update()  # Force UI update to show loading screen

    # Reload account data to ensure we have latest info
    def ReloadAccountData():
        nonlocal account_info
        ref.execute('SELECT * FROM Students WHERE ID = ?', (account_info[0],))
        account_info = ref.fetchone()
    
    ReloadAccountData()
    
    # Clear existing UI
    for widget in parent.winfo_children():
        widget.destroy()

    # -- Title Frame -- #
    UpperingFrame = CTkFrame(parent, fg_color='white')
    UpperingFrame.pack(fill=X, padx=15, pady=10)

    CTkLabel(UpperingFrame, text='', image=CTkImage(Image.open('TDSAssets/General/student2.png'), size=(70,70))).pack(side=RIGHT, padx=10, pady=10)
    CTkLabel(UpperingFrame, text=account_info[1], font=('Cairo Medium', 20)).pack(side=RIGHT, padx=10, pady=(15,10))
    
    def back():
        for x in parent.winfo_children():
            x.destroy()
        Dashboard.Dashboard(parent).pack(fill=BOTH, expand=True)
    
    CTkButton(UpperingFrame, text='الرجوع الي الرئيسية', font=('Cairo Medium', 16), command=back).pack(side=LEFT, padx=10, ipady=10, ipadx=17)

    # -- Info Frame -- #
    InfoFrame = CTkFrame(parent, fg_color='transparent')
    InfoFrame.pack(fill=X, padx=5)
    
    RankFrame = CTkFrame(InfoFrame, fg_color='white', corner_radius=10)
    RankFrame.pack(side=RIGHT, padx=10, pady=5)
    CTkLabel(RankFrame, text='', image=CTkImage(Image.open('TDSAssets/General/trophy.png'), size=(60,60))).pack(side=RIGHT, padx=(10,30), pady=10)
    CTkLabel(RankFrame, text=f'تصنيف الطالب  : {account_info[5]}', font=('Cairo Medium', 18)).pack(side=RIGHT, padx=(30,10), pady=(15,10))
    RankFrame = CTkFrame(InfoFrame, fg_color='white', corner_radius=10)
    RankFrame.pack(side=RIGHT, padx=10, pady=5)
    CTkLabel(RankFrame, text='', image=CTkImage(Image.open('TDSAssets/General/green_money.png'), size=(60,60))).pack(side=RIGHT, padx=(10,30), pady=10)
    CTkLabel(RankFrame, text=f'مبلغ الاشتراك : {account_info[11]}', font=('Cairo Medium', 18)).pack(side=RIGHT, padx=(30,10), pady=(15,10))
    
    Oper = CTkFrame(InfoFrame, fg_color='white', corner_radius=10)
    Oper.pack(side=RIGHT, padx=10, pady=5)
    CTkLabel(Oper, text='', image=CTkImage(Image.open('TDSAssets/General/board2.png'), size=(50,50))).pack(side=RIGHT, padx=(10,30), pady=10)
    
    # Fix attendance percentage calculation
    attendance_percent = "0"
    try:
        attendance_percent = int(float(account_info[9]))
    except (ValueError, TypeError):
        pass
    
    CTkLabel(Oper, text=f'نسبة الحضور : %{attendance_percent}', font=('Cairo Medium', 18)).pack(side=RIGHT, padx=(30,10), pady=(15,10))
    
    Stat = CTkFrame(InfoFrame, fg_color='white', corner_radius=10)
    Stat.pack(side=RIGHT, padx=10, pady=5)
    CTkLabel(Stat, text='', image=CTkImage(Image.open('TDSAssets/General/ask.png'), size=(50,50))).pack(side=RIGHT, padx=(10,30), pady=10)
    CTkLabel(Stat, text=f'حالة الطالب : عادي', font=('Cairo Medium', 18)).pack(side=RIGHT, padx=(30,10), pady=(15,10))
    
    # Get team information more efficiently
    type = "بالشهر" if account_info[10] != "BySession" else "بالجلسة"  # Always assign a value to type

    # Payment section for monthly subscriptions
    if type == "بالشهر":
        PFrame = CTkScrollableFrame(parent, height=400, fg_color='white', label_text="سجل الدفع", label_font=('Cairo Medium', 16))
        
        # Load the PayHistory data safely
        pay_history = []
        try:
            if account_info[10]:
                pay_history = loads(account_info[10])
        except (JSONDecodeError, TypeError):
            pay_history = []
        
        # Convert to list if it's a dictionary (fixing inconsistent data structure)
        if isinstance(pay_history, dict):
            pay_history = [pay_history]
        
        # Function to handle payment process
        def pay(month_name):
            student_id = account_info[0]
            
            # Load student groups and calculate total from groups
            droos_in = safe_load_json(account_info[12], default=[])
            calculated_price = sum(int(group.get("price", 0)) for group in droos_in)
            
            # Get manually set subscription amount
            manual_price = int(account_info[11]) if account_info[11] else 0
            
            # Validate payment
            if calculated_price == 0 and manual_price == 0:
                messagebox.showerror("لا يمكن تنفيذ العملية", "متأكد انك ضايف الطالب لمجموعات المواد ؟")
                return
            
            # Determine final price - use manual price if set, otherwise use calculated price
            final_price = manual_price if manual_price > 0 else calculated_price
            
            # Update payment history
            current_pay_history = safe_load_json(account_info[10], default=[])
            if isinstance(current_pay_history, dict):
                current_pay_history = [current_pay_history]
            
            # Update the specific month's payment status
            for entry in current_pay_history:
                if entry.get("month") == month_name:
                    entry["state"] = "تم"
                    entry["date_payed"] = datetime.date.today().strftime("%d/%m")
                    break
            
            try:
                with ref.connection as conn:
                    cursor = conn.cursor()
                    
                    # Update student data - note we keep the manual subscription amount
                    cursor.execute("""
                        UPDATE Students 
                        SET PayHistory = ?, SubscribtionAmount = ? 
                        WHERE ID = ?
                    """, (dumps(current_pay_history), final_price, student_id))
                    
                    # Record gain with the final price
                    from datetime import datetime
                    now = datetime.datetime.now()
                    today = now.strftime('%d \\ %m \\ %Y')
                    time_str = now.strftime('%I:%M %p')
                    date_with_time = f'{today} - {time_str}'
                    cursor.execute("SELECT COUNT(*) FROM Gains")
                    next_id = cursor.fetchone()[0] + 1
                    cursor.execute("""
                        INSERT INTO Gains (ID, Type, Qnt, Date) 
                        VALUES (?, ?, ?, ?)
                    """, (
                        f"{next_id}C",
                        dumps({'title': 'SPay', 'SName': account_info[1]}),
                        str(final_price),
                        date_with_time
                    ))
                
                # Send notifications
                helper = whatsapptool.WhatsAppHelper()
                for phone in (account_info[3], account_info[4]):
                    if phone and phone.strip():
                        helper.SendMessage({"type": "PMonth", "std_name": account_info[1]}, phone)
                
                # Refresh UI
                ShowAccount(parent, account_info)
                
            except Exception as e:
                messagebox.showerror("خطأ في العملية", f"حدث خطأ أثناء تحديث البيانات: {str(e)}")
        
        # Create UI elements for payment history
        if pay_history:
            for month in pay_history:
                if not isinstance(month, dict):
                    continue
                    
                ff = CTkFrame(PFrame)
                ff.pack(fill="x", padx=5, pady=(10, 0))
                
                # Determine icon based on payment state
                icon_name = "done" if month.get("state") == "تم" else "error"
                CTkLabel(ff, text='', image=CTkImage(Image.open(f'TDSAssets/General/{icon_name}.png'), size=(50, 50))).pack(side="right", padx=(10, 10), pady=10)
                
                # Month name
                month_name = month.get("month", "Unknown")
                if month_name in CUSTOM_MONTHS:
                    CTkLabel(ff, text=get_custom_month_name(int(month_name)), font=('Tajawal Medium', 24)).pack(side="right", pady=(7, 0))
                else:
                    CTkLabel(ff, text=month_name, font=('Tajawal Medium', 24)).pack(side="right", pady=(7, 0))
                
                # Payment status
                CTkLabel(ff, text=month.get("state", "Unknown"), font=('Cairo Medium', 15)).pack(side="right", pady=(7, 0), padx=20)
                
                # Payment button (only if unpaid)
                if month.get("state") == "لم يدفع":
                    expiry = month.get("expire", "غير معروف")
                    CTkLabel(ff, text=f"مهلة الدفع : {expiry}", font=('Cairo Medium', 15)).pack(side="right", pady=(7, 0), padx=20)
                    
                    CTkButton(ff, command=lambda m=month.get("month"): pay(m), text="دفع", font=('Tajawal Medium', 21)).pack(side="left", pady=(7, 0), padx=20, ipady=10)
                else:
                    payment_date = month.get("date_payed", "غير معروف")
                    CTkLabel(ff, text=f"تم الدفع في : {payment_date}", font=('Cairo Medium', 15)).pack(side="right", pady=(7, 0), padx=20)
        else:
            CTkLabel(PFrame, text="لا يوجد سجل دفع", font=('Cairo Medium', 18)).pack(pady=20)
        
        PFrame.pack(fill="both", pady=5, padx=5)
        
        # Groups section
        GFrame = CTkScrollableFrame(parent, height=400, fg_color='white', label_text="المجموعات", label_font=('Cairo Medium', 16))
        
        # Load DroosIn data safely
        droos_in = []
        try:
            if account_info[12]:
                droos_in = loads(account_info[12])
        except (JSONDecodeError, TypeError):
            droos_in = []
        
        if not isinstance(droos_in, list):
            droos_in = []
        
        # Display student's groups
        for drs in droos_in:
            if not isinstance(drs, dict):
                continue
                
            ff = CTkFrame(GFrame)
            ff.pack(fill=X, padx=5, pady=(10,0))
            CTkLabel(ff, text=drs.get("name", "Unknown"), font=('Tajawal Medium', 24)).pack(side=RIGHT, pady=15, padx=10)
            
            def delete_from_group(group_map):
                group_name = group_map.get("name")
                if not group_name:
                    return
                
                # Find the group in InvSessions
                ref.execute("SELECT ID, JoinedNumber FROM InvSessions WHERE Name = ?", (group_name,))
                group_row = ref.fetchone()
                
                if group_row:
                    group_id, joined_number = group_row
                    
                    # Decrement JoinedNumber safely
                    new_joined_number = max(0, joined_number - 1)
                    
                    # Get current DroosIn
                    student_id = account_info[0]
                    current_droos_in = []
                    try:
                        if account_info[12]:
                            current_droos_in = loads(account_info[12])
                            if not isinstance(current_droos_in, list):
                                current_droos_in = []
                    except (JSONDecodeError, TypeError):
                        current_droos_in = []
                    
                    # Filter out the group
                    current_droos_in = [d for d in current_droos_in if d.get("name") != group_name]
                    
                    # Update database
                    try:
                        with ref.connection:
                            ref.execute("UPDATE InvSessions SET JoinedNumber = ? WHERE ID = ?", 
                                       (new_joined_number, group_id))
                            ref.execute("UPDATE Students SET DroosIn = ? WHERE ID = ?", 
                                       (dumps(current_droos_in), student_id))
                        # Refresh UI
                        ShowAccount(parent, account_info)
                    except Exception as e:
                        messagebox.showerror("خطأ في العملية", f"حدث خطأ أثناء تحديث البيانات: {str(e)}")
            
            CTkButton(ff, fg_color="red", text="حذف الطالب من المجموعة", 
                     command=lambda g=drs: delete_from_group(g), 
                     font=("Cairo Medium", 15)).pack(side=LEFT, padx=10)
        
        def add_to_group():
            xshow1 = CTkToplevel()
            xshow1.geometry("500x400")
            xshow1.attributes("-topmost", True)
            xshow1.title("إضافة إلى مجموعة")
            
            Mainxshow1Frame = CTkScrollableFrame(xshow1, fg_color="white", height=300, width=330)
            
            # Fetch all available groups
            ref.execute("SELECT * FROM InvSessions")
            indvsessions = ref.fetchall()
            
            # Get student's current groups
            current_droos_in = []
            try:
                if account_info[12]:
                    current_droos_in = loads(account_info[12])
                    if not isinstance(current_droos_in, list):
                        current_droos_in = []
            except (JSONDecodeError, TypeError):
                current_droos_in = []
            
            # Convert to a set for quick lookup
            existing_groups = {drs.get("name", "") for drs in current_droos_in if isinstance(drs, dict)}
            
            group_added = False
            for indvsession in indvsessions:
                group_id = indvsession[0]
                group_name = indvsession[1].strip() if indvsession[1] else ""
                joined_number = indvsession[2]
                group_price = indvsession[3]
                
                # Skip groups that are already added
                if group_name in existing_groups:
                    continue
                
                group_added = True
                ff = CTkFrame(Mainxshow1Frame)
                ff.pack(fill=X, padx=5, pady=(10,0))
                
                CTkLabel(ff, text=group_name, font=('Tajawal Medium', 24)).pack(side=RIGHT, pady=(7,0))
                
                def add_group_to_student(group):
                    student_id = account_info[0]
                    
                    # Get current droos_in
                    current_groups = []
                    try:
                        if account_info[12]:
                            current_groups = loads(account_info[12])
                            if not isinstance(current_groups, list):
                                current_groups = []
                    except (JSONDecodeError, TypeError):
                        current_groups = []
                    
                    # Append new group details
                    current_groups.append({
                        "name": group.get("name", ""),
                        "price": group.get("price", "0")
                    })
                    
                    # Update database efficiently
                    try:
                        with ref.connection:
                            ref.execute(
                                "UPDATE Students SET DroosIn = ? WHERE ID = ?", 
                                (dumps(current_groups), student_id)
                            )
                            ref.execute(
                                "UPDATE InvSessions SET JoinedNumber = ? WHERE ID = ?", 
                                (group.get("joined_number", 0) + 1, group.get("id", ""))
                            )
                        
                        # Send notifications
                        helper = whatsapptool.WhatsAppHelper()
                        if account_info[3] and account_info[3].strip():
                            helper.SendMessage({
                                "type": "GAdd", 
                                "std_name": account_info[1], 
                                "inv_name": group.get("name", ""), 
                                "inv_price": group.get("price", ""), 
                                "inv_time": "-------"
                            }, account_info[3])
                        
                        if account_info[4] and account_info[4].strip():
                            helper.SendMessage({
                                "type": "GAdd", 
                                "std_name": account_info[1], 
                                "inv_name": group.get("name", ""), 
                                "inv_price": group.get("price", ""), 
                                "inv_time": "-------"
                            }, account_info[4])
                        
                        # Refresh UI and close dialog
                        ShowAccount(parent, account_info)
                        xshow1.destroy()
                    except Exception as e:
                        messagebox.showerror("خطأ في العملية", f"حدث خطأ أثناء إضافة المجموعة: {str(e)}")
                
                # Add button to join the group
                CTkButton(ff, text="إضافة", font=("Cairo Medium", 19), 
                         command=lambda g={
                             "id": group_id, 
                             "name": group_name, 
                             "price": group_price, 
                             "joined_number": joined_number
                         }: add_group_to_student(g)
                ).pack(side=LEFT, padx=5, pady=5)
            
            if not group_added:
                CTkLabel(Mainxshow1Frame, text="لا توجد مجموعات متاحة للإضافة", font=('Cairo Medium', 18)).pack(pady=20)
            
            Mainxshow1Frame.pack(fill=BOTH, pady=5, padx=5)
        
        # Add button to manually set subscription amount
        def set_subscription_amount():
            dialog = CTkToplevel()
            dialog.geometry("400x200")
            dialog.attributes("-topmost", True)
            dialog.title("تعديل قيمة الاشتراك")
            
            frame = CTkFrame(dialog, fg_color="white")
            frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
            
            CTkLabel(frame, text="قيمة الاشتراك الجديدة", font=('Cairo Medium', 16)).pack(pady=(10,5))
            amount_entry = CTkEntry(frame, font=('Cairo Medium', 14))
            amount_entry.pack(pady=5, padx=20, fill=X)
            
            def save_amount():
                try:
                    new_amount = int(amount_entry.get())
                    ref.execute("UPDATE Students SET SubscribtionAmount = ? WHERE ID = ?", 
                               (new_amount, account_info[0]))
                    ref.connection.commit()
                    dialog.destroy()
                    ShowAccount(parent, account_info)  # Refresh view
                except ValueError:
                    messagebox.showerror("خطأ", "برجاء إدخال رقم صحيح")
            
            CTkButton(frame, text="حفظ", font=('Cairo Medium', 16), 
                     command=save_amount).pack(pady=20)

        subscription_button = CTkButton(parent, command=set_subscription_amount,
                                      text="تعديل قيمة الاشتراك يدويًا",
                                      font=("Cairo Medium", 20))
        subscription_button.pack(fill=X, padx=17, pady=10)

        # Original add to group button
        CTkButton(GFrame, command=add_to_group, 
                 text="إضافة الطالب إلى مجموعة", 
                 font=("Cairo Medium", 20)).pack(fill=X, padx=10, pady=10)
        GFrame.pack(fill=X, padx=17, pady=10)
    else:  # Session-based payment section
        # Add button to manually set subscription amount for session-based students
        def set_session_subscription_amount():
            dialog = CTkToplevel()
            dialog.geometry("400x200")
            dialog.attributes("-topmost", True)
            dialog.title("تعديل قيمة الاشتراك")
            
            frame = CTkFrame(dialog, fg_color="white")
            frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
            
            CTkLabel(frame, text="قيمة الاشتراك الجديدة", font=('Cairo Medium', 16)).pack(pady=(10,5))
            amount_entry = CTkEntry(frame, font=('Cairo Medium', 14))
            amount_entry.pack(pady=5, padx=20, fill=X)
            
            def save_amount():
                try:
                    new_amount = int(amount_entry.get())
                    ref.execute("UPDATE Students SET SubscribtionAmount = ? WHERE ID = ?", 
                               (new_amount, account_info[0]))
                    ref.connection.commit()
                    dialog.destroy()
                    ShowAccount(parent, account_info)  # Refresh view
                except ValueError:
                    messagebox.showerror("خطأ", "برجاء إدخال رقم صحيح")
            
            CTkButton(frame, text="حفظ", font=('Cairo Medium', 16), 
                     command=save_amount).pack(pady=20)

        subscription_button = CTkButton(parent, command=set_session_subscription_amount,
                                      text="تعديل قيمة الاشتراك يدويًا",
                                      font=("Cairo Medium", 20))
        subscription_button.pack(fill=X, padx=17, pady=10)

        # Group card for session-based students
        GFrame = CTkFrame(parent, fg_color='white', corner_radius=10)
        GFrame.pack(fill=X, padx=17, pady=10)
        
        CTkLabel(GFrame, text="المجموعة", font=('Cairo Medium', 18)).pack(pady=(10,5))
        
        # Load DroosIn data safely
        droos_in = []
        try:
            if account_info[8]:
                    group = account_info[8]  # Get first (and should be only) group
                    CTkLabel(GFrame, text=group, 
                            font=('Tajawal Medium', 24)).pack(pady=10)
        except (JSONDecodeError, TypeError):
            CTkLabel(GFrame, text="غير مسجل في مجموعة", 
                    font=('Tajawal Medium', 24)).pack(pady=10)

    # Attendance records
    AFrame = CTkScrollableFrame(parent, height=400, fg_color='white', label_text='سجل الحضور', label_font=('Cairo Medium', 16))
    
    # Safely get sessions and attendance records
    sessions = []
    try:
        ref.execute("SELECT * FROM Sessions WHERE StartTime = ?", (account_info[8],))
        sessions = ref.fetchall()
    except Exception as e:
        print(f"Error fetching sessions: {e}")
    
    attendances = []
    try:
        if account_info[6]:
            attendances = loads(account_info[6])
            if not isinstance(attendances, list):
                attendances = []
    except (JSONDecodeError, TypeError):
        attendances = []
    
    # Display attendance records
    attendance_found = False
    for session_data in sessions:
        if not session_data or len(session_data) < 2:
            continue
            
        session_name = session_data[1].strip() if session_data[1] else ""
        
        # Check if student attended this session
        attended = False
        for record in attendances:
            if isinstance(record, dict) and session_name in record and record[session_name] == "Attended.":
                attended = True
                break
        
        attendance_found = True
        ff = CTkFrame(AFrame)
        ff.pack(fill=X, padx=5, pady=(10,0))
        
        icon_name = "done" if attended else "error"
        CTkLabel(ff, text='', image=CTkImage(Image.open(f'TDSAssets/General/{icon_name}.png'), size=(50,50))).pack(side=RIGHT, padx=(10,10), pady=10)
        CTkLabel(ff, text=session_name, font=('Tajawal Medium', 24)).pack(side=RIGHT, pady=(7,0))
        
        status_text = 'الطالب حضر' if attended else 'الطالب لم يحضر'
        CTkLabel(ff, text=status_text, font=('Cairo Medium', 15)).pack(side=RIGHT, pady=(7,0), padx=20)
    
    if not attendance_found:
        CTkLabel(AFrame, text="لا يوجد سجل حضور", font=('Cairo Medium', 18)).pack(pady=20)
    
    AFrame.pack(fill=X, padx=17, pady=10)
    
    # Test results
    TestsFrame = CTkScrollableFrame(parent, height=400, fg_color='white', label_text='درجات الامتحانات', label_font=('Cairo Medium', 16))
    
    # Safely load test results
    tests = []
    try:
        if account_info[7]:
            tests = loads(account_info[7])
            if not isinstance(tests, list):
                tests = []
    except (JSONDecodeError, TypeError):
        tests = []
    
    # Remove empty entries
    tests = [test for test in tests if isinstance(test, dict) and test]
    
    # Display test results
    if tests:
        for test in tests:
            ff = CTkFrame(TestsFrame)
            ff.pack(fill=X, padx=5, pady=(10,0))
            CTkLabel(ff, text='', image=CTkImage(Image.open('TDSAssets/General/test.png'), size=(50,50))).pack(side=RIGHT, padx=(10,10), pady=10)
            CTkLabel(ff, text=test.get('title', 'Unknown'), font=('Tajawal Medium', 20)).pack(side=RIGHT, pady=(7,0))
            CTkLabel(ff, text=f'الدرجة : {test.get("degree", "N/A")}', font=('Cairo Medium', 15)).pack(side=RIGHT, pady=(7,0), padx=20)
    else:
        CTkLabel(TestsFrame, text="لا يوجد درجات امتحانات", font=('Cairo Medium', 18)).pack(pady=20)
    
    TestsFrame.pack(fill=X, padx=17, pady=10)
    
    # Badges
    BadgesFrame = CTkFrame(parent, fg_color='white')
    BadgesFrame.pack(fill=X, padx=17, pady=5)
    
    try:
        attendance_percent = float(account_info[9]) if account_info[9] else 0
        rank = int(account_info[5]) if account_info[5] else 0
        
        if attendance_percent >= 75:
            CTkLabel(BadgesFrame, text='', image=CTkImage(Image.open('TDSAssets/Badges/attndstd.png'), size=(400,400))).pack(side=RIGHT, padx=10, pady=10)
        
        if rank < 5:
            CTkLabel(BadgesFrame, text='', image=CTkImage(Image.open('TDSAssets/Badges/1ststd.png'), size=(400,400))).pack(side=RIGHT, padx=10, pady=10)
        
        CTkLabel(BadgesFrame, text='', image=CTkImage(Image.open('TDSAssets/Badges/newstd.png'), size=(400,400))).pack(side=RIGHT, padx=10, pady=10)
    except (ValueError, TypeError) as e:
        print(f"Error displaying badges: {e}")
        CTkLabel(BadgesFrame, text='خطأ في عرض الشارات', font=('Cairo Medium', 18)).pack(pady=20)