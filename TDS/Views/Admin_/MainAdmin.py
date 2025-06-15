from customtkinter import *
from PIL import Image
from tkinter import messagebox
from sqlite3 import *
from json import *
import datetime
from CTkTable.ctktable import CTkTable
from CTkXYFrame.ctk_xyframe import CTkXYFrame
import threading
from concurrent.futures import ThreadPoolExecutor
from Views.StudentAccount import CUSTOM_MONTHS, CUSTOM_MONTH_NAMES, get_custom_month_name
from time import localtime
import json
class MainAdminView:
    def __init__(self, parent, db_name):
        self.parent = parent
        self.db_name = db_name  # Store database name
        self.executor = ThreadPoolExecutor(max_workers=4)  # Thread pool for async operations
        self.tables_icon = CTkImage(Image.open('TDSAssets/General/note.png'), size=(25, 25))  # Cache image
        # Initialize database connection
        from Proccesors.Database.db import create_db_connection, change_distnation
        change_distnation(self.db_name)
        self.db = create_db_connection()
        self.setup_ui()

    def __del__(self):
        """Cleanup database connection when object is destroyed"""
        if hasattr(self, 'db'):
            self.db.close()

    def setup_ui(self):
        # Clear existing widgets
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Create grade selection frame
        self.create_grade_selection()

    def create_grade_selection(self):
        """Creates grade selection buttons"""
        self.executor.submit(self._async_create_grade_selection)

    def _async_create_grade_selection(self):
        try:
            conn = connect("Application.db")
            ref = conn.cursor()
            
            ref.execute('SELECT * FROM PGroups')
            groups = ref.fetchall()
            
            # Schedule UI updates on main thread
            self.parent.after(0, self._create_ui_elements, groups)
            
        except Exception as e:
            self.parent.after(0, messagebox.showerror, "خطأ", f"حدث خطأ أثناء تحميل الصفوف: {str(e)}")
        finally:
            if conn:
                conn.close()

    def _create_ui_elements(self, groups):
        """Create UI elements on main thread"""
        selection_frame = CTkFrame(self.parent, fg_color="transparent")
        selection_frame.pack(fill=BOTH, expand=True, padx=15, pady=10)
        
        # Create title frame
        self._create_title_frame(selection_frame)
        
        # Create stats container
        self._create_stats_container(selection_frame)
        
        # Create teachers frame
        self._create_teachers_frame()
        
        # Create tables
        self._create_tables(selection_frame)
        
        # Create financial table
        self.create_financial_table(selection_frame)

    def _create_title_frame(self, parent):
        """Create title frame with back button"""
        title_frame = CTkFrame(parent, fg_color="white", corner_radius=20)
        title_frame.pack(fill=X, pady=10)
        
        # Back button - Updated version
        CTkButton(
            title_frame,
            text="رجوع",
            font=("Cairo Medium", 14),
            fg_color="#2B6BE6",  # Blue background
            hover_color="#1E4A8E",  # Darker blue on hover
            text_color="white",  # White text
            corner_radius=8,  # Rounded corners
            height=35,  # Fixed height
            width=100,  # Fixed width
            command=self._go_back_to_grade_selection
        )
        # Positioned on the left

        # Grade icon
        grade_icon = CTkImage(Image.open('TDSAssets/General/calender.png'), size=(70, 70))
        CTkLabel(title_frame, text='', image=grade_icon).pack(side=RIGHT, padx=10, pady=10)
        
        # Title
        CTkLabel(
            title_frame,
            text=" صفحة المدير العام ",
            font=('Cairo Medium', 27)
        ).pack(side=RIGHT, padx=10, pady=(15,10))

    def _go_back_to_grade_selection(self):
        """Returns to the grade selection page"""
        try:
            # Destroy current window after a short delay
            self.parent.after(100, self._destroy_and_initialize)
        except Exception as e:
            print(f"Error during back navigation: {e}")

    def _destroy_and_initialize(self):
        """Safely destroys current window and initializes login"""
        try:
            from Views.Admin import initialize_login
            self.parent.destroy()  # Destroy current window
            initialize_login(self.parent.master)  # Create new grade selection window
        except Exception as e:
            print(f"Error during window transition: {e}")

    def _create_stats_container(self, parent):
        """Create stats container"""
        stats_container = CTkFrame(
            parent, 
            fg_color="transparent", 
            corner_radius=20
        )
        stats_container.pack(fill=X, padx=15, pady=10)

        # Load stats async
        self.executor.submit(self._load_stats_async, stats_container)

    def _load_stats_async(self, parent):
        """Load stats in background"""
        paid_count, unpaid_count = self.get_total_payment_counts()
        self.parent.after(0, self._create_stats_frames, parent, paid_count, unpaid_count)

    def _create_stats_frames(self, parent, paid_count, unpaid_count):
        """Create stats frames on main thread"""
        self.create_stats_frame(parent, "unpaid", unpaid_count)
        self.create_stats_frame(parent, "paid", paid_count)

    def _create_tables(self, parent):
        """Create tables with proper layout"""
        # Create a container for tables and tools
        tables_container = CTkFrame(parent, fg_color="transparent")
        tables_container.pack(fill=BOTH, expand=True, padx=15, pady=10)
        
        # Students table - Takes 40% of space
        students_frame = CTkFrame(tables_container, fg_color="transparent")
        students_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        self._create_students_table(students_frame)
        
        # Attendance table - Takes 40% of space
        attendance_frame = CTkFrame(tables_container, fg_color="transparent")
        attendance_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        self._create_sessions_table(attendance_frame)
        
        # Tools frame - Takes 20% of space
        tools_frame = CTkFrame(tables_container, fg_color="transparent")
        tools_frame.pack(fill=BOTH, expand=True)
        self.create_tools_frame(tools_frame)

    def _create_students_table(self, parent):
        """Create students table"""
        students_frame = CTkFrame(parent, fg_color="white", corner_radius=20)
        students_frame.pack(fill=X, padx=15, pady=10)
        
        # Load data async
        self.executor.submit(self._load_students_data_async, students_frame)

    def _load_students_data_async(self, parent):
        """Load students data in background"""
        students_data = self.get_students_data()
        self.parent.after(0, self._create_students_table_ui, parent, students_data)

    def _create_students_table_ui(self, parent, students_data):
        """Create students table UI on main thread"""
        # Students Table Section
        students_frame = CTkFrame(parent, fg_color="white", corner_radius=20)
        students_frame.pack(fill=X, padx=15, pady=10)
        
        # Students Title
        title_frame = CTkFrame(students_frame, fg_color="transparent")
        title_frame.pack(fill=X, padx=20, pady=10)

        CTkLabel(
            title_frame,
            text="   قائمة الطلاب   ",
            font=("Cairo Medium", 18, "bold"),
            image=self.tables_icon,
            compound="right"
        ).pack(side=RIGHT)

        # Container frame with grey background for students table
        students_frame_tc = CTkFrame(students_frame, fg_color="grey", corner_radius=20)
        students_frame_tc.pack(fill=BOTH, expand=True, padx=15, pady=10)

        # --- BEGIN DYNAMIC MONTH HEADERS ---
        month_headers = [get_custom_month_name(m) for m in CUSTOM_MONTHS]
        headers = [["الكود", "الاسم"] + month_headers + ["سعر الاشتراك", "نوع الدفع", "حذف"]]
        reversed_headers = [headers[0][::-1]]  # Reverse the inner list for RTL
        students_data = reversed_headers + students_data
        # --- END DYNAMIC MONTH HEADERS ---
        
        # Create table with only delete column clickable
        self.students_table = CTkTable(
            students_frame_tc,
            values=students_data,
            colors=["#f8f9fa", "#edf2f7"],
            hover_color="#e2e8f0",
            font=("Cairo Medium", 14),
            padx=1,
            pady=1,
            command=None  # Remove global command
        )
        
        # Add click handler and style only to delete column
        for row in range(1, len(students_data)):  # Skip header row
            # Configure delete cell
            delete_cell = self.students_table.frame[row, 0]
            delete_cell.configure(
                command=lambda r=row: self.delete_student({"row": r, "column": 0}),
                fg_color="#ffebee",  # Light red background
                text_color="#c62828",  # Dark red text
                hover_color="#ffcdd2",  # Lighter red on hover
                hover=True,  # Ensure hover effect is enabled
                corner_radius=0  # Remove corner radius
            )
            # Force the hover color to stay consistent
            delete_cell.bind("<Enter>", lambda e, cell=delete_cell: cell.configure(fg_color="#ffcdd2"))
            delete_cell.bind("<Leave>", lambda e, cell=delete_cell: cell.configure(fg_color="#ffebee"))
        
        self.students_table.pack(expand=True, fill="both", padx=5, pady=5)

    def _create_sessions_table(self, parent):
        """Create sessions table with fixed height"""
        sessions_container = CTkFrame(
            parent, 
            fg_color="white", 
            corner_radius=20,
            height=400  # Fixed height
        )
        sessions_container.pack(fill=BOTH, expand=True, padx=15, pady=10)
        sessions_container.pack_propagate(False)  # Prevent height from changing

        # Load data async
        self.executor.submit(self._load_sessions_data_async, sessions_container)

    def _load_sessions_data_async(self, parent):
        """Load sessions data in background"""
        sessions = self.get_all_sessions()
        attendance_data = self.get_attendance_data(sessions)
        self.parent.after(0, self._create_sessions_table_ui, parent, sessions, attendance_data)

    def _create_sessions_table_ui(self, parent, sessions, attendance_data):
        """Create sessions table UI on main thread"""
        # Sessions Table Section - Using CTkXYFrame with matching styling
        sessions_container = CTkFrame(
            parent, 
            fg_color="white", 
            corner_radius=20,
            height=600  # Fixed height
        )
        sessions_container.pack(fill=BOTH, expand=True, padx=15, pady=10)
        sessions_container.pack_propagate(False)  # Prevent height from changing

        # Title frame similar to students table
        sessions_title_frame = CTkFrame(sessions_container, fg_color="transparent")
        sessions_title_frame.pack(fill=X, padx=20, pady=10)

        sessions_icon = CTkImage(Image.open('TDSAssets/General/note.png'), size=(25, 25))
        CTkLabel(
            sessions_title_frame,
            text="   قائمة الحضور   ",
            font=("Cairo Medium", 18, "bold"),
            image=sessions_icon,
            compound="right"
        ).pack(side=RIGHT)

        # Container frame with grey background similar to students table
        sessions_frame_tc = CTkFrame(
            sessions_container, 
            fg_color="grey", 
            corner_radius=20
        )
        sessions_frame_tc.pack(fill=BOTH, expand=True, padx=15, pady=10)
        
        # Create XY scrollable frame inside the container
        xy_frame = CTkXYFrame(
            sessions_frame_tc,
            scrollbar_button_color="#2B6BE6",
            scrollbar_button_hover_color="#1E4A8E",
            corner_radius=20,
            fg_color="grey"
        )
        xy_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)

        # Create headers
        headers = ["الكود", "الاسم"] + [session[1] for session in sessions]
        
        # Create table with matching styling
        self.sessions_table = CTkTable(
            xy_frame,
            values=[headers[::-1]] + [row[::-1] for row in attendance_data],
            colors=["#f8f9fa", "#edf2f7"],
            hover_color="#e2e8f0",
            font=("Cairo Medium", 14),
            padx=1,
            pady=1
        )
        self.sessions_table.pack(expand=True, fill="both", padx=5, pady=5)

    def create_stats_frame(self, parent, status_type, count):
        """Creates a statistics frame for either paid or unpaid students"""
        stats_frame = CTkFrame(
            parent, 
            fg_color="white", 
            corner_radius=20
        )
        stats_frame.pack(fill=BOTH, expand=True, padx=20, pady=20, side=RIGHT)

        # Title section
        title_frame = CTkFrame(stats_frame, fg_color="white", corner_radius=20)
        title_frame.pack(fill=X, padx=20, pady=20)

        # Status indicator
        indicator_color = "#4CAF50" if status_type == "paid" else "#F44336"
        status_indicator = CTkFrame(
            title_frame,
            width=30, 
            height=30, 
            fg_color=indicator_color, 
            corner_radius=180
        )
        status_indicator.pack(side=RIGHT, padx=10)

        # Title text
        title_text = "عدد الطلاب اللي دفعوا" if status_type == "paid" else "عدد الطلاب اللي مدفعوش"
        CTkLabel(
            title_frame, 
            text=title_text, 
            font=("Cairo Medium", 24)
        ).pack(side=RIGHT, padx=20, pady=10)

        # Count with special styling
        count_frame = CTkFrame(
            title_frame, 
            fg_color="#e8f5e9" if status_type == "paid" else "#ffebee",
            corner_radius=15
        )
        count_frame.pack(side=LEFT, padx=20, pady=5)
        
        CTkLabel(
            count_frame,
            text=str(count),
            font=("Cairo Medium", 24, "bold"),
            text_color="#2E7D32" if status_type == "paid" else "#C62828"
        ).pack(padx=15, pady=5)

    def get_total_payment_counts(self):
        """Accurately gets total paid/unpaid counts for current grade for the current month."""
        try:
            from Proccesors.Database.db import create_db_connection, change_distnation
            change_distnation(self.db_name)
            conn = create_db_connection()
            ref = conn.cursor()
            
            total_paid = 0
            total_unpaid = 0
            
            # Get all students who pay monthly
            ref.execute("SELECT ID, Name, PayHistory FROM Students WHERE PayHistory != 'BySession'")
            students = ref.fetchall()
            
            # Current month as int (no leading zero)
            current_month = int(datetime.datetime.now().month)
            
            for student in students:
                try:
                    payment_data = loads(student[2])  # PayHistory
                    if isinstance(payment_data, list):
                        found_month = False
                        for payment in payment_data:
                            # Extract month as int
                            month_str = str(payment.get("month", "")).replace("شهر", "").strip()
                            if month_str.isdigit() and int(month_str) == current_month:
                                found_month = True
                                if payment.get("state") == "تم":
                                    total_paid += 1
                                else:
                                    total_unpaid += 1
                                break
                        if not found_month:
                            # No payment record for this month = unpaid
                            total_unpaid += 1
                    else:
                        # If PayHistory is not a list, treat as unpaid
                        total_unpaid += 1
                except Exception as e:
                    print(f"Error processing student {student[0]}: {e}")
                    total_unpaid += 1
            
            return total_paid, total_unpaid
            
        except Exception as e:
            print(f"Error getting payment counts: {e}")
            return 0, 0
        finally:
            if conn:
                conn.close()

    def get_students_data(self):
        """Retrieves student data with payment and attendance info"""
        try:
            from Proccesors.Database.db import create_db_connection, change_distnation
            change_distnation(self.db_name)
            conn = create_db_connection()
            ref = conn.cursor()
            
            # Get student data with payment history
            ref.execute("SELECT ID, Name, PayHistory, Attendance, SubscribtionAmount, OPercentage FROM Students")
            students = ref.fetchall()
            
            table_data = []
            
            for student in students:
                # --- BEGIN DYNAMIC MONTH STATUS ---
                month_statuses = []
                payment_type = ""
                if student[2] == "BySession":
                    month_statuses = ["--------------"] * len(CUSTOM_MONTHS)
                    payment_type = "بيدفع بالحصة"
                else:
                    try:
                        payment_data = loads(student[2])  # PayHistory
                        if isinstance(payment_data, list):
                            for m in CUSTOM_MONTHS:
                                found = False
                                for payment in payment_data:
                                    month_num = str(payment.get("month", "")).replace("شهر", "").strip()
                                    payment_date = payment.get("date_payed", "")
                                    expire = payment.get("expire", "")
                                    if not payment_type and expire:
                                        payment_type = "دفع مقدم" if "27" in str(expire) else "دفع مؤخر"
                                    if month_num == str(m):
                                        if payment.get("state") == "تم":
                                            month_statuses.append(f"✅\n({payment_date})" if payment_date else "✅")
                                        else:
                                            month_statuses.append("❌")
                                        found = True
                                        break
                                if not found:
                                    month_statuses.append("❌")
                    except Exception as e:
                        print(e)
                        month_statuses = ["❌"] * len(CUSTOM_MONTHS)
                subscription_price = f"{student[4]} جنيه"
                row_data = [
                    student[0],  # ID
                    student[1],  # Name
                    *month_statuses,
                    subscription_price,
                    payment_type,
                    "حذف"
                ]
                table_data.append(row_data[::-1])  # Reverse for RTL
                # --- END DYNAMIC MONTH STATUS ---
            return table_data
        except Exception as e:
            print(f"Error getting students data: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_all_sessions(self):
        """Gets all sessions from the database"""
        try:
            from Proccesors.Database.db import create_db_connection, change_distnation
            change_distnation(self.db_name)
            conn = create_db_connection()
            ref = conn.cursor()
            
            ref.execute("SELECT ID, Title FROM Sessions ORDER BY Date ASC")
            return ref.fetchall()
        except Exception as e:
            print(f"Error getting sessions: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_attendance_data(self, sessions):
        """Gets attendance data for all students"""
        try:
            from Proccesors.Database.db import create_db_connection, change_distnation
            change_distnation(self.db_name)
            conn = create_db_connection()
            ref = conn.cursor()
            
            # Get all students
            ref.execute("SELECT ID, Name, Attendance FROM Students")
            students = ref.fetchall()
            
            attendance_data = []
            
            for student in students:
                student_row = [student[0], student[1]]  # ID and Name
                
                # Load attendance data with error handling
                attendance = []
                if student[2]:
                    try:
                        attendance = loads(student[2])
                        if not isinstance(attendance, list):
                            attendance = []
                    except:
                        attendance = []
                
                # Check attendance for each session
                for session in sessions:
                    session_name = session[1]  # Use session name instead of ID
                    attended = False
                    
                    # Check if session is in attendance records
                    for record in attendance:
                        if isinstance(record, dict) and record.get(session_name) == 'Attended.':
                            attended = True
                            break
                    
                    student_row.append("✅" if attended else "❌")
                
                attendance_data.append(student_row)
            
            return attendance_data
        except Exception as e:
            print(f"Error getting attendance data: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def create_tools_frame(self, parent):
        """Creates a tools frame with proper layout"""
        tools_frame = CTkFrame(
            parent,
            fg_color="white",
            corner_radius=20
        )
        tools_frame.pack(fill=BOTH, expand=True, padx=15, pady=10)

        # WhatsApp notification tool
        whatsapp_frame = CTkFrame(tools_frame, fg_color="#e8f5e9", corner_radius=15)
        whatsapp_frame.pack(fill=X, padx=20, pady=10)

        whatsapp_icon = CTkImage(Image.open('TDSAssets/General/whatsapp.png'), size=(30, 30))
        CTkLabel(
            whatsapp_frame,
            text="",
            image=whatsapp_icon
        ).pack(side=RIGHT, padx=15, pady=10)

        # Tool description
        desc_frame = CTkFrame(whatsapp_frame, fg_color="transparent")
        desc_frame.pack(side=RIGHT, fill=X, expand=True, padx=10)

        CTkLabel(
            desc_frame,
            text="ارسال رسائل واتساب للطلاب المتأخرين عن السداد",
            font=("Cairo Medium", 16),
            anchor="e"
        ).pack(fill=X)

        CTkLabel(
            desc_frame,
            text="إرسال تنبيهات آلية لأولياء الأمور عن طريق الواتساب",
            font=("Cairo Medium", 12),
            text_color="gray",
            anchor = "e"
        ).pack(fill=X)

        # Send button
        CTkButton(
            whatsapp_frame,
            text="إرسال التنبيهات",
            font=("Cairo Medium", 14),
            command=self.send_payment_reminders,
            hover_color="#2B6BE6",
            height=35,
            corner_radius=8
        ).pack(side=LEFT, padx=15, pady=10)

    def create_financial_table(self, parent):
        """Creates a beautiful financial records table with modern UI"""
        table_frame = CTkFrame(
            parent,
            fg_color="#F7F9FB",  # Soft background
            corner_radius=20
        )
        table_frame.pack(fill=BOTH, expand=True, padx=24, pady=18)

        # Title section with icon
        title_frame = CTkFrame(table_frame, fg_color="white", corner_radius=15)
        title_frame.pack(fill=X, padx=24, pady=(18, 8))
        
        money_icon = CTkImage(Image.open('TDSAssets/General/green_money.png'), size=(32, 32))
        CTkLabel(
            title_frame,
            text="  السجل المالي  ",
            font=("Cairo Medium", 26, "bold"),
            image=money_icon,
            compound="right",
            fg_color="white"
        ).pack(side=RIGHT, padx=12, pady=10)

        # Summary cards
        summary_frame = CTkFrame(table_frame, fg_color="white", corner_radius=15)
        summary_frame.pack(fill=X, padx=24, pady=(0, 12))

        # Today's summary
        today_frame = CTkFrame(summary_frame, fg_color="#E3F2FD", corner_radius=15)
        today_frame.pack(side=RIGHT, expand=True, fill=X, padx=8, pady=10)
        CTkLabel(
            today_frame,
            text="إجمالي اليوم",
            font=("Cairo Medium", 18, "bold"),
            text_color="#1976D2",
            fg_color="#E3F2FD"
        ).pack(pady=(10, 2))
        today_amount = self.calculate_today_total()
        CTkLabel(
            today_frame,
            text=f"{today_amount:,} جنيه",
            font=("Cairo Medium", 22, "bold"),
            text_color="#1976D2",
            fg_color="#E3F2FD"
        ).pack(pady=(0, 10))

        # Month's summary
        month_frame = CTkFrame(summary_frame, fg_color="#E8F5E9", corner_radius=15)
        month_frame.pack(side=RIGHT, expand=True, fill=X, padx=8, pady=10)
        CTkLabel(
            month_frame,
            text="إجمالي الشهر",
            font=("Cairo Medium", 18, "bold"),
            text_color="#388E3C",
            fg_color="#E8F5E9"
        ).pack(pady=(10, 2))
        month_amount = self.calculate_month_total()
        CTkLabel(
            month_frame,
            text=f"{month_amount:,} جنيه",
            font=("Cairo Medium", 22, "bold"),
            text_color="#388E3C",
            fg_color="#E8F5E9"
        ).pack(pady=(0, 10))

        # Search section
        search_frame = CTkFrame(table_frame, fg_color="#F5F5F5", corner_radius=15)
        search_frame.pack(fill=X, padx=24, pady=10)

        # Date inputs with labels
        inputs_frame = CTkFrame(search_frame, fg_color="transparent")
        inputs_frame.pack(pady=10)

        # Day input
        day_frame = CTkFrame(inputs_frame, fg_color="transparent")
        day_frame.pack(side=RIGHT, padx=10)
        CTkLabel(day_frame, text="اليوم", font=("Cairo Medium", 14)).pack()
        self.day_entry = CTkEntry(
            day_frame,
            width=70,
            font=("Cairo Medium", 14),
            corner_radius=10
        )
        self.day_entry.pack()

        # Month input
        month_frame = CTkFrame(inputs_frame, fg_color="transparent")
        month_frame.pack(side=RIGHT, padx=10)
        CTkLabel(month_frame, text="الشهر", font=("Cairo Medium", 14)).pack()
        self.month_entry = CTkEntry(
            month_frame,
            width=70,
            font=("Cairo Medium", 14),
            corner_radius=10
        )
        self.month_entry.pack()

        # Year input
        year_frame = CTkFrame(inputs_frame, fg_color="transparent")
        year_frame.pack(side=RIGHT, padx=10)
        CTkLabel(year_frame, text="السنة", font=("Cairo Medium", 14)).pack()
        self.year_entry = CTkEntry(
            year_frame,
            width=70,
            font=("Cairo Medium", 14),
            corner_radius=10
        )
        self.year_entry.pack()

        # Search button
        CTkButton(
            search_frame,
            text="بحث",
            font=("Cairo Medium", 14, "bold"),
            command=self.search_records,
            width=100,
            corner_radius=10,
            hover_color="#2B6BE6"
        ).pack(pady=10)

        # Records container
        self.table_content = CTkScrollableFrame(
            table_frame,
            fg_color="#F7F9FB",
            height=420
        )
        self.table_content.pack(fill=BOTH, expand=True, padx=24, pady=10)

        # Initial load of records
        self.load_financial_records()

    def calculate_today_total(self):
        """Calculate total gains for today"""
        try:
            conn = connect(self.db_name)
            ref = conn.cursor()
            today = f'{localtime().tm_mday} \\ {localtime().tm_mon} \\ {localtime().tm_year}'
            ref.execute("SELECT SUM(CAST(Qnt AS INTEGER)) FROM Gains WHERE substr(Date, 1, instr(Date, ' - ') - 1) = ?", (today,))
            total = ref.fetchone()[0] or 0
            return total
        except Exception as e:
            print(f"Error calculating today's total: {e}")
            return 0
        finally:
            if conn:
                conn.close()

    def calculate_month_total(self):
        """Calculate total gains for current month"""
        try:
            conn = connect(self.db_name)
            ref = conn.cursor()
            current_month = localtime().tm_mon
            # Get all gains for debugging
            ref.execute('SELECT Date, Qnt FROM Gains')
            gains = ref.fetchall()
            print(f"Found {len(gains)} total gains records")
            total = 0
            for row in gains:
                try:
                    date_str = row[0].split(' - ')[0]  # Only date part
                    amount_str = row[1]
                    date_parts = [part.strip() for part in date_str.split('\\')]
                    print(f"Processing date: {date_str}, parts: {date_parts}, amount: {amount_str}")
                    if len(date_parts) >= 2:
                        month = int(date_parts[1])
                        if month == current_month:
                            amount = int(amount_str)
                            total += amount
                            print(f"Added amount {amount} to total (now {total})")
                except Exception as e:
                    print(f"Error processing row {row}: {str(e)}")
                    continue
            print(f"Final total for month {current_month}: {total}")
            return total
        except Exception as e:
            print(f"Error calculating month's total: {e}")
            return 0
        finally:
            if conn:
                conn.close()

    def calculate_monthly_revenue(self):
        """Calculates total monthly revenue including both monthly and per-session payments"""
        try:
            conn = connect(self.db_name)
            ref = conn.cursor()
            current_month = str(datetime.datetime.now().month).replace("0", "")
            total = 0
            # Get monthly payments
            ref.execute("SELECT * FROM Students")
            for student in ref.fetchall():
                if student[10] != "BySession":
                    payment_data = loads(student[10])
                    for month in payment_data:
                        if current_month == str(month["month"]).replace("شهر", "").strip():
                            if month["state"] == "تم":
                                try:
                                    total += int(month.get("amount", 0))
                                except:
                                    continue
                            break
            # Get session payments
            ref.execute("SELECT Date, Qnt, ID FROM Gains")
            for gain in ref.fetchall():
                date_str = gain[0].split(' - ')[0]
                date_parts = [part.strip() for part in date_str.split('\\')]
                if len(date_parts) >= 2:
                    month = date_parts[1]
                    if str(month) == current_month and not str(gain[2]).endswith('C'):
                        try:
                            total += int(gain[1])
                        except:
                            continue
            return f"{total:,} جنيه"
        finally:
            if conn:
                conn.close()

    def analyze_payment_trends(self):
        """Analyzes payment trends and patterns"""
        try:
            conn = connect(self.db_name)
            ref = conn.cursor()
            current_month = str(datetime.datetime.now().month).replace("0", "")
            last_month = str(12 if current_month == "1" else int(current_month) - 1)
            trends = []
            # Calculate this month's and last month's revenue
            this_month_revenue = int(self.calculate_monthly_revenue().replace(",", "").replace(" جنيه", ""))
            # Calculate last month's revenue
            last_month_revenue = 0
            ref.execute("SELECT * FROM Students")
            for student in ref.fetchall():
                if student[10] != "BySession":
                    payment_data = loads(student[10])
                    for month in payment_data:
                        if last_month == str(month["month"]).replace("شهر", "").strip():
                            if month["state"] == "تم":
                                try:
                                    last_month_revenue += int(month.get("amount", 0))
                                except:
                                    continue
            # Get session payments for last month
            ref.execute("SELECT Date, Qnt, ID FROM Gains")
            for gain in ref.fetchall():
                date_str = gain[0].split(' - ')[0]
                date_parts = [part.strip() for part in date_str.split('\\')]
                if len(date_parts) >= 2:
                    month = date_parts[1]
                    if str(month) == last_month and not str(gain[2]).endswith('C'):
                        try:
                            last_month_revenue += int(gain[1])
                        except:
                            continue
            # Revenue Trend
            revenue_change = ((this_month_revenue - last_month_revenue) / last_month_revenue * 100) if last_month_revenue > 0 else 0
            trends.append({
                "title": "مقارنة بالشهر السابق",
                "value": f"{'↗️' if revenue_change >= 0 else '↘️'} {abs(int(revenue_change))}%",
                "color": "green" if revenue_change >= 0 else "red"
            })
            # ... rest of the function unchanged ...
        finally:
            if conn:
                conn.close()

    def debug_gains_data(self):
        """Debug method to check Gains table data"""
        try:
            conn = connect(self.db_name)
            ref = conn.cursor()
            
            # Get table info
            ref.execute("PRAGMA table_info(Gains)")
            columns = ref.fetchall()
            print("\nGains table structure:")
            for col in columns:
                print(f"Column: {col}")
            
            # Get sample data
            ref.execute("SELECT * FROM Gains LIMIT 5")
            rows = ref.fetchall()
            print("\nSample Gains data:")
            for row in rows:
                print(f"Row: {row}")
            
            # Get distinct dates
            ref.execute("SELECT DISTINCT Date FROM Gains")
            dates = ref.fetchall()
            print("\nDistinct dates in Gains:")
            for date in dates:
                print(f"Date: {date[0]}")
            
        except Exception as e:
            print(f"Error in debug_gains_data: {e}")
        finally:
            if conn:
                conn.close()

    def search_records(self):
        """Search and display financial records based on date"""
        try:
            day = self.day_entry.get().strip() or None
            month = self.month_entry.get().strip() or None
            year = self.year_entry.get().strip() or None
            
            # Clear current records
            for widget in self.table_content.winfo_children():
                widget.destroy()

            # Load records with date filter
            self.load_financial_records(day, month, year)

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء البحث: {str(e)}")

    def load_financial_records(self, day=None, month=None, year=None):
        """Load and display financial records for the current grade with improved UI"""
        try:
            # Clear current records
            for widget in self.table_content.winfo_children():
                widget.destroy()

            conn = connect(f"{self.db_name}")  # Connect to current grade's database
            ref = conn.cursor()
            total_gains = 0

            # Build date filter
            if day and month and year:
                date_filter = f"{day} \\ {month} \\ {year}"
                ref.execute("SELECT * FROM Gains WHERE substr(Date, 1, instr(Date, ' - ') - 1) = ?", (date_filter,))
            else:
                ref.execute("SELECT * FROM Gains")
            gain_records = ref.fetchall()

            # Group gains by session ID
            from collections import defaultdict
            session_gains = defaultdict(list)
            for gain in gain_records:
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
                        payment_frame = CTkFrame(self.table_content, fg_color='#E8F5E9', corner_radius=12)
                        payment_frame.pack(fill=X, padx=18, pady=8, ipadx=8, ipady=8)
                        CTkLabel(payment_frame, text='', image=CTkImage(Image.open('TDSAssets/General/green_money.png'), size=(28, 28))).pack(side=RIGHT, padx=8)
                        CTkLabel(payment_frame, text=f'دفع شهر للطالب {student_name}', font=("Cairo Medium", 16, "bold"), text_color="#388E3C").pack(side=RIGHT, padx=12)
                        CTkLabel(payment_frame, text=f'{amount:,} جنيه', font=("Cairo Medium", 15), text_color="#1976D2").pack(side=RIGHT, padx=12)
                        CTkLabel(payment_frame, text=f'الوقت : {date}', font=("Cairo Medium", 14), text_color="#616161").pack(side=RIGHT, padx=12)
                        total_gains += amount
                else:
                    # Session or custom gains: use big frame
                    ref.execute(f'SELECT Title FROM Sessions WHERE ID = ?', (session_id,))
                    session_title = ref.fetchone()
                    session_title = session_title[0] if session_title else (gains[0][1] if gains[0][1] else f'جلسة رقم ({session_id})')
                    session_frame = CTkFrame(self.table_content, fg_color='#F0F4C3', corner_radius=16)
                    session_frame.pack(fill=X, padx=10, pady=(18, 8), ipadx=8, ipady=8)
                    title_bar = CTkFrame(session_frame, fg_color='#FFFDE7', corner_radius=10)
                    title_bar.pack(fill=X, padx=0, pady=(0, 8))
                    CTkLabel(title_bar, text=session_title, font=("Cairo Medium", 20, "bold"), text_color="#795548").pack(side=RIGHT, padx=18, pady=8)
                    for gain in gains:
                        amount = int(float(gain[2]))
                        date = gain[3]
                        payment_frame = CTkFrame(session_frame, fg_color='#FFFFFF', corner_radius=10)
                        payment_frame.pack(fill=X, padx=12, pady=6, ipadx=6, ipady=6)
                        session_id_inner = str(gain[0])
                        if gain[1] and not gain[1].startswith('{'):
                            CTkLabel(payment_frame, text='', image=CTkImage(Image.open('TDSAssets/General/note.png'), size=(24, 24))).pack(side=RIGHT, padx=6)
                            CTkLabel(payment_frame, text=gain[1], font=("Cairo Medium", 16, "bold"), text_color="#1976D2").pack(side=RIGHT, padx=10)
                        else:
                            ref.execute(f'SELECT Title FROM Sessions WHERE ID = ?', (session_id_inner,))
                            session_title_inner = ref.fetchone()
                            session_title_inner = session_title_inner[0] if session_title_inner else f'جلسة رقم ({session_id_inner})'
                            CTkLabel(payment_frame, text='', image=CTkImage(Image.open('TDSAssets/General/board2.png'), size=(24, 24))).pack(side=RIGHT, padx=6)
                            CTkLabel(payment_frame, text=session_title_inner, font=("Cairo Medium", 16, "bold"), text_color="#388E3C").pack(side=RIGHT, padx=10)
                        CTkLabel(payment_frame, text=f'{amount:,} جنيه', font=("Cairo Medium", 15), text_color="#1976D2").pack(side=RIGHT, padx=10)
                        CTkLabel(payment_frame, text=f'الوقت : {date}', font=("Cairo Medium", 14), text_color="#616161").pack(side=RIGHT, padx=10)
                        total_gains += amount
            # Add total at the bottom
            total_frame = CTkFrame(
                self.table_content,
                fg_color="#E3F2FD",
                corner_radius=15,
                height=54
            )
            total_frame.pack(fill=X, pady=(16, 6), padx=10)
            total_frame.pack_propagate(False)
            CTkLabel(
                total_frame,
                text=f"المجموع الكلي: {total_gains:,} جنيه",
                font=("Cairo Medium", 20, "bold"),
                text_color="#2B6BE6"
            ).pack(pady=12)
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحميل السجلات: {str(e)}")
        finally:
            if conn:
                conn.close()

    def create_grade_card(self, parent, group):
        """Creates a card for each grade with statistics"""
        card = CTkFrame(parent, fg_color="white", corner_radius=15, height=100)
        card.pack_propagate(False)
        
        # Grade info section
        info_frame = CTkFrame(card, fg_color="transparent")
        info_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=15)
        
        CTkLabel(
            info_frame,
            text=group[1],  # Grade name
            font=("Cairo Medium", 20, "bold")
        ).pack(side=RIGHT, pady=5)
        
        # Get statistics
        stats = self.get_grade_stats(f"{group[1]}.db")
        
        # Stats section
        stats_frame = CTkFrame(info_frame, fg_color="transparent")
        stats_frame.pack(fill=X)
        
        # Students count
        CTkLabel(
            stats_frame,
            text=f"عدد الطلاب: {stats['total_students']}",
            font=("Cairo Medium", 14),
            text_color="gray"
        ).pack(side=RIGHT, padx=10)
        
        # Monthly revenue
        CTkLabel(
            stats_frame,
            text=f"الإيرادات الشهرية: {stats['monthly_revenue']} جنيه",
            font=("Cairo Medium", 14),
            text_color="gray"
        ).pack(side=RIGHT, padx=10)
        
        # View button
        CTkButton(
            card,
            text="عرض التفاصيل",
            font=("Cairo Medium", 16),
            command=lambda: self.view_grade_details(group[1]),
            hover_color="#2B6BE6",
            height=40,
            width=120
        ).pack(side=LEFT, padx=15)
        
        return card

    def get_grade_stats(self, db_name):
        """Gets basic statistics for a grade"""
        try:
            conn = connect(db_name)
            ref = conn.cursor()
            
            # Get total students
            ref.execute("SELECT COUNT(*) FROM Students")
            total_students = ref.fetchone()[0]
            
            # Calculate monthly revenue
            current_month = str(datetime.datetime.now().month).replace("0", "")
            monthly_revenue = 0
            
            ref.execute("SELECT * FROM Students")
            for student in ref.fetchall():
                if student[10] != "BySession":
                    payment_data = loads(student[10])
                    for month in payment_data:
                        if current_month == str(month["month"]).replace("شهر", "").strip():
                            if month["state"] == "تم":
                                try:
                                    monthly_revenue += int(month.get("amount", 0))
                                except:
                                    continue
            
            return {
                "total_students": total_students,
                "monthly_revenue": f"{monthly_revenue:,}"
            }
            
        except Exception as e:
            print(f"Error getting grade stats: {e}")
            return {
                "total_students": 0,
                "monthly_revenue": "0"
            }
        finally:
            if conn:
                conn.close()

    def view_grade_details(self, grade_name):
        """Opens the detailed view for a grade"""
        from Views.Admin_.Money import MoneyView
        MoneyView(self.parent, f"{grade_name}.db")

    def delete_student(self, cell):
        """Handles student deletion with improved error handling and UI feedback"""
        try:
            row = cell["row"]
            col = cell["column"]
            
            if row == 0 or col != 0:
                return
                
            # Dynamically find the correct column indexes
            header = self.students_table.values[0]
            id_col_index = header.index("الكود")
            name_col_index = header.index("الاسم")
            student_id = self.students_table.values[row][id_col_index]
            student_name = self.students_table.values[row][name_col_index]
            
            # Create a confirmation dialog
            confirm_dialog = CTkToplevel()
            confirm_dialog.title("تأكيد الحذف")
            confirm_dialog.geometry("400x300")  # Increased height
            confirm_dialog.attributes('-topmost', True)
            
            # Center the dialog
            confirm_dialog.update_idletasks()
            x = (confirm_dialog.winfo_screenwidth() - confirm_dialog.winfo_width()) // 2
            y = (confirm_dialog.winfo_screenheight() - confirm_dialog.winfo_height()) // 2
            confirm_dialog.geometry(f"+{x}+{y}")
            
            # Add warning icon
            warning_icon = CTkImage(Image.open('TDSAssets/General/error.png'), size=(50, 50))
            CTkLabel(confirm_dialog, image=warning_icon, text="").pack(pady=(20,10))
            
            # Add warning message
            CTkLabel(
                confirm_dialog,
                text=f"هل أنت متأكد من حذف الطالب\n{student_name}\nكود: {student_id}؟",
                font=("Cairo Medium", 16)
            ).pack(pady=10)
            
            def confirm_delete():
                try:
                    from Proccesors.Database.db import create_db_connection, change_distnation
                    change_distnation(self.db_name)
                    conn = create_db_connection()
                    ref = conn.cursor()
                    
                    # Delete student
                    ref.execute("DELETE FROM Students WHERE ID = ?", (student_id,))
                    conn.commit()
                    conn.close()
            
                    # Refresh the table UI
                    self.setup_ui()
                    
                    # Show success message
                    messagebox.showinfo("تم", f"تم حذف الطالب {student_name} بنجاح")
                    confirm_dialog.destroy()
            
                except Exception as e:
                    messagebox.showerror("خطأ", f"حدث خطأ أثناء حذف الطالب: {str(e)}")
                    confirm_dialog.destroy()
            
            # Add buttons
            buttons_frame = CTkFrame(confirm_dialog, fg_color="transparent")
            buttons_frame.pack(pady=20)
            
            CTkButton(
                buttons_frame,
                text="تأكيد الحذف",
                font=("Cairo Medium", 14),
                fg_color="#FF5252",
                hover_color="#FF1744",
                command=confirm_delete
            ).pack(side=LEFT, padx=10)
            
            CTkButton(
                buttons_frame,
                text="إلغاء",
                font=("Cairo Medium", 14),
                command=confirm_dialog.destroy
            ).pack(side=LEFT, padx=10)
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")

    def send_payment_reminders(self):
        """Sends WhatsApp reminders to students with late payments"""
        try:
            conn = connect(self.db_name)
            ref = conn.cursor()
            
            ref.execute("SELECT * FROM Students")
            students = ref.fetchall()
            
            current_month = str(datetime.datetime.now().month)
            current_month = current_month.replace("0", "")
            
            late_students = []
            
            for student in students:
                if student[10] != "BySession":  # Only check monthly payment students
                    payment_data = loads(student[10])
                    
                    for month in payment_data:
                        if current_month == str(month["month"]).replace("شهر", "").strip():
                            if month["state"] != "تم":
                                late_students.append({
                                    "name": student[1],
                                    "phone": student[3],  # Student phone
                                    "parent_phone": student[4],  # Parent phone
                                    "expire": month.get("expire", "غير محدد")
                                })
                            break
            
            if not late_students:
                messagebox.showinfo("تنبيه", "لا يوجد طلاب متأخرين عن السداد")
                return
            print(late_students)
            # Initialize WhatsApp helper
            from Views import whatsapptool
            whatsapp = whatsapptool.WhatsAppHelper()
            
            # Send messages
            sent_count = 0
            for student in late_students:
                try:
                    # Send to parent's phone
                    whatsapp.SendMessage({
                        "type": "Custom",
                        "std_name": student["name"],
                        "message": f"""
تذكير هام ⚠️

نود تذكير حضرتك بموعد سداد المصروفات الشهرية للطالب {student["name"]}
موعد السداد: {student["expire"]}

برجاء سرعة السداد لضمان استمرار الخدمة
مع خالص الشكر والتقدير 🌹
"""
                    }, student["parent_phone"])
                    
                    sent_count += 1
                except Exception as e:
                    print(f"Error sending to {student['name']}: {str(e)}")
                    continue

            messagebox.showinfo("تم", f"تم إرسال {sent_count} رسالة تذكير بنجاح")

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء إرسال الرسائل: {str(e)}")
        finally:
            if conn:
                conn.close()

    def _create_teachers_frame(self):
        """Create teachers statistics frame"""
        try:
            # Create main container frame
            self.teachers_container = CTkFrame(self.parent)
            self.teachers_container.pack(fill=X, padx=15, pady=10)
            
            # Title frame
            title_frame = CTkFrame(self.teachers_container, fg_color="white", corner_radius=15)
            title_frame.pack(fill=X, padx=5, pady=5)
            
            # Add icon and title
            teacher_icon = CTkImage(Image.open('TDSAssets/General/calender.png'), size=(32, 32))
            CTkLabel(
                title_frame,
                text="  احصائيات المدرسين  ",
                font=("Cairo Medium", 24, "bold"),
                image=teacher_icon,
                compound="right"
            ).pack(side=RIGHT, padx=15, pady=10)
            
            # Create grid frame for teacher cards
            self.teachers_grid = CTkFrame(self.teachers_container, fg_color="transparent")
            self.teachers_grid.pack(fill=X, padx=5, pady=5)
            
            # Configure grid columns (3 columns with equal weight)
            for i in range(3):
                self.teachers_grid.grid_columnconfigure(i, weight=1)
            
            # Get teachers data
            cursor = self.db.cursor()
            cursor.execute("SELECT * FROM Teachers")
            teachers_data = cursor.fetchall()
            
            # Create cards for each teacher
            current_row = 0
            current_col = 0
            
            for teacher in teachers_data:
                # Create teacher card
                card = self._create_teacher_card(teacher)
                card.grid(row=current_row, column=current_col, padx=10, pady=10, sticky="nsew")
                
                # Update grid position
                current_col += 1
                if current_col >= 3:
                    current_col = 0
                    current_row += 1
            
        except Exception as e:
            print(f"Error creating teachers frame: {e}")
            # Create a label to show the error
            CTkLabel(
                self.teachers_container,
                text=f"حدث خطأ في تحميل بيانات المدرسين: {str(e)}",
                font=("Cairo Medium", 14),
                text_color="red"
            ).pack(pady=10)

    def _create_teacher_card(self, teacher):
        # Create main card frame with white background and rounded corners
        card = CTkFrame(self.teachers_grid, fg_color="white", corner_radius=15)
        
        # Header section with teacher info
        header_frame = CTkFrame(card, fg_color="#E3F2FD", corner_radius=10)
        header_frame.pack(fill=X, padx=10, pady=10)
        
        # Teacher icon and name
        teacher_icon = CTkImage(Image.open('TDSAssets/General/calender.png'), size=(32, 32))
        CTkLabel(
            header_frame,
            text="",
            image=teacher_icon
        ).pack(side=RIGHT, padx=10, pady=5)
        
        CTkLabel(
            header_frame,
            text=f"{teacher[1]}",  # Teacher name
            font=("Cairo Medium", 20, "bold"),
            text_color="#1976D2"
        ).pack(side=RIGHT, padx=5, pady=5)
        
        # Groups section
        try:
            groups = json.loads(teacher[2] if teacher[2] else '[]')
            groups_text = " | ".join(groups) if groups else "لا يوجد مجموعات"
        except:
            groups_text = "لا يوجد مجموعات"
            
        groups_frame = CTkFrame(card, fg_color="#F5F5F5", corner_radius=10)
        groups_frame.pack(fill=X, padx=10, pady=5)
        
        CTkLabel(
            groups_frame,
            text="المجموعات:",
            font=("Cairo Medium", 16, "bold"),
            text_color="#424242"
        ).pack(side=RIGHT, padx=10, pady=5)
        
        CTkLabel(
            groups_frame,
            text=groups_text,
            font=("Cairo Medium", 14),
            text_color="#616161"
        ).pack(side=RIGHT, padx=5, pady=5)
        
        # Stats section
        stats_frame = CTkFrame(card, fg_color="transparent")
        stats_frame.pack(fill=X, padx=10, pady=5)
        
        # Calculate statistics
        sessions_count = self._get_teacher_sessions_count(teacher)
        students_count = self._get_teacher_students_count(teacher)
        session_paying, monthly_paying, paid_monthly = self._get_teacher_payment_stats(teacher)
        real_students = session_paying + paid_monthly
        real_income = self._calculate_real_income(teacher)
        
        # Create stats cards
        stats = [
            {"label": "عدد الحصص (هذا الشهر)", "value": sessions_count, "color": "#E8F5E9", "text_color": "#2E7D32"},
            {"label": "عدد الطلاب في المجموعات", "value": students_count, "color": "#E3F2FD", "text_color": "#1976D2"},
            {"label": "طلاب الحصص", "value": session_paying, "color": "#FFF3E0", "text_color": "#E65100"},
            {"label": "طلاب الشهر", "value": monthly_paying, "color": "#F3E5F5", "text_color": "#7B1FA2"},
            {"label": "الطلاب الدافعين للشهر", "value": paid_monthly, "color": "#E8F5E9", "text_color": "#2E7D32"},
            {"label": "الطلاب الفعليين", "value": real_students, "color": "#E1F5FE", "text_color": "#0288D1"},
            {"label": "الدخل الفعلي", "value": f"{real_income} ج.م", "color": "#FFEBEE", "text_color": "#C62828"}
        ]
        
        for stat in stats:
            stat_card = CTkFrame(stats_frame, fg_color=stat["color"], corner_radius=8)
            stat_card.pack(fill=X, pady=2, padx=5)
            
            CTkLabel(
                stat_card,
                text=stat["label"],
                font=("Cairo Medium", 14),
                text_color="#424242"
            ).pack(side=RIGHT, padx=10, pady=3)
            
            CTkLabel(
                stat_card,
                text=str(stat["value"]),
                font=("Cairo Medium", 14, "bold"),
                text_color=stat["text_color"]
            ).pack(side=LEFT, padx=10, pady=3)
        
        # Sessions details section
        sessions_frame = CTkFrame(card, fg_color="#FAFAFA", corner_radius=10)
        sessions_frame.pack(fill=X, padx=10, pady=5)
        
        CTkLabel(
            sessions_frame,
            text="تفاصيل الحصص:",
            font=("Cairo Medium", 16, "bold"),
            text_color="#424242"
        ).pack(padx=10, pady=5)
        
        # Create scrollable frame for sessions
        sessions_scroll = CTkScrollableFrame(sessions_frame, height=150)
        sessions_scroll.pack(fill=X, padx=5, pady=5)
        
        # Add session details
        sessions = self._get_teacher_sessions(teacher)
        if sessions:
            for session in sessions:
                session_card = CTkFrame(sessions_scroll, fg_color="white", corner_radius=5)
                session_card.pack(fill=X, pady=2, padx=5)
                
                CTkLabel(
                    session_card,
                    text=session['name'],
                    font=("Cairo Medium", 14),
                    text_color="#424242"
                ).pack(side=RIGHT, padx=10, pady=3)
                
                CTkLabel(
                    session_card,
                    text=f"{session['attendance']} حضور",
                    font=("Cairo Medium", 14),
                    text_color="#1976D2"
                ).pack(side=LEFT, padx=10, pady=3)
        else:
            CTkLabel(
                sessions_scroll,
                text="لا توجد حصص هذا الشهر",
                font=("Cairo Medium", 14),
                text_color="#757575"
            ).pack(pady=10)
        
        return card

    def _get_teacher_sessions_count(self, teacher):
        cursor = self.db.cursor()
        current_month = datetime.datetime.now().strftime("%m")
        try:
            groups = json.loads(teacher[2] if teacher[2] else '[]')
        except:
            groups = []
        count = 0
        
        for group in groups:
            query = """
                SELECT COUNT(*) FROM Sessions 
                WHERE StartTime LIKE ? 
                AND strftime('%m', Date) = ?
            """
            result = cursor.execute(query, (f"%{group}%", current_month)).fetchone()
            count += result[0] if result else 0
            
        return count

    def _get_teacher_students_count(self, teacher):
        cursor = self.db.cursor()
        try:
            groups = json.loads(teacher[2] if teacher[2] else '[]')
        except:
            groups = []
        total_students = 0
        
        for group in groups:
            query = """
                SELECT COUNT(DISTINCT ID) FROM Students 
                WHERE (Badges LIKE ? OR DroosIn LIKE ?)
            """
            result = cursor.execute(query, (f"%{group}%", f"%{group}%")).fetchone()
            total_students += result[0] if result else 0
            
        return total_students

    def _get_teacher_payment_stats(self, teacher):
        cursor = self.db.cursor()
        try:
            groups = json.loads(teacher[2] if teacher[2] else '[]')
        except:
            groups = []
        current_month = datetime.datetime.now().strftime("%m")
        session_paying = 0
        monthly_paying = 0
        paid_monthly = 0
        
        for group in groups:
            query = """
                SELECT ID, PayHistory FROM Students 
                WHERE (Badges LIKE ? OR DroosIn LIKE ?)
            """
            students = cursor.execute(query, (f"%{group}%", f"%{group}%")).fetchall()
            
            for student in students:
                if student[1] == 'BySession':
                    session_paying += 1
                else:
                    monthly_paying += 1
                    try:
                        pay_history = json.loads(student[1])
                        if str(current_month).zfill(2) in pay_history.get('Months', []):
                            paid_monthly += 1
                    except:
                        continue
        
        return session_paying, monthly_paying, paid_monthly

    def _calculate_real_income(self, teacher):
        cursor = self.db.cursor()
        try:
            groups = json.loads(teacher[2] if teacher[2] else '[]')
        except:
            groups = []
        current_month = datetime.datetime.now().strftime("%m")
        total_income = 0
        
        for group in groups:
            session_price = self._get_group_session_price(group)
            
            session_students = cursor.execute("""
                SELECT COUNT(*) FROM Students 
                WHERE (Badges LIKE ? OR DroosIn LIKE ?)
                AND PayHistory = 'BySession'
            """, (f"%{group}%", f"%{group}%")).fetchone()[0]
            
            sessions_count = cursor.execute("""
                SELECT COUNT(*) FROM Sessions 
                WHERE StartTime LIKE ? 
                AND strftime('%m', Date) = ?
            """, (f"%{group}%", current_month)).fetchone()[0]
            
            total_income += session_students * session_price * sessions_count
            
            monthly_students = cursor.execute("""
                SELECT PayHistory FROM Students 
                WHERE (Badges LIKE ? OR DroosIn LIKE ?)
                AND PayHistory != 'BySession'
            """, (f"%{group}%", f"%{group}%")).fetchall()
            
            for student in monthly_students:
                try:
                    pay_history = json.loads(student[0])
                    if str(current_month).zfill(2) in pay_history.get('Months', []):
                        total_income += pay_history.get('Price', 0)
                except:
                    continue
        
        return total_income

    def _get_group_session_price(self, group):
        # Implement your logic to get session price for a group
        # This is a placeholder
        return 50  # Default price

    def _get_teacher_sessions(self, teacher):
        cursor = self.db.cursor()
        try:
            groups = json.loads(teacher[2] if teacher[2] else '[]')
        except:
            groups = []
        current_month = datetime.datetime.now().strftime("%m")
        sessions = []
        
        for group in groups:
            query = """
                SELECT Title, Date FROM Sessions 
                WHERE StartTime LIKE ? 
                AND strftime('%m', Date) = ?
            """
            group_sessions = cursor.execute(query, (f"%{group}%", current_month)).fetchall()
            
            for session in group_sessions:
                attendance = self._get_session_attendance(session[0])  # Title is at index 0
                sessions.append({
                    'name': session[0],  # Title is at index 0
                    'attendance': attendance
                })
        
        return sessions

    def _get_session_attendance(self, session_name):
        cursor = self.db.cursor()
        query = """
            SELECT COUNT(*) FROM Students 
            WHERE json_extract(Attendance, '$.' || ?) = 1
        """
        result = cursor.execute(query, (session_name,)).fetchone()
        return result[0] if result else 0

def MainAdmin(parent, db_name):
    """Factory function to create the MainAdminView"""
    return MainAdminView(parent, db_name)
