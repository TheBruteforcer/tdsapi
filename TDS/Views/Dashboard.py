from customtkinter import *
import customtkinter
from PIL import Image
from Widgets import Entries
from Proccesors import *
from requests import *
from Proccesors.Database.db import *
from threading import Thread
from Proccesors.Genric.SearchStudent import *
from AlphaControllers.EntryValidators import CheckBlank
from Views import whatsapptool,AddStdForm, Spends, AddSpend, Sessions, SessionsSettings, Exams, Money, Groups, AllStudents, Teachers
from time import localtime
from ServicesApplier.MLPowerdSelection import View
from customtkinter import *
from Proccesors.Database.db import *
from Views import StudentAccount

# Define a consistent color scheme and styling
COLORS = {
    "primary": "#0F67B1",
    "success": "#059212",
    "accent": "#FFD35A",
    "light_bg": "#F0EBE3",
    "white": "white",
    "dark_text": "#333333",
    "button_primary": "#0F67B1",
    "button_success": "#95D2B3",
    "button_danger": "#FF5858"
}

def Search(parent, key):
    root2 = CTk()
    root2.title(f'نتائج البحث عن {key}')
    root2.geometry('570x400')
    tt = CTkScrollableFrame(root2, fg_color=COLORS["white"])
    tt.pack(fill=BOTH, expand=True)
    try:
        int(key)
        ref.execute(f'SELECT * FROM Students WHERE ID = "{key}"')
        students = ref.fetchall()

        for student in students:
            ff = CTkFrame(tt)
            ff.pack(fill=X, padx=10, pady=5)
            CTkLabel(ff, text=student[1], font=('Cairo Medium', 17)).pack(side=RIGHT, padx=(3,7), pady=3)
            CTkLabel(ff, text=f'    كود الطالب : {student[0]}    ', fg_color=COLORS["accent"], font=('Cairo Medium', 17)).pack(side=RIGHT, pady=3, padx=10)
            CTkButton(ff, text='الذهاب الي صفحة الطالب', font=('Cairo Medium', 15), command=lambda sd=student: StudentAccount.ShowAccount(parent, sd)).pack(side=LEFT, padx=5, pady=3)
        if students == []:
            CTkLabel(tt, text='لا نتائج', font=('Cairo Medium', 37)).pack(fill=BOTH, expand=True, padx=(3,7), pady=3)
    
    except:
        ref.execute(f'SELECT * FROM Students WHERE Name LIKE "%{key}%"')
        students = ref.fetchall()
        print(students)
        for student in students:
            ff = CTkFrame(tt)
            ff.pack(fill=X, padx=10, pady=5)
            CTkLabel(ff, text=student[1], font=('Cairo Medium', 17)).pack(side=RIGHT, padx=(3,7), pady=3)
            CTkLabel(ff, text=f'    كود الطالب : {student[0]}    ', fg_color=COLORS["accent"], font=('Cairo Medium', 17)).pack(side=RIGHT, pady=3, padx=10)
            CTkButton(ff, text='الذهاب الي صفحة الطالب', font=('Cairo Medium', 15), command=lambda sd=student: StudentAccount.ShowAccount(parent, sd)).pack(side=LEFT, padx=5, pady=3)
        if students == []:
            CTkLabel(tt, text='لا نتائج', font=('Cairo Medium', 37)).pack(fill=BOTH, expand=True, padx=(3,7), pady=3)
        
    root2.mainloop()

# Create consistent button styles
def create_button(parent, text, command, color="primary", width=120):  # Set a default width
    button_color = COLORS["button_primary"] if color == "primary" else COLORS["button_success"] if color == "success" else COLORS["button_danger"]
    return CTkButton(
        parent, 
        text=text, 
        command=command, 
        font=('Cairo Medium', 17), 
        fg_color=button_color, 
        text_color="white",
        width=width,
        corner_radius=10
    )

# Create consistent card style
def create_card(parent, title, icon_path, icon_size=(90, 90)):
    card = CTkFrame(parent, fg_color=COLORS["white"], corner_radius=25)
    CTkLabel(card, text='', image=CTkImage(Image.open(icon_path), size=icon_size)).pack(pady=(25, 10), padx=100)
    CTkLabel(card, text=title, font=('Cairo Medium', 22, 'bold')).pack(padx=3, pady=(0, 10))
    return card

