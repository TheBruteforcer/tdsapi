from customtkinter import *
from PIL import Image
from tkinter import messagebox
from Views.StudentAccount import ShowAccount
from Views import whatsapptool
import datetime
from sqlite3 import *
from json import *


class MoneyView:
    def __init__(self, parent, db_name):
        self.parent = parent
        self.db_name = db_name  # Store database name for use in queries
        self.setup_ui()

    def setup_ui(self):
        # Clear existing widgets
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        self.create_header_frame()
        self.create_main_content()

    def create_header_frame(self):
        """Creates the header section with title and back button"""
        header = CTkFrame(self.parent, fg_color='white', corner_radius=20)
        header.pack(fill=X, padx=15, pady=10)

        # Student icon
        student_icon = CTkImage(Image.open('TDSAssets/General/green_money.png'), size=(70, 70))
        CTkLabel(header, text='', image=student_icon).pack(side=RIGHT, padx=10, pady=10)
        
        # Title
        CTkLabel(
            header, 
            text="صفحة الماليات الكاملة  ", 
            font=('Cairo Medium', 27)
        ).pack(side=RIGHT, padx=10, pady=(15,10))

        # Back button
        CTkButton(
            header,
            text='الرجوع الي الرئيسية',
            font=('Cairo Medium', 16),
            command=self.go_back,
            hover_color='#2B6BE6',
            height=45
        ).pack(side=LEFT, padx=10)

    def create_main_content(self):
        """Creates the main content area with statistics frames and financial table"""
        # Upper frame for stats
        stats_container = CTkFrame(
            self.parent, 
            fg_color="transparent", 
            corner_radius=20
        )
        stats_container.pack(fill=X, padx=15, pady=10)

        # Create statistics frames side by side
        self.create_stats_frame(stats_container, "unpaid")
        self.create_stats_frame(stats_container, "paid")
        
        # Create financial records table
        self.create_financial_table()
        
        # Create tools frame
        self.create_tools_frame()

        # Create statistics frame
        self.create_statistics_frame()

    def create_stats_frame(self, parent, status_type):
        """Creates a statistics frame for either paid or unpaid students
        
        Args:
            parent: Parent widget to pack the frame into
            status_type (str): Either "paid" or "unpaid"
        """
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

        # Get counts
        paid_count, unpaid_count = self.get_payment_counts()
        
        # Count with special styling
        count = paid_count if status_type == "paid" else unpaid_count
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

        # Add export report button with enhanced styling
        export_frame = CTkFrame(stats_frame, fg_color="transparent")
        export_frame.pack(side=BOTTOM, fill=X, padx=10, pady=(0, 10))

        # Export icon
        export_icon = CTkImage(Image.open('TDSAssets/General/stats.png'), size=(20, 20))
        
        CTkButton(
            export_frame,
            text="استخراج تقرير تفصيلي في ملف إكسل",
            font=('Cairo Medium', 16),
            command=lambda: self.export_report(status_type),
            hover_color='#2B6BE6',
            height=45,
            corner_radius=15,
            image=export_icon,
            compound="right"
        ).pack(fill=X)

    def create_financial_table(self):
        """Creates a searchable table for financial records"""
        table_frame = CTkFrame(
            self.parent,
            fg_color="white",
            corner_radius=20
        )
        table_frame.pack(fill=BOTH, expand=True, padx=15, pady=10)

        # Search section
        search_frame = CTkFrame(table_frame, fg_color="transparent")
        search_frame.pack(fill=X, padx=20, pady=10)

        # Search label with icon
        search_icon = CTkImage(Image.open('TDSAssets/General/pencil.png'), size=(20, 20))
        CTkLabel(
            search_frame,
            text="   البحث بالتاريخ   ",
            font=("Cairo Medium", 16),
            image=search_icon,
            compound="right"
        ).pack(side=RIGHT, padx=10)

        # Date entry fields with better styling
        self.day_entry = CTkEntry(
            search_frame,
            placeholder_text="اليوم",
            width=70,
            font=("Cairo Medium", 14),
            corner_radius=10
        )
        self.day_entry.pack(side=RIGHT, padx=5)

        self.month_entry = CTkEntry(
            search_frame,
            placeholder_text="الشهر",
            width=70,
            font=("Cairo Medium", 14),
            corner_radius=10
        )
        self.month_entry.pack(side=RIGHT, padx=5)

        self.year_entry = CTkEntry(
            search_frame,
            placeholder_text="السنة",
            width=70,
            font=("Cairo Medium", 14),
            corner_radius=10
        )
        self.year_entry.pack(side=RIGHT, padx=5)

        # Search button with icon
        CTkButton(
            search_frame,
            text="بحث",
            font=("Cairo Medium", 14),
            command=self.search_records,
            width=100,
            corner_radius=10,
            hover_color='#2B6BE6'
        ).pack(side=RIGHT, padx=10)

        # Table headers with gradient background
        headers_frame = CTkFrame(table_frame, fg_color="#f0f0f0", corner_radius=15)
        headers_frame.pack(fill=X, padx=20, pady=(10, 0))

        headers = ["التاريخ", "اسم الطالب / الحصة", "المبلغ", "نوع الدفع"]
        for header in headers:
            CTkLabel(
                headers_frame,
                text=header,
                font=("Cairo Medium", 16, "bold"),
                width=150,
                fg_color="#e0e0e0",
                corner_radius=8
            ).pack(side=RIGHT, padx=10, pady=8)

        # Scrollable table content
        self.table_content = CTkScrollableFrame(
            table_frame,
            fg_color="transparent",
            height=400
        )
        self.table_content.pack(fill=BOTH, expand=True, padx=20, pady=10)

        # Initial load of records
        self.load_financial_records()

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
        """Load and display financial records"""
        try:
            conn = connect(self.db_name)
            ref = conn.cursor()
            
            # Get payment type (monthly or per session)
            ref.execute("PRAGMA database_list;")
            team = ((ref.fetchone()[2]).split("\\")[-1]).replace(".db", "")
            conn_checker = connect("Application.db")
            ref_checker = conn_checker.cursor()
            ref_checker.execute("SELECT * FROM PGroups WHERE Name = ?", (team,))
            payment_type = ref_checker.fetchone()[2]

            # Clear current records
            for widget in self.table_content.winfo_children():
                widget.destroy()

            # Build date filter
            if day and month and year:
                date_filter = f"{day} \ {month} \ {year}"
                ref.execute("SELECT * FROM Gains WHERE Date LIKE ?", (date_filter + '%',))
            else:
                ref.execute("SELECT * FROM Gains")
            
            gain_records = ref.fetchall()
            total_gains = 0

            # Process and display records
            for gain_record in gain_records:
                session_id = str(gain_record[0])
                amount = int(gain_record[2])
                date = gain_record[3]
                total_gains += amount

                record_frame = CTkFrame(
                    self.table_content,
                    fg_color="white",
                    corner_radius=10,
                    height=60
                )
                record_frame.pack(fill=X, pady=3, padx=5)
                record_frame.pack_propagate(False)  # Fixed height

                if "C" in session_id:  # Monthly payment
                    # Parse student info from Type field
                    student_info = loads(gain_record[1]) if gain_record[1] else {}
                    student_name = student_info.get("SName", "طالب غير معروف")
                    
                    # Icon for monthly payment
                    payment_icon = CTkImage(Image.open('TDSAssets/General/green_money.png'), size=(30, 30))
                    CTkLabel(
                        record_frame,
                        text="",
                        image=payment_icon
                    ).pack(side=RIGHT, padx=(15,5))

                    # Record details with better layout
                    details_frame = CTkFrame(record_frame, fg_color="transparent")
                    details_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10)

                    CTkLabel(
                        details_frame,
                        text=student_name,
                        font=("Cairo Medium", 16),
                        anchor="e"
                    ).pack(fill=X, pady=(5,0))

                    info_frame = CTkFrame(details_frame, fg_color="transparent")
                    info_frame.pack(fill=X)

                    CTkLabel(
                        info_frame,
                        text=f"التاريخ: {date}",
                        font=("Cairo Medium", 12),
                        text_color="gray"
                    ).pack(side=RIGHT, padx=5)

                    CTkLabel(
                        info_frame,
                        text="دفع شهري",
                        font=("Cairo Medium", 12),
                        text_color="green"
                    ).pack(side=RIGHT, padx=5)

                    # Amount with special styling
                    amount_frame = CTkFrame(record_frame, fg_color="#e8f5e9", corner_radius=8)
                    amount_frame.pack(side=LEFT, padx=15)
                    CTkLabel(
                        amount_frame,
                        text=f"{amount} جنيه",
                        font=("Cairo Medium", 14, "bold"),
                        text_color="green"
                    ).pack(padx=10, pady=5)

                else:  # Per session payment
                    # Get session title
                    ref.execute(f'SELECT Title FROM Sessions WHERE ID = ?', (session_id,))
                    session_title = ref.fetchone()
                    session_title = session_title[0] if session_title else f'جلسة رقم ({session_id})'

                    # Icon for session payment
                    session_icon = CTkImage(Image.open('TDSAssets/General/board2.png'), size=(30, 30))
                    CTkLabel(
                        record_frame,
                        text="",
                        image=session_icon
                    ).pack(side=RIGHT, padx=(15,5))

                    # Record details with better layout
                    details_frame = CTkFrame(record_frame, fg_color="transparent")
                    details_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10)

                    CTkLabel(
                        details_frame,
                        text=session_title,
                        font=("Cairo Medium", 16),
                        anchor="e"
                    ).pack(fill=X, pady=(5,0))

                    info_frame = CTkFrame(details_frame, fg_color="transparent")
                    info_frame.pack(fill=X)

                    CTkLabel(
                        info_frame,
                        text=f"التاريخ: {date}",
                        font=("Cairo Medium", 12),
                        text_color="gray"
                    ).pack(side=RIGHT, padx=5)

                    CTkLabel(
                        info_frame,
                        text="دفع بالحصة أو متعلق بها",
                        font=("Cairo Medium", 12),
                        text_color="blue"
                    ).pack(side=RIGHT, padx=5)

                    # Amount with special styling
                    amount_frame = CTkFrame(record_frame, fg_color="#e3f2fd", corner_radius=8)
                    amount_frame.pack(side=LEFT, padx=15)
                    CTkLabel(
                        amount_frame,
                        text=f"{amount} جنيه",
                        font=("Cairo Medium", 14, "bold"),
                        text_color="blue"
                    ).pack(padx=10, pady=5)

            # Add total at the bottom with enhanced styling
            total_frame = CTkFrame(
                self.table_content,
                fg_color="#f5f5f5",
                corner_radius=15,
                height=50
            )
            total_frame.pack(fill=X, pady=(10,2), padx=5)
            total_frame.pack_propagate(False)

            CTkLabel(
                total_frame,
                text=f"المجموع الكلي: {total_gains} جنيه",
                font=("Cairo Medium", 18, "bold"),
                text_color="#2B6BE6"
            ).pack(pady=10)

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحميل السجلات: {str(e)}")
        finally:
            if conn:
                conn.close()
            if conn_checker:
                conn_checker.close()

    def get_payment_counts(self):
        """
        Counts the number of paid and unpaid students for the current month
        
        Returns:
            tuple: (paid_count, unpaid_count)
        """
        try:
            conn = connect(self.db_name)
            ref = conn.cursor()
            
            ref.execute("SELECT * FROM Students")
            students = ref.fetchall()
            
            paid_count = 0
            unpaid_count = 0
            
            current_month = str(datetime.datetime.now().month)
            current_month = current_month.replace("0", "")
            
            for student in students:
                if student[10] != "BySession":  # Skip students who pay by session
                    payment_data = loads(student[10])  # Parse JSON payment data
                    
                    # Find current month's payment status
                    for month in payment_data:
                        if current_month == str(month["month"]).replace("شهر", "").strip():
                            if month["state"] == "تم":
                                paid_count += 1
                            else:
                                unpaid_count += 1
                            break
            
            return paid_count, unpaid_count
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء حساب عدد الطلاب: {str(e)}")
            return 0, 0
        finally:
            if conn:
                conn.close()

    def export_report(self, status_type):
        """Exports student payment data to Excel report
        
        Args:
            status_type (str): Either "paid" or "unpaid"
        """
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            import os
            from datetime import datetime
            
            # Create reports directory if it doesn't exist
            if not os.path.exists("التقارير"):
                os.makedirs("التقارير")

            wb = Workbook()
            ws = wb.active
            
            # Set sheet title
            title = "تقرير الطلاب المسددين" if status_type == "paid" else "تقرير الطلاب الغير مسددين"
            ws.title = title
            
            # Styling
            header_fill = PatternFill(start_color="4CAF50" if status_type == "paid" else "F44336",
                                    end_color="4CAF50" if status_type == "paid" else "F44336",
                                    fill_type="solid")
            header_font = Font(name='Cairo', size=12, bold=True, color="FFFFFF")
            cell_font = Font(name='Cairo', size=11)
            border = Border(left=Side(style='thin'), 
                          right=Side(style='thin'),
                          top=Side(style='thin'),
                          bottom=Side(style='thin'))
            
            # Add report title
            ws.merge_cells('A1:E1')
            title_cell = ws['A1']
            title_cell.value = title
            title_cell.font = Font(name='Cairo', size=16, bold=True)
            title_cell.alignment = Alignment(horizontal='center')
            
            # Add report date
            ws.merge_cells('A2:E2')
            date_cell = ws['A2']
            date_cell.value = f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            date_cell.font = Font(name='Cairo', size=12)
            date_cell.alignment = Alignment(horizontal='center')

            # Set headers
            headers = ["اسم الطالب", "رقم الهاتف", "رقم هاتف ولي الأمر", "المبلغ المدفوع", "تاريخ الدفع"]
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=4, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.border = border
                cell.alignment = Alignment(horizontal='center')
                ws.column_dimensions[chr(64 + col)].width = 20

            # Get student data
            conn = connect(self.db_name)
            ref = conn.cursor()
            
            current_month = str(datetime.now().month)
            current_month = current_month.replace("0", "")
            
            ref.execute("SELECT * FROM Students")
            students = ref.fetchall()
            
            row = 5
            for student in students:
                if student[10] != "BySession":  # Skip students who pay by session
                    payment_data = loads(student[10])
                    
                    # Find current month's payment status
                    for month in payment_data:
                        if current_month == str(month["month"]).replace("شهر", "").strip():
                            is_paid = month["state"] == "تم"
                            if (status_type == "paid" and is_paid) or (status_type == "unpaid" and not is_paid):
                                # Add student data to Excel
                                ws.cell(row=row, column=1, value=student[1])  # Name
                                ws.cell(row=row, column=2, value=student[3])  # Phone
                                ws.cell(row=row, column=3, value=student[4])  # Parent Phone
                                ws.cell(row=row, column=4, value=month.get("amount", "غير محدد"))  # Amount
                                ws.cell(row=row, column=5, value=month.get("date", "غير محدد"))  # Date
                                
                                # Apply styling to cells
                                for col in range(1, 6):
                                    cell = ws.cell(row=row, column=col)
                                    cell.font = cell_font
                                    cell.border = border
                                    cell.alignment = Alignment(horizontal='center')
                                
                                row += 1
                            break

            # Add total row
            total_row = row
            ws.merge_cells(f'A{total_row}:C{total_row}')
            total_label = ws[f'A{total_row}']
            total_label.value = "المجموع الكلي"
            total_label.font = Font(name='Cairo', size=12, bold=True)
            total_label.alignment = Alignment(horizontal='center')
            
            # Calculate total amount
            total_formula = f'=SUM(D5:D{row-1})'
            ws[f'D{total_row}'] = total_formula
            ws[f'D{total_row}'].font = Font(name='Cairo', size=12, bold=True)
            ws[f'D{total_row}'].border = border
            ws[f'D{total_row}'].alignment = Alignment(horizontal='center')
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            status_text = "مدفوع" if status_type == "paid" else "غير_مدفوع"
            filename = f"تقرير_الطلاب_{status_text}_{timestamp}.xlsx"
            
            # Save the workbook
            wb.save(os.path.join("التقارير", filename))
            messagebox.showinfo("نجاح", "تم استخراج التقرير بنجاح")
            from Views.ExcelReader import ExcelReader
            top = CTkToplevel()
            top.title(f"عرض ملف Excel: {os.path.join('التقارير', filename)}")
            top.attributes("-topmost", True)
            top.geometry("900x600")
            frame = CTkScrollableFrame(top, fg_color="white")
            frame.pack(fill="both", expand=True, padx=10, pady=10)
            ExcelReader(frame, file_path=os.path.join('التقارير', filename))
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء استخراج التقرير: {str(e)}")
        finally:
            if conn:
                conn.close()

    def go_back(self):
        """Handles navigation back to main admin view"""
        for widget in self.parent.winfo_children():
            widget.destroy()
        from Views.Admin import SuperUser
        SuperUser().UI(self.parent).pack(fill=BOTH, expand=True)

    def create_tools_frame(self):
        """Creates a tools frame with various financial management tools"""
        tools_frame = CTkFrame(
            self.parent,
            fg_color="white",
            corner_radius=20
        )
        tools_frame.pack(fill=X, padx=15, pady=10)

        # Title with icon
        title_frame = CTkFrame(tools_frame, fg_color="transparent")
        title_frame.pack(fill=X, padx=20, pady=(15,5))

        tools_icon = CTkImage(Image.open('TDSAssets/General/settings.png'), size=(25, 25))
        CTkLabel(
            title_frame,
            text="   أدوات إدارة المالية والمدفوعات   ",
            font=("Cairo Medium", 18, "bold"),
            image=tools_icon,
            compound="right"
        ).pack(side=RIGHT, padx=(5,0))

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

            # Initialize WhatsApp helper
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

    def create_statistics_frame(self):
        """Creates a statistics frame with financial analytics and predictions"""
        stats_frame = CTkFrame(
            self.parent,
            fg_color="white",
            corner_radius=20
        )
        stats_frame.pack(fill=X, padx=15, pady=10)

        # Title with icon
        title_frame = CTkFrame(stats_frame, fg_color="transparent")
        title_frame.pack(fill=X, padx=20, pady=(15,5))

        stats_icon = CTkImage(Image.open('TDSAssets/General/bulb.png'), size=(25, 25))
        CTkLabel(
            title_frame,
            text="   الإحصائيات والتحليلات المالية   ",
            font=("Cairo Medium", 18, "bold"),
            image=stats_icon,
            compound="right"
        ).pack(side=RIGHT)

        # Create grid for statistics cards
        grid_frame = CTkFrame(stats_frame, fg_color="transparent")
        grid_frame.pack(fill=X, padx=20, pady=10)

        # Current Month Stats
        current_stats = CTkFrame(grid_frame, fg_color="transparent")
        current_stats.pack(side=RIGHT, fill=X, expand=True)
        
        CTkLabel(
            current_stats,
            text="إحصائيات الشهر الحالي",
            font=("Cairo Medium", 16, "bold"),
            text_color="#2B6BE6"
        ).pack(pady=5)

        # Monthly Revenue Card
        monthly_frame = self.create_stat_card(
            current_stats,
            "إجمالي الإيرادات الشهرية",
            self.calculate_monthly_revenue(),
            "green_money.png",
            "#e8f5e9"
        )
        monthly_frame.pack(fill=X, pady=5)

        # Average Payment Card
        avg_frame = self.create_stat_card(
            current_stats,
            "متوسط المدفوعات",
            self.calculate_average_payment(),
            "note.png",
            "#e3f2fd"
        )
        avg_frame.pack(fill=X, pady=5)

        # Payment Rate Card
        rate_frame = self.create_stat_card(
            current_stats,
            "معدل الدفع",
            self.calculate_payment_rate(),
            "calender.png",
            "#fff3e0"
        )
        rate_frame.pack(fill=X, pady=5)

        # Predictions Section
        predictions = CTkFrame(grid_frame, fg_color="transparent")
        predictions.pack(side=RIGHT, fill=X, expand=True, padx=10)
        
        CTkLabel(
            predictions,
            text="التوقعات والتنبؤات",
            font=("Cairo Medium", 16, "bold"),
            text_color="#FF6B6B"
        ).pack(pady=5)

        # Expected Revenue Card
        expected_revenue = self.create_stat_card(
            predictions,
            "الإيرادات المتوقعة",
            self.calculate_expected_revenue(),
            "note.png",
            "#fff3e0"
        )
        expected_revenue.pack(fill=X, pady=5)

        # Potential Income Card
        potential_income = self.create_stat_card(
            predictions,
            "الدخل المحتمل من المتأخرين",
            self.calculate_potential_income(),
            "green_bag.png",
            "#e8f5e9"
        )
        potential_income.pack(fill=X, pady=5)

        # Session Prediction Card
        session_prediction = self.create_stat_card(
            predictions,
            "متوسط دخل الحصص اليومي",
            self.predict_session_income(),
            "calender.png",
            "#e3f2fd"
        )
        session_prediction.pack(fill=X, pady=5)

        # Create trends section with better styling
        trends_frame = CTkFrame(stats_frame, fg_color="#fafafa", corner_radius=15)
        trends_frame.pack(fill=X, padx=20, pady=10)

        trends_header = CTkFrame(trends_frame, fg_color="transparent")
        trends_header.pack(fill=X, padx=15, pady=(10,5))

        trend_icon = CTkImage(Image.open('TDSAssets/General/green_up.png'), size=(20, 20))
        CTkLabel(
            trends_header,
            text="   تحليل الاتجاهات والمؤشرات   ",
            font=("Cairo Medium", 16, "bold"),
            image=trend_icon,
            compound="right"
        ).pack(side=RIGHT)

        # Add trends in a grid layout
        trends_grid = CTkFrame(trends_frame, fg_color="transparent")
        trends_grid.pack(fill=X, padx=15, pady=10)

        trends = self.analyze_payment_trends()
        for i, trend in enumerate(trends):
            trend_item = CTkFrame(trends_grid, fg_color="white", corner_radius=10)
            trend_item.pack(fill=X, pady=2)
            
            CTkLabel(
                trend_item,
                text=trend["title"],
                font=("Cairo Medium", 14),
                text_color=trend["color"]
            ).pack(side=RIGHT, padx=10, pady=5)
            
            CTkLabel(
                trend_item,
                text=trend["value"],
                font=("Cairo Medium", 14, "bold"),
                text_color=trend["color"]
            ).pack(side=LEFT, padx=10, pady=5)

    def create_stat_card(self, parent, title, value, icon_name, bg_color):
        """Creates a statistics card with consistent styling"""
        card = CTkFrame(parent, fg_color=bg_color, corner_radius=15)
        
        icon = CTkImage(Image.open(f'TDSAssets/General/{icon_name}'), size=(30, 30))
        CTkLabel(card, text="", image=icon).pack(pady=10)
        
        CTkLabel(
            card,
            text=title,
            font=("Cairo Medium", 14)
        ).pack()
        
        CTkLabel(
            card,
            text=value,
            font=("Cairo Medium", 20, "bold")
        ).pack(pady=(0,10))
        
        return card

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
            ref.execute("SELECT * FROM Gains WHERE Date LIKE ?", (f'% \ {current_month} \ %',))
            for gain in ref.fetchall():
                if not gain[0].endswith('C'):  # Skip monthly payments (marked with C)
                    try:
                        total += int(gain[2])
                    except:
                        continue
            
            return f"{total:,} جنيه"
        finally:
            if conn:
                conn.close()

    def calculate_average_payment(self):
        """Calculates average payment per student"""
        try:
            paid_count, _ = self.get_payment_counts()
            if paid_count == 0:
                return "0 جنيه"
            
            total = int(self.calculate_monthly_revenue().replace(",", "").replace(" جنيه", ""))
            return f"{int(total/paid_count):,} جنيه"
        except:
            return "0 جنيه"

    def calculate_payment_rate(self):
        """Calculates payment completion rate"""
        paid, unpaid = self.get_payment_counts()
        total = paid + unpaid
        if total == 0:
            return "0%"
        return f"{int((paid/total) * 100)}%"

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
            ref.execute("SELECT * FROM Gains WHERE Date LIKE ?", (f'% \ {last_month} \ %',))
            for gain in ref.fetchall():
                if not gain[0].endswith('C'):
                    try:
                        last_month_revenue += int(gain[2])
                    except:
                        continue

            # Revenue Trend
            revenue_change = ((this_month_revenue - last_month_revenue) / last_month_revenue * 100) if last_month_revenue > 0 else 0
            trends.append({
                "title": "مقارنة بالشهر السابق",
                "value": f"{'↗️' if revenue_change >= 0 else '↘️'} {abs(int(revenue_change))}%",
                "color": "green" if revenue_change >= 0 else "red"
            })

            # Payment Status
            paid, unpaid = self.get_payment_counts()
            if paid > unpaid:
                trends.append({
                    "title": "معدل السداد",
                    "value": "↗️ جيد",
                    "color": "green"
                })
            else:
                trends.append({
                    "title": "معدل السداد",
                    "value": "↘️ يحتاج تحسين",
                    "color": "red"
                })
            
            # Collection Efficiency
            rate = int(self.calculate_payment_rate().replace("%", ""))
            if rate >= 80:
                trends.append({
                    "title": "كفاءة التحصيل",
                    "value": "🌟 ممتاز",
                    "color": "green"
                })
            elif rate >= 60:
                trends.append({
                    "title": "كفاءة التحصيل",
                    "value": "✅ جيد",
                    "color": "orange"
                })
            else:
                trends.append({
                    "title": "كفاءة التحصيل",
                    "value": "⚠️ ضعيف",
                    "color": "red"
                })

            # Average Payment Time
            early_count = 0
            late_count = 0
            ref.execute("SELECT * FROM Students")
            for student in ref.fetchall():
                if student[10] != "BySession":
                    payment_data = loads(student[10])
                    for month in payment_data:
                        if month["state"] == "تم":
                            try:
                                payment_date = int(month.get("date", "").split("/")[0])
                                if payment_date <= 15:  # Assuming first half of month is "early"
                                    early_count += 1
                                else:
                                    late_count += 1
                            except:
                                continue

            payment_timing = "مبكر" if early_count > late_count else "متأخر"
            trends.append({
                "title": "توقيت السداد",
                "value": f"⏰ {payment_timing}",
                "color": "green" if early_count > late_count else "orange"
            })

            # Session vs Monthly Revenue
            session_revenue = 0
            monthly_revenue = 0
            ref.execute("SELECT * FROM Gains")
            for gain in ref.fetchall():
                try:
                    if gain[0].endswith('C'):
                        monthly_revenue += int(gain[2])
                    else:
                        session_revenue += int(gain[2])
                except:
                    continue

            revenue_type = "شهري" if monthly_revenue > session_revenue else "بالحصة"
            trends.append({
                "title": "نوع الدخل الأعلى",
                "value": f"💰 {revenue_type}",
                "color": "blue"
            })
            
            return trends

        except Exception as e:
            print(f"Error in analyze_payment_trends: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def calculate_expected_revenue(self):
        """Calculates expected revenue based on current trends"""
        try:
            conn = connect(self.db_name)
            ref = conn.cursor()
            
            # Get average daily session income
            daily_session = float(self.predict_session_income().split()[0])
            
            # Get remaining days in month
            current_day = datetime.datetime.now().day
            days_remaining = 30 - current_day
            
            # Calculate expected session revenue
            expected_session_revenue = daily_session * days_remaining
            
            # Get potential income from unpaid students
            potential = float(self.calculate_potential_income().split()[0].replace(",", ""))
            
            # Total expected revenue
            total_expected = expected_session_revenue + potential
            
            return f"{int(total_expected):,} جنيه"
        except Exception as e:
            print(f"Error in calculate_expected_revenue: {e}")
            return "0 جنيه"
        finally:
            if conn:
                conn.close()

    def calculate_potential_income(self):
        """Calculates potential income from unpaid students"""
        try:
            conn = connect(self.db_name)
            ref = conn.cursor()
            current_month = str(datetime.datetime.now().month).replace("0", "")
            
            total_potential = 0
            ref.execute("SELECT * FROM Students")
            for student in ref.fetchall():
                if student[10] != "BySession":
                    payment_data = loads(student[10])
                    for month in payment_data:
                        if current_month == str(month["month"]).replace("شهر", "").strip():
                            if month["state"] != "تم":
                                try:
                                    total_potential += int(month.get("amount", 0))
                                except:
                                    continue
                            break
            
            return f"{total_potential:,} جنيه"
        finally:
            if conn:
                conn.close()

    def predict_session_income(self):
        """Predicts daily session income based on historical data"""
        try:
            conn = connect(self.db_name)
            ref = conn.cursor()
            current_month = str(datetime.datetime.now().month).replace("0", "")
            
            # Get session payments for current month
            ref.execute("SELECT * FROM Gains WHERE Date LIKE ? AND ID NOT LIKE '%C'", (f'% \ {current_month} \ %',))
            session_gains = ref.fetchall()
            
            if not session_gains:
                return "0 جنيه"
            
            # Calculate total session revenue
            total_session_revenue = sum(int(gain[2]) for gain in session_gains if gain[2].isdigit())
            
            # Calculate daily average
            current_day = datetime.datetime.now().day
            daily_average = total_session_revenue / current_day
            
            return f"{int(daily_average):,} جنيه"
        finally:
            if conn:
                conn.close()

def MoneySelectionView(parent):
    """Creates a selection view for choosing which grade's finances to view"""
    for widget in parent.winfo_children():
        widget.destroy()
    
    conn = connect(f"Application.db")
    ref = conn.cursor()
    
    ref.execute('SELECT * FROM PGroups')
    Groups = ref.fetchall()
    
    for Group in Groups:
        def OpenDashboard(database_name):
            for widget in parent.winfo_children():
                widget.destroy()
            MoneyView(parent, database_name)
            
        CTkButton(
            parent,
            command=lambda dn=f"{Group[1]}.db": OpenDashboard(dn),
            text=Group[1],
            font=("Tajawal Medium", 40)
        ).pack(pady=10, ipadx=20)

def Money(parent):
    """Factory function to create the MoneySelectionView"""
    return MoneySelectionView(parent)

