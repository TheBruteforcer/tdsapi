import os
from customtkinter import *
from json import loads
from sqlite3 import connect
from PIL import Image
from Views.Admin_ import Students, Money, States, Groups
import json
import hashlib
import logging
from datetime import datetime
from Views.Admin_.MainAdmin import MainAdmin
from tkinter import messagebox


class SuperUser:
    def __init__(self):
        pass

    def UI(self, parent: CTkScrollableFrame):
        # تنظيف الواجهة قبل إعادة إنشاء العناصر
        for widget in parent.winfo_children():
            widget.destroy()

        # الحصول على جميع قواعد البيانات في المجلد الحالي
        dblist = [db for db in os.listdir(".") if db.endswith(".db") and "journal" not in db]

        # تعريف المتغيرات التجميعية
        total_gains = total_spends = total_students = total_gains_moves = 0
        total_groups = total_teachers = total_lecs = total_sessions = 0

        # معالجة كل قاعدة بيانات
        for db_name in dblist:
            with connect(db_name) as conn:
                ref = conn.cursor()

                ref.execute("SELECT * FROM Gains")
                gains = ref.fetchall()
                total_gains_moves += len(gains)
                total_gains += sum(int(g[2]) for g in gains)

                ref.execute("SELECT * FROM Spends")
                spends = ref.fetchall()
                total_spends += sum(int(s[0]) for s in spends)

                ref.execute("SELECT * FROM Students")
                total_students += len(ref.fetchall())

                ref.execute("SELECT * FROM Groups")
                total_groups += len(ref.fetchall())

                ref.execute("SELECT * FROM Teachers")
                total_teachers += len(ref.fetchall())

                ref.execute("SELECT * FROM InvSessions")
                total_lecs += len(ref.fetchall())

                ref.execute("SELECT * FROM Sessions")
                total_sessions += len(ref.fetchall())

        # تحميل الصور مرة واحدة فقط لتوفير الموارد
        icons = {
            "students": CTkImage(Image.open("TDSAssets/General/folder.png"), size=(70, 70)),
            "stats": CTkImage(Image.open("TDSAssets/General/stats.png"), size=(70, 70)),
            "groups": CTkImage(Image.open("TDSAssets/General/calender.png"), size=(70, 70)),
        }

        def animate_padding(frame, target, step):
            """ تحسين الرسوم المتحركة لعدم تعليق الـ UI """
            if not frame.winfo_ismapped():
                return
            try:
                current_padx = frame.pack_info().get("pady", 10)
                if current_padx != target:
                    new_padx = current_padx + step if current_padx < target else current_padx - step
                    frame.pack_configure(pady=new_padx)
                    frame.after(10, lambda: animate_padding(frame, target, step))  # إعادة الاستدعاء تدريجياً
            except Exception as e:
                print("Error:", e)

        def create_stats_frame(icon, state_name, state_desc, func):
            frame = CTkFrame(parent, fg_color="white")
            
            def onhover(event):
                animate_padding(frame, 21, 1)

            def onleave(event):
                animate_padding(frame, 10, 1)

            frame.pack(fill=X, padx=10, pady=(10, 10))
            frame.bind("<Enter>", onhover)
            frame.bind("<Leave>", onleave)

            CTkLabel(frame, text="", image=icon).pack(padx=20, pady=20, side=RIGHT)

            listor1 = CTkFrame(frame, fg_color="transparent")
            listor1.pack(padx=(10, 20), side=RIGHT)

            CTkLabel(listor1, text="   " + state_name + "   ", font=("Tajawal Medium", 24), anchor="e").pack(padx=2, pady=(20, 2), fill=X)
            CTkLabel(listor1, text="   " + state_desc + "   ", font=("Tajawal Medium", 18), anchor="e").pack(padx=2, pady=(6, 20), fill=X)
            CTkButton(frame, text="   مزيد من التفاصيل    ", command=func, font=("Tajawal Medium", 18)).pack(fill=Y, padx=20, side=LEFT, pady=13)

        CTkLabel(parent, text="صفحة المدير", font=("Cairo Medium", 80), anchor="e").pack(fill=X, padx=10, pady=(12, 0))
        CTkLabel(parent, text="أهلًا بيك تاني أ/يحيى", font=("Cairo Medium", 30), anchor="e").pack(fill=X, padx=10, pady=(0, 10))

        # خط متحرك تحت العنوان
        linecon = CTkFrame(parent, fg_color="transparent")
        line = CTkFrame(linecon, fg_color="grey", height=4, width=5, corner_radius=170)
        line.pack(pady=4, side=RIGHT, padx=10)
        linecon.pack(fill=X)

        def linearanimator():
            """ تحسين تحريك الخط بدون تجميد الواجهة """
            if line.winfo_width() < 400:
                line.configure(width=line.winfo_width() + 30)
                parent.after(10, linearanimator)

        parent.after(500, linearanimator)

        # إنشاء الـ stats frames
        create_stats_frame(icons["students"], "ملفات الطلاب", f"عدد الطلاب : {total_students}", lambda: Students.StudentSView(parent))
        create_stats_frame(icons["stats"], "المصروفات المفصلة", f"الأرباح الإجمالية : {total_gains}\nعدد حركات الدفعات : {total_gains_moves}", lambda: Money.Money(parent))
        create_stats_frame(icons["groups"], "النظام والخدمات الجانبية", "التحقق من سير النظام والخدمات الجانبية للبرنامج", lambda: States.show(parent))
        create_stats_frame(icons["groups"], "المجموعات", "", lambda: Groups.Groups(parent))