# Hover button with visual feedback
class HoverButton(CTkButton):
    def __init__(self, *args, **kwargs):
        self.original_color = kwargs.get("fg_color", COLORS["button_primary"])
        # Create a slightly darker version of the color for hover effect
        r, g, b = int(self.original_color[1:3], 16), int(self.original_color[3:5], 16), int(self.original_color[5:7], 16)
        r, g, b = max(0, r-20), max(0, g-20), max(0, b-20)
        self.hover_color = f"#{r:02x}{g:02x}{b:02x}"
        
        super().__init__(*args, **kwargs)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, e):
        self.configure(fg_color=self.hover_color)
    
    def on_leave(self, e):
        self.configure(fg_color=self.original_color)

def show_notification(parent, message, type="info"):
    color = COLORS["success"] if type == "success" else COLORS["button_danger"] if type == "error" else COLORS["primary"]
    notification = CTkFrame(parent, fg_color=color, corner_radius=10)
    notification.place(relx=0.5, rely=0.1, anchor="center")
    
    CTkLabel(notification, text=message, text_color="white", font=('Cairo Medium', 16)).pack(padx=20, pady=10)
    
    # Auto-hide after 3 seconds
    parent.after(3000, notification.destroy)

class Dashboard(CTkFrame):
    def __init__(self, parent: CTkFrame):
        print(ref.connection)
        ref.execute("PRAGMA database_list;")
        self.team = ((ref.fetchone()[2]).split("\\")[-1]).replace(".db", "")
        print(self.team)
        self.today = f'{localtime().tm_mday}/{localtime().tm_mon}/{localtime().tm_year}'
        self.today_db = f'{localtime().tm_mday:02d} \\ {localtime().tm_mon:02d} \\ {localtime().tm_year}'
        self.parent = parent
        
        super().__init__(parent, fg_color=COLORS["light_bg"])
        
        # Setup grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Content

        # Create header with stats
        self.create_header()
        
        # Create main content
        self.create_main_content()
    
    def create_header(self):
        # Create a modern header with stats
        header = CTkFrame(self, fg_color=COLORS["primary"], corner_radius=0, height=120)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 20))
        
        
        # Stats in header
        self.create_stat_card(header, "عدد الطلاب", self.get_student_count(), "TDSAssets/General/student.png", side=LEFT)
        self.create_stat_card(header, "الأرباح", self.get_daily_profit(), "TDSAssets/General/green_bag.png", side=LEFT, text_color=COLORS["success"])
        self.create_stat_card(header, "حصص اليوم", self.get_daily_sessions(), "TDSAssets/General/board.png", side=LEFT)
    
        # Title and date
        title_frame = CTkFrame(header, fg_color="transparent")
        title_frame.pack(side=RIGHT, padx=20, pady=10)
        CTkLabel(title_frame, text=f"{self.team}", font=('Tajawal Medium', 24, 'bold'), text_color="white").pack(anchor="w", pady=(5, 0))
        CTkLabel(title_frame, text=f"التاريخ: {self.today}", font=('Cairo Medium', 14), text_color="white").pack(anchor="w")
    def create_stat_card(self, parent, title, value, icon_path, side=LEFT, text_color=COLORS["primary"]):
        card = CTkFrame(parent, fg_color=("#FFFFFF", "#E5E5E5"), corner_radius=15)

        card.pack(side=side, padx=10, pady=10, fill=Y)
        
        inner_frame = CTkFrame(card, fg_color="transparent")
        inner_frame.pack(padx=15, pady=10, ipadx=10)
        
        CTkLabel(inner_frame, text=str(value), font=('Arial', 22, 'bold'), text_color=text_color).pack(padx=35)
        CTkLabel(inner_frame, text=title, font=('Cairo Medium', 14)).pack(padx=10)
        CTkLabel(card, text='', image=CTkImage(Image.open(icon_path), size=(32, 32))).place(x=10, y=10)
    
    def create_main_content(self):
        content_frame = CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        content_frame.grid_columnconfigure((0, 1, 2), weight=1)
        content_frame.grid_rowconfigure((0, 1), weight=1)
        
        # Row 1
        self.create_student_card(content_frame, 0, 0)
        self.create_expenses_card(content_frame, 0, 1)
        self.create_finances_card(content_frame, 0, 2)
        
        # Row 2
        self.create_sessions_card(content_frame, 1, 0)
        self.create_exams_card(content_frame, 1, 1)
        self.create_groups_card(content_frame, 1, 2)
        
        # Row 3 (if needed)
        content_frame.grid_rowconfigure(2, weight=1)
        self.create_teachers_card(content_frame, 2, 0)
        self.create_tools_card(content_frame, 2, 1, columnspan=2)
    
    def create_student_card(self, parent, row, col, rowspan=1, columnspan=1):
        card = create_card(parent, "الطلاب", "TDSAssets/General/student.png")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew", rowspan=rowspan, columnspan=columnspan)
        
        # Search functionality
        search_frame = CTkFrame(card, fg_color="transparent")
        search_frame.pack(fill=X, expand=True, padx=15, pady=(10, 5))
        
        query = Entries.UpperLabeledEntry(search_frame, 'اسم/رقم الطالب')
        query.pack(fill=X, expand=True)
        
        def search_action():
            if CheckBlank(query.entry):
                Search(self.parent, query.get_input())
        
        search_button = create_button(search_frame, 'بحث', search_action, "success")
        search_button.pack(fill=X, pady=(5, 10))
        
        # Buttons
        button_frame = CTkFrame(card, fg_color="transparent")
        button_frame.pack(fill=X, expand=True, padx=15, pady=10)
        
        create_button(button_frame, 'إضافة طالب جديد', lambda: AddStdForm.apply(self.parent)).pack(fill=X, pady=5)
        create_button(button_frame, 'جـرد الطلاب', lambda: AllStudents.StudentsPage(self.parent), "success").pack(fill=X, pady=5)

    def create_expenses_card(self, parent, row, col, rowspan=1, columnspan=1):
        card = create_card(parent, "المصروفات", "TDSAssets/General/red_bag.png")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew", rowspan=rowspan, columnspan=columnspan)
        
        totalspends = self.get_daily_spends()
        if totalspends > 0:
            CTkLabel(card, text=f'{totalspends:,} جنيه مصري', font=('Cairo Medium', 25)).pack(padx=3, pady=5)
        else:
            CTkLabel(card, text='لا مصروفات حتي الأن', font=('Cairo Medium', 25)).pack(padx=3, pady=5)
        
        CTkLabel(card, text=f'بتاريخ اليوم {self.today}', font=('Cairo Medium', 15)).pack(padx=3)
        
        button_frame = CTkFrame(card, fg_color="transparent")
        button_frame.pack(fill=X, expand=True, padx=15, pady=15, side=BOTTOM)
        
        create_button(button_frame, 'اضافة مصروف جديد', lambda: AddSpend.apply(self.parent)).pack(fill=X, pady=5)
        create_button(button_frame, 'تفاصيل', lambda: Spends.show(self.parent), "success").pack(fill=X, pady=5)

    def create_finances_card(self, parent, row, col, rowspan=1, columnspan=1):
        card = create_card(parent, "الماليات", "TDSAssets/General/green_bag.png")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew", rowspan=rowspan, columnspan=columnspan)
        
        # Daily gains
        gains = self.get_daily_gains()
        gains_text = f'{gains:,} جنيه' if gains > 0 else 'لا إيرادات حتى الآن'
        
        CTkLabel(card, text="إيرادات اليوم", font=('Cairo Medium', 18)).pack(padx=3, pady=(15, 5))
        CTkLabel(card, text=gains_text, font=('Cairo Medium', 22), text_color=COLORS["success"]).pack(padx=3, pady=5)
        
        button_frame = CTkFrame(card, fg_color="transparent")
        button_frame.pack(fill=X, expand=True, padx=15, pady=15, side=BOTTOM)
        
        create_button(button_frame, 'الذهاب إلى الماليات', lambda: Money.show(self.parent), "primary").pack(fill=X, pady=5)

    def create_sessions_card(self, parent, row, col, rowspan=1, columnspan=1):
        card = create_card(parent, "الحصص", "TDSAssets/General/board.png")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew", rowspan=rowspan, columnspan=columnspan)
        
        sessions_count = self.get_daily_sessions()
        CTkLabel(card, text=f'{sessions_count} حصة اليوم', font=('Cairo Medium', 20)).pack(padx=3, pady=10)
        
        button_frame = CTkFrame(card, fg_color="transparent")
        button_frame.pack(fill=X, expand=True, padx=15, pady=15, side=BOTTOM)
        
        create_button(button_frame, 'صفحة الحصص', lambda: SessionsSettings.go(self.parent), "primary").pack(fill=X, pady=5)

    def create_exams_card(self, parent, row, col, rowspan=1, columnspan=1):
        card = create_card(parent, "الامتحانات", "TDSAssets/General/sh.png")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew", rowspan=rowspan, columnspan=columnspan)
        

        button_frame = CTkFrame(card, fg_color="transparent")
        button_frame.pack(fill=X, expand=True, padx=15, pady=15, side=BOTTOM)
        
        create_button(button_frame, 'الذهاب إلى الامتحانات', lambda: Exams.go(self.parent), "primary").pack(fill=X, pady=5)

    def create_groups_card(self, parent, row, col, rowspan=1, columnspan=1):
        card = create_card(parent, "المجموعات", "TDSAssets/Banking/bank_ico.png")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew", rowspan=rowspan, columnspan=columnspan)
        
        # Get groups count
        ref.execute('SELECT COUNT(*) FROM Groups')
        groups_count = ref.fetchone()[0] or 0
        
        CTkLabel(card, text=f'{groups_count} مجموعة', font=('Cairo Medium', 20)).pack(padx=3, pady=10)
        
        button_frame = CTkFrame(card, fg_color="transparent")
        button_frame.pack(fill=X, expand=True, padx=15, pady=15, side=BOTTOM)
        
        create_button(button_frame, 'إدارة المجموعات', lambda: Groups.show(self.parent), "primary").pack(fill=X, pady=5)

    def create_teachers_card(self, parent, row, col, rowspan=1, columnspan=1):
        card = create_card(parent, "شؤون المعلمين", "TDSAssets/General/folder.png")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew", rowspan=rowspan, columnspan=columnspan)
        
        # Get teachers count
        ref.execute('SELECT COUNT(*) FROM Teachers')
        teachers_count = ref.fetchone()[0] or 0
        
        CTkLabel(card, text=f'{teachers_count} معلم', font=('Cairo Medium', 20)).pack(padx=3, pady=10)
        
        button_frame = CTkFrame(card, fg_color="transparent")
        button_frame.pack(fill=X, expand=True, padx=15, pady=15, side=BOTTOM)
        
        create_button(button_frame, 'إدارة المعلمين', lambda: Teachers.Teachers(self.parent), "primary").pack(fill=X, pady=5)

    def create_tools_card(self, parent, row, col, rowspan=1, columnspan=1):
        card = create_card(parent, "الأدوات والإعدادات", "TDSAssets/General/tag.png")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew", rowspan=rowspan, columnspan=columnspan)
        
        button_frame = CTkFrame(card, fg_color="transparent")
        button_frame.pack(fill=X, expand=True, padx=15, pady=15, side=BOTTOM)
        
        create_button(button_frame, 'اصدار مستلزمات لكل الطلاب', lambda: View.Apply(self.parent), "primary").pack(fill=X, pady=5)
        create_button(button_frame, 'اداة الواتساب - جديد ومميز !', lambda: whatsapptool.WhatsAppHelper().UIPage(self.parent), "primary").pack(fill=X, pady=5)

    def show_settings(self):
        # Placeholder for settings page
        show_notification(self, "صفحة الإعدادات قيد التطوير", "info")
    
    # Helper methods to get data
    def get_student_count(self):
        ref.execute('SELECT COUNT(*) FROM Students')
        return ref.fetchone()[0] or 0
    
    def get_daily_profit(self):
        ref.execute("SELECT SUM(CAST(Qnt AS INTEGER)) FROM Gains WHERE Date LIKE ?", (self.today_db + '%',))
        gains = ref.fetchone()[0] or 0
        ref.execute("SELECT SUM(CAST(Qnt AS INTEGER)) FROM Spends WHERE Date LIKE ?", (self.today_db + '%',))
        spends = ref.fetchone()[0] or 0
        return gains - spends
    
    def get_daily_gains(self):
        ref.execute("SELECT SUM(CAST(Qnt AS INTEGER)) FROM Gains WHERE Date LIKE ?", (self.today_db + '%',))
        return ref.fetchone()[0] or 0
    
    def get_daily_spends(self):
        ref.execute("SELECT SUM(CAST(Qnt AS INTEGER)) FROM Spends WHERE Date LIKE ?", (self.today_db + '%',))
        return ref.fetchone()[0] or 0
    
    def get_daily_sessions(self):
        ref.execute('SELECT COUNT(*) FROM Sessions WHERE Date = ?', (self.today_db,))
        return ref.fetchone()[0] or 0