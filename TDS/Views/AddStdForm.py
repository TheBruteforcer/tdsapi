from customtkinter import *
from Widgets import Entries
from Views import Dashboard, whatsapptool
from AlphaControllers import EntryValidators
from Proccesors.Database.db import *
import json
from tkinter import messagebox
from sqlite3 import *

def apply(frame: CTkFrame, after_add=None):
    """
    نموذج إضافة طالب جديد مع دعم التحقق، منع التكرار، واختيار المجموعات والاشتراك.
    الآن مع معاينة مباشرة لبيانات الطالب.
    """
    for x in frame.winfo_children():
        x.destroy()
    
    frame2 = CTkFrame(frame, fg_color='White')
    frame2.pack(fill=BOTH, expand=True)
    
    CTkLabel(frame2, text='      بيانات الطالـب       ', font=('Cairo Medium', 22), anchor='e', fg_color='#f6f9fc').pack(fill=X, ipadx=10, ipady=5)
    
    name = Entries.UpperLabeledEntry(frame2, 'اسم الطالب')
    name.pack(pady=(10,10), fill=X, padx=10)
    
    cn = Entries.UpperLabeledEntry(frame2, 'رقم تليفون الطالب')
    cn.pack(pady=10, fill=X, padx=10)
    
    fq = Entries.UpperLabeledEntry(frame2, 'رقم تليفون ولي أمر الطالب')
    fq.pack(pady=20, fill=X, padx=20)
    
    fwq = Entries.UpperLabeledEntry(frame2, 'رقم ولي أمر اخر (اختياري)')
    fwq.pack(pady=20, fill=X, padx=20)
    typeofpayment = StringVar(value="بالحصة")
    payment_menu = CTkOptionMenu(frame2, values=["بالحصة", "بالشهر"], variable=typeofpayment, font=('Cairo Medium', 18))
    payment_menu.pack(pady=10, padx=30, fill=X, ipadx=10, ipady=10)
    
    # إطار ثابت أعلى الأزرار لكل ما يتغير حسب نوع الدفع
    dynamic_holder = CTkFrame(frame2, fg_color='transparent')
    dynamic_holder.pack(fill=X, padx=10, pady=5)

    # --- Preview Frame ---
    preview_frame = CTkFrame(frame2, fg_color='#F7F7F7', corner_radius=12, border_width=1, border_color='#1976D2')
    preview_frame.pack(fill=X, padx=10, pady=(10, 5))
    preview_title = CTkLabel(preview_frame, text='معاينة بيانات الطالب', font=('Cairo Medium', 18, 'bold'), text_color='#1976D2')
    preview_title.pack(pady=(5, 0))
    preview_content = CTkLabel(preview_frame, text='', font=('Cairo Medium', 15), anchor='e', justify='right')
    preview_content.pack(pady=5, padx=10, fill=X)

    payment_mode = StringVar(value="نهاية الشهر")
    ref.execute('SELECT * FROM Groups')
    group_choices = [x[0] for x in ref.fetchall()]
    group_vars = []

    def clear_dynamic():
        for widget in dynamic_holder.winfo_children():
            widget.destroy()
        group_vars.clear()

    def update_preview(*args):
        # Gather current values
        n = name.get_input().strip()
        sphone = cn.get_input().strip()
        pphone = fq.get_input().strip()
        payment = typeofpayment.get()
        # Groups
        if hasattr(dynamic_holder, 'selected_groups_func'):
            groups = dynamic_holder.selected_groups_func()
        else:
            groups = []
        # Subscription
        subscribtion = ''
        if hasattr(dynamic_holder, 'subscribtion_entry'):
            subscribtion = dynamic_holder.subscribtion_entry.get_input().strip()
        # Compose preview text
        lines = []
        lines.append(f"الاسم: {n if n else '-'}")
        lines.append(f"رقم الطالب: {sphone if sphone else '-'}")
        lines.append(f"رقم ولي الأمر: {pphone if pphone else '-'}")
        lines.append(f"نوع الدفع: {payment}")
        lines.append(f"المجموعة/المجموعات: {', '.join(groups) if groups else '-'}")
        lines.append(f"قيمة الاشتراك: {subscribtion if subscribtion else '-'}")
        preview_content.configure(text='\n'.join(lines))

    def update_visibility(*args):
        clear_dynamic()
        if typeofpayment.get() == "بالشهر":
            payment_mode_menu_local = CTkOptionMenu(dynamic_holder, values=["بداية الشهر", "نهاية الشهر"], variable=payment_mode, font=('Cairo Medium', 18))
            payment_mode_menu_local.pack(pady=10, fill=X)
            group_frame = CTkFrame(dynamic_holder, fg_color='transparent')
            CTkLabel(group_frame, text='اختر المجموعات التي ينضم إليها الطالب', font=('Cairo Medium', 16), anchor='e').pack(fill=X, padx=10)
            for g in group_choices:
                var = BooleanVar()
                chk = CTkCheckBox(group_frame, text=g, variable=var, font=('Cairo Medium', 15), onvalue=True, offvalue=False)
                chk.pack(anchor='e', padx=20, pady=2)
                group_vars.append(var)
                var.trace_add('write', update_preview)
            group_frame.pack(fill=X, padx=10, pady=5)
            subscribtion_label = CTkLabel(dynamic_holder, text='قيمة الاشتراك الشهري (جنيه)', font=('Cairo Medium', 16), anchor='e')
            subscribtion_label.pack(fill=X, padx=10)
            subscribtion_entry = Entries.UpperLabeledEntry(dynamic_holder, 'قيمة الاشتراك')
            subscribtion_entry.pack(pady=5, fill=X, padx=10)
            subscribtion_entry.entry.bind('<KeyRelease>', lambda e: update_preview())
            dynamic_holder.subscribtion_entry = subscribtion_entry
            dynamic_holder.selected_groups_func = lambda: [g for g, v in zip(group_choices, group_vars) if v.get()]
        else:
            CTkLabel(dynamic_holder, text='اختر المجموعة', font=('Cairo Medium', 16), anchor='e').pack(fill=X, padx=10)
            group_dropdown_var = StringVar(value=group_choices[0] if group_choices else "")
            group_dropdown = CTkOptionMenu(dynamic_holder, values=group_choices, variable=group_dropdown_var, font=('Cairo Medium', 16))
            group_dropdown.pack(pady=5, fill=X, padx=10)
            group_dropdown_var.trace_add('write', update_preview)
            subscribtion_label = CTkLabel(dynamic_holder, text='قيمة الاشتراك بالحصة (جنيه)', font=('Cairo Medium', 16), anchor='e')
            subscribtion_label.pack(fill=X, padx=10)
            subscribtion_entry = Entries.UpperLabeledEntry(dynamic_holder, 'قيمة الاشتراك')
            subscribtion_entry.pack(pady=5, fill=X, padx=10)
            subscribtion_entry.entry.bind('<KeyRelease>', lambda e: update_preview())
            dynamic_holder.subscribtion_entry = subscribtion_entry
            dynamic_holder.selected_groups_func = lambda: [group_dropdown_var.get()] if group_dropdown_var.get() else []
        update_preview()

    typeofpayment.trace_add("write", update_visibility)
    name.entry.bind('<KeyRelease>', lambda e: update_preview())
    cn.entry.bind('<KeyRelease>', lambda e: update_preview())
    fq.entry.bind('<KeyRelease>', lambda e: update_preview())
    fwq.entry.bind('<KeyRelease>', lambda e: update_preview())
    update_visibility()

    add_in_progress = [False]

    def back():
        for x in frame.winfo_children():
            x.destroy()
        Dashboard.Dashboard(frame).pack(fill=BOTH, expand=True)
        
    def validate_phone(phone):
        return phone.isdigit() and (10 <= len(phone) <= 15)

    def add():
        if add_in_progress[0]:
            return
        add_in_progress[0] = True
        try:
            if not name.get_input().strip():
                messagebox.showerror('خطأ', 'يرجى إدخال اسم الطالب')
                return
            if not cn.get_input().strip() or not validate_phone(cn.get_input().strip()):
                messagebox.showerror('خطأ', 'يرجى إدخال رقم تليفون صحيح للطالب')
                return
            if not fq.get_input().strip() or not validate_phone(fq.get_input().strip()):
                messagebox.showerror('خطأ', 'يرجى إدخال رقم تليفون صحيح لولي الأمر')
                return
            ref.execute('SELECT * FROM Students WHERE Name = ? OR OwnPhone = ?', (name.get_input().strip(), cn.get_input().strip()))
            if ref.fetchone():
                messagebox.showerror('خطأ', 'الطالب مسجل بالفعل بنفس الاسم أو رقم الهاتف')
                return
            selected_groups = dynamic_holder.selected_groups_func()
            subscribtion_entry = dynamic_holder.subscribtion_entry
            if typeofpayment.get() == "بالشهر":
                if not selected_groups:
                    messagebox.showerror('خطأ', 'يرجى اختيار مجموعة واحدة على الأقل')
                    return
                if not subscribtion_entry.get_input().strip().isdigit() or int(subscribtion_entry.get_input().strip()) <= 0:
                    messagebox.showerror('خطأ', 'يرجى إدخال قيمة اشتراك صحيحة')
                    return
            else:
                if not selected_groups or not selected_groups[0]:
                    messagebox.showerror('خطأ', 'يرجى اختيار مجموعة')
                    return
                if not subscribtion_entry.get_input().strip().isdigit() or int(subscribtion_entry.get_input().strip()) <= 0:
                    messagebox.showerror('خطأ', 'يرجى إدخال قيمة اشتراك صحيحة')
                    return
            # Find the smallest available ID
            ref.execute('SELECT ID FROM Students')
            existing_ids = sorted([int(row[0]) for row in ref.fetchall() if str(row[0]).isdigit()])
            id = 1
            for eid in existing_ids:
                if eid == id:
                    id += 1
                else:
                    break
            custom_months = [8, 9, 10, 11, 12, 1]
            def get_expire_date(month_index):
                month = custom_months[month_index]
                if payment_mode.get() == "نهاية الشهر":
                    return f"30/{month}"
                else:
                    prev_month = custom_months[month_index-1] if month_index > 0 else custom_months[0]
                    return f"27/{month}, 10/{prev_month}"
            payment_data = [ 
                {"month": str(m), "state": "لم يدفع", "date_payed": "", "expire": get_expire_date(i)}
                for i, m in enumerate(custom_months)
            ] if typeofpayment.get() == "بالشهر" else []
            droos_in = json.dumps([{ "name": g, "price": subscribtion_entry.get_input().strip() } for g in selected_groups])
            ref.execute(
                """
                    INSERT INTO Students VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    id,
                    name.get_input().strip(),
                    cn.get_input().strip(),
                    fq.get_input().strip(),
                    fwq.get_input().strip(),
                    id,
                    '[{}]',
                    '[{}]',
                    'Temp' if typeofpayment.get() == "بالشهر" else selected_groups[0],
                    '0',
                    json.dumps(payment_data) if typeofpayment.get() == "بالشهر" else "BySession",
                    subscribtion_entry.get_input().strip(),
                    droos_in,
                    "{}"
                )
            )
            conn.commit()
            # --- Badge popup logic ---
            response = messagebox.askyesno('الكارت', 'هل الطالب سيستلم الكارت الأن ام نضعه في الانتظار؟')
            if not response:
                from Proccesors.Database.db import add_pending_code
                import datetime
                add_pending_code(id, name.get_input().strip(), datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
            helper = whatsapptool.WhatsAppHelper()
            helper.SendMessage({"type": "SubscribeNum", "std_name": name.get_input().strip()}, fq.get_input().strip())
            if fwq.get_input().strip():
                helper.SendMessage({"type": "SubscribeNum", "std_name": name.get_input().strip()}, fwq.get_input().strip())
            helper.SendMessage({"type": "SubscribeStd", "std_name": name.get_input().strip(), "std_id": id}, fq.get_input().strip())
            messagebox.showinfo('تم بنجاح', f'تم تسجيل الطالب بكود {id}')
            if after_add:
                after_add(id)
            else:
                back()
        finally:
            add_in_progress[0] = False

    AddButton = CTkButton(frame2, command=add, fg_color='#13b272', hover_color='#13b271', text='اضافة الطالب', font=('Cairo Medium', 17), text_color='white')
    AddButton.pack(fill=X, padx=20, pady=(20,10), ipady=2, side=BOTTOM)
    CancelButton = CTkButton(frame2, fg_color='#fc5f7d', command=back, hover_color='#fc5f7d', text='الغاء الأمر', font=('Cairo Medium', 17), text_color='white')
    CancelButton.pack(fill=X, padx=20, pady=(0,20), ipady=2, side=BOTTOM)