class LoginPage:
    def __init__(self, root):
        self.root = root
        
        self.attempts = 0
        self.max_attempts = 5
        self.lockout_duration = 300
        self.show_password = False
        
        # Create security directory if it doesn't exist
        os.makedirs('security', exist_ok=True)
        
        # Enhanced logging configuration
        logging.basicConfig(
            filename='security/login_attempts.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        self.security_config = self.load_security_config()
        self.setup_ui()

    def load_security_config(self):
        """Load or create security configuration"""
        config_file = "security_config.json"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Default configuration with hashed password
            default_password = "admin123"  # Change this to your desired default password
            config = {
                "password_hash": self.hash_password(default_password),
                "lockout_until": None
            }
            with open(config_file, 'w') as f:
                json.dump(config, f)
            return config

    def hash_password(self, password):
        """Create secure hash of password"""
        return hashlib.sha256(password.encode()).hexdigest()

    def setup_ui(self):
        # Create main container that centers everything
        main_container = CTkFrame(self.root, fg_color="transparent")
        main_container.pack(expand=True, fill="both")
        
        # Create login frame with padding
        login_frame = CTkFrame(
            main_container,
            width=400,
            height=500,
            corner_radius=15,
            fg_color="#ffffff"
        )
        login_frame.pack(expand=True, padx=20, pady=20)
        # Force the frame to keep its size
        login_frame.pack_propagate(False)
        
        # Title with new font
        title = CTkLabel(
            login_frame,
            text="تسجيل الدخول",
            font=("Tajawal Medium", 32),
            text_color="#2B6BE6"
        )
        title.pack(pady=(90, 30))

        # Password container
        password_container = CTkFrame(login_frame, fg_color="transparent")
        password_container.pack(pady=(0, 20))

        self.password_var = StringVar()
        self.password_entry = CTkEntry(
            password_container,
            width=250,
            height=45,  # Increased height
            placeholder_text="كلمة المرور",
            show="•",
            font=("Tajawal Medium", 16),
            textvariable=self.password_var
        )
        self.password_entry.pack(side=LEFT, padx=(0, 5))

        # Larger eye icon button
        self.toggle_btn = CTkButton(
            password_container,
            text="👁",
            width=45,  # Match height
            height=45,  # Match password entry height
            command=self.toggle_password_visibility,
            fg_color="transparent",
            hover_color="#E0E0E0",
            font=("Tajawal Medium", 20)  # Bigger font for eye icon
        )
        self.toggle_btn.pack(side=LEFT)

        # Loading label
        self.loading_label = CTkLabel(
            login_frame,
            text="جاري التحقق...",
            font=("Tajawal Medium", 14),
            text_color="#2B6BE6"
        )
        self.loading_label.pack(pady=(0, 10))
        self.loading_label.pack_forget()

        # Error label
        self.error_label = CTkLabel(
            login_frame,
            text="",
            font=("Tajawal Medium", 14),
            text_color="#FF5252"
        )
        self.error_label.pack(pady=(0, 10))

        # Login button
        self.login_button = CTkButton(
            login_frame,
            text="دخول",
            font=("Tajawal Medium", 18),
            width=200,
            height=45,
            corner_radius=12,
            command=self.validate_login
        )
        self.login_button.pack(pady=(20, 0))

        # Center all elements in the frame
        for widget in login_frame.winfo_children():
            widget.pack_configure(anchor="center")

        # Focus on password entry
        self.password_entry.focus()

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        self.show_password = not self.show_password
        self.password_entry.configure(show="" if self.show_password else "•")
        self.toggle_btn.configure(text="👁️" if self.show_password else "👁")

    def validate_login(self):
        """Enhanced login validation"""
        # Show loading state
        self.loading_label.pack(pady=(0, 10))
        self.login_button.configure(state="disabled")
        self.password_entry.configure(state="disabled")
        
        # Simulate network delay (remove in production)
        self.root.after(800, self._perform_validation)

    def _perform_validation(self):
        """Actual validation logic"""
        # Check for lockout
        if self.security_config.get("lockout_until"):
            lockout_time = datetime.fromisoformat(self.security_config["lockout_until"])
            if datetime.now() < lockout_time:
                remaining = (lockout_time - datetime.now()).seconds
                self.show_error(f"الحساب مقفل. حاول مرة أخرى بعد {remaining//60} دقيقة و {remaining%60} ثانية")
                self._reset_loading_state()
                return

        entered_password = self.password_var.get()
        if not entered_password:
            self.show_error("يرجى إدخال كلمة المرور")
            self._reset_loading_state()
            return

        if self.hash_password(entered_password) == self.security_config["password_hash"]:
            self.loading_label.configure(text="تم تسجيل الدخول بنجاح!")
            self.root.after(500, self.login_success)
        else:
            self.handle_failed_attempt()
            self._reset_loading_state()

    def _reset_loading_state(self):
        """Reset UI elements after validation"""
        self.loading_label.pack_forget()
        self.login_button.configure(state="normal")
        self.password_entry.configure(state="normal")
        self.password_entry.focus()

    def handle_failed_attempt(self):
        """Handle failed login attempt"""
        self.attempts += 1
        remaining_attempts = self.max_attempts - self.attempts
        
        if remaining_attempts > 0:
            self.show_error(f"كلمة المرور غير صحيحة. {remaining_attempts} محاولات متبقية")
        else:
            # Implement lockout
            lockout_time = datetime.now().isoformat()
            self.security_config["lockout_until"] = lockout_time
            with open("security_config.json", 'w') as f:
                json.dump(self.security_config, f)
            
            self.show_error("تم قفل الحساب لمدة 5 دقائق")
            self.attempts = 0

        # Log failed attempt
        logging.warning(f"Failed login attempt. IP: {self.get_client_ip()}")

    def login_success(self):
        """Handle successful login"""
        # Reset attempts
        self.attempts = 0
        self.security_config["lockout_until"] = None
        with open("security_config.json", 'w') as f:
            json.dump(self.security_config, f)

        # Log successful login
        logging.info(f"Successful login. IP: {self.get_client_ip()}")

        # Load grade selection view
        self.show_grade_selection()

    def show_grade_selection(self):
        """Shows grade selection view"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        try:
            conn = connect("Application.db")
            ref = conn.cursor()
            ref.execute('SELECT * FROM PGroups')
            groups = ref.fetchall()

            # Create main container
            main_frame = CTkFrame(self.root, fg_color="transparent")
            main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

            # Header
            header_frame = CTkFrame(main_frame, fg_color="white", corner_radius=15)
            header_frame.pack(fill=X, pady=(0, 20))

            grade_icon = CTkImage(Image.open('TDSAssets/General/calender.png'), size=(70, 70))
            CTkLabel(header_frame, text='', image=grade_icon).pack(side=RIGHT, padx=10, pady=10)

            CTkLabel(
                header_frame,
                text="اختر الصف الدراسي",
                font=('Cairo Medium', 27)
            ).pack(side=RIGHT, padx=10, pady=(15,10))

            # Create buttons for each grade
            for group in groups:
                def open_admin(db_name=f"{group[1]}.db"):
                    MainAdmin(self.root, db_name)

                grade_button = CTkButton(
                    main_frame,
                    text=group[1],
                    font=("Cairo Medium", 20),
                    command=lambda g=group[1]: MainAdmin(self.root, f"{g}.db"),
                    height=60,
                    corner_radius=15,
                    hover_color="#2B6BE6"
                )
                grade_button.pack(fill=X, pady=5)

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحميل الصفوف: {str(e)}")
        finally:
            if conn:
                conn.close()

    def show_error(self, message):
        """Enhanced error display"""
        self.error_label.configure(text=message)
        self.password_entry.configure(border_color="#FF5252")
        
        # Shake animation for failed attempt
        original_x = self.password_entry.winfo_x()
        for i in range(10):
            offset = 10 if i % 2 == 0 else -10
            self.root.after(i * 50, lambda x=offset: self.password_entry.place(x=original_x + x))
        
        self.root.after(500, lambda: self.password_entry.configure(border_color="#2B6BE6"))

    def get_client_ip(self):
        """Get client IP for logging"""
        try:
            import socket
            return socket.gethostbyname(socket.gethostname())
        except:
            return "Unknown"

def initialize_login(root):
    """Initialize login page"""
    return LoginPage(root)
