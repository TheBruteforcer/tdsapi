from customtkinter import *
from PIL import Image
from Proccesors.Database.CustomGainsDB import custom_gains_db
from datetime import datetime
from tkinter import messagebox
import os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

class CustomGainsView(CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color='#F0EBE3')
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        # Header
        header_frame = CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill=X, pady=(20,0), padx=20)
        
        CTkLabel(
            header_frame, 
            text="الدخل الإضافي والرحلات", 
            font=("Cairo", 28, "bold")
        ).pack(side=RIGHT)
        
        # Back button
        CTkButton(
            header_frame,
            text="عودة",
            font=("Cairo", 16),
            width=100,
            command=self.go_back
        ).pack(side=LEFT)

        # Main content area with tabs
        self.tabview = CTkTabview(self, height=600)
        self.tabview.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Add tabs
        self.tab_programs = self.tabview.add("البرامج النشطة")
        self.tab_new = self.tabview.add("إضافة برنامج جديد")
        self.tab_reports = self.tabview.add("التقارير")
        
        self.setup_programs_tab()
        self.setup_new_program_tab()
        self.setup_reports_tab()

    def setup_programs_tab(self):
        # Programs list frame with modern styling
        programs_frame = CTkFrame(self.tab_programs, fg_color="#FFFFFF", corner_radius=15)
        programs_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Title with icon
        title_frame = CTkFrame(programs_frame, fg_color="transparent")
        title_frame.pack(fill=X, padx=15, pady=10)
        
        board_icon = CTkImage(Image.open("TDSAssets/General/board2.png"), size=(32, 32))
        
        CTkLabel(
            title_frame,
            text="  البرامج النشطة  ",
            font=("Cairo", 24, "bold"),
            image=board_icon,
            compound="right"
        ).pack(side=RIGHT, padx=10)
        
        # Programs scrollable frame
        self.programs_list = CTkScrollableFrame(programs_frame, fg_color="transparent")
        self.programs_list.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        self.load_active_programs()

    def setup_new_program_tab(self):
        """Setup the new program tab with a modern form"""
        # Main container with white background
        form_frame = CTkFrame(self.tab_new, fg_color="#FFFFFF", corner_radius=15)
        form_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Title with icon
        title_frame = CTkFrame(form_frame, fg_color="transparent")
        title_frame.pack(fill=X, padx=15, pady=10)
        
        add_icon = CTkImage(Image.open("TDSAssets/General/done.png"), size=(32, 32))
        
        CTkLabel(
            title_frame,
            text="  إضافة برنامج جديد  ",
            font=("Cairo", 24, "bold"),
            image=add_icon,
            compound="right"
        ).pack(side=RIGHT, padx=10)
        
        # Create scrollable container for form
        form_container = CTkScrollableFrame(form_frame, fg_color="transparent")
        form_container.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # Basic Info Section
        basic_info = CTkFrame(form_container, fg_color="#F8F9FA", corner_radius=12)
        basic_info.pack(fill=X, pady=10)
        
        CTkLabel(
            basic_info,
            text="معلومات البرنامج الأساسية",
            font=("Cairo", 18, "bold"),
            text_color="#1976D2"
        ).pack(pady=10)
        
        # Title
        title_frame = CTkFrame(basic_info, fg_color="transparent")
        title_frame.pack(fill=X, padx=20, pady=5)
        CTkLabel(title_frame, text="عنوان البرنامج:", font=("Cairo", 14)).pack(anchor="e")
        self.title_entry = CTkEntry(title_frame, font=("Cairo", 14), width=400)
        self.title_entry.pack(pady=5)
        
        # Type
        type_frame = CTkFrame(basic_info, fg_color="transparent")
        type_frame.pack(fill=X, padx=20, pady=5)
        CTkLabel(type_frame, text="نوع البرنامج:", font=("Cairo", 14)).pack(anchor="e")
        self.type_menu = CTkOptionMenu(
            type_frame,
            values=["رحلة", "معسكر", "برنامج تدريبي", "أخرى"],
            font=("Cairo", 14),
            width=400
        )
        self.type_menu.pack(pady=5)
        
        # Cost
        cost_frame = CTkFrame(basic_info, fg_color="transparent")
        cost_frame.pack(fill=X, padx=20, pady=5)
        CTkLabel(cost_frame, text="التكلفة:", font=("Cairo", 14)).pack(anchor="e")
        self.cost_entry = CTkEntry(cost_frame, font=("Cairo", 14), width=400)
        self.cost_entry.pack(pady=5)
        
        # Dates Section
        dates_section = CTkFrame(form_container, fg_color="#F8F9FA", corner_radius=12)
        dates_section.pack(fill=X, pady=10)
        
        CTkLabel(
            dates_section,
            text="مواعيد البرنامج",
            font=("Cairo", 18, "bold"),
            text_color="#1976D2"
        ).pack(pady=10)
        
        dates_frame = CTkFrame(dates_section, fg_color="transparent")
        dates_frame.pack(fill=X, padx=20, pady=5)
        
        # Start Date
        start_frame = CTkFrame(dates_frame, fg_color="transparent")
        start_frame.pack(side=RIGHT, fill=X, expand=True, padx=5)
        CTkLabel(start_frame, text="تاريخ البداية:", font=("Cairo", 14)).pack(anchor="e")
        self.start_date_entry = CTkEntry(start_frame, font=("Cairo", 14), width=190)
        self.start_date_entry.pack(pady=5)
        CTkLabel(start_frame, text="مثال: 15 \\ 6 \\ 2024", font=("Cairo", 12), text_color="gray").pack()
        
        # End Date
        end_frame = CTkFrame(dates_frame, fg_color="transparent")
        end_frame.pack(side=RIGHT, fill=X, expand=True, padx=5)
        CTkLabel(end_frame, text="تاريخ النهاية:", font=("Cairo", 14)).pack(anchor="e")
        self.end_date_entry = CTkEntry(end_frame, font=("Cairo", 14), width=190)
        self.end_date_entry.pack(pady=5)
        CTkLabel(end_frame, text="مثال: 20 \\ 6 \\ 2024", font=("Cairo", 12), text_color="gray").pack()
        
        # Additional Info Section
        additional_info = CTkFrame(form_container, fg_color="#F8F9FA", corner_radius=12)
        additional_info.pack(fill=X, pady=10)
        
        CTkLabel(
            additional_info,
            text="معلومات إضافية",
            font=("Cairo", 18, "bold"),
            text_color="#1976D2"
        ).pack(pady=10)
        
        # Max Students
        max_students_frame = CTkFrame(additional_info, fg_color="transparent")
        max_students_frame.pack(fill=X, padx=20, pady=5)
        CTkLabel(max_students_frame, text="الحد الأقصى للمشتركين:", font=("Cairo", 14)).pack(anchor="e")
        self.max_students_entry = CTkEntry(max_students_frame, font=("Cairo", 14), width=400)
        self.max_students_entry.pack(pady=5)
        
        # Location
        location_frame = CTkFrame(additional_info, fg_color="transparent")
        location_frame.pack(fill=X, padx=20, pady=5)
        CTkLabel(location_frame, text="المكان:", font=("Cairo", 14)).pack(anchor="e")
        self.location_entry = CTkEntry(location_frame, font=("Cairo", 14), width=400)
        self.location_entry.pack(pady=5)
        
        # Description
        desc_frame = CTkFrame(additional_info, fg_color="transparent")
        desc_frame.pack(fill=X, padx=20, pady=5)
        CTkLabel(desc_frame, text="الوصف:", font=("Cairo", 14)).pack(anchor="e")
        self.desc_text = CTkTextbox(desc_frame, font=("Cairo", 14), height=100)
        self.desc_text.pack(fill=X, pady=5)
        CTkLabel(desc_frame, text="ملاحظة: إذا كان هذا الدخل لطالب معين، أضف كود الطالب في نهاية الوصف بهذا الشكل: (ID:1234)", font=("Cairo", 12), text_color="gray").pack(anchor="e", pady=(2,0))
        
        # Submit button
        CTkButton(
            form_container,
            text="إضافة البرنامج",
            font=("Cairo", 16, "bold"),
            command=self.add_new_program,
            fg_color="#4CAF50",
            hover_color="#388E3C",
            height=45
        ).pack(pady=20)

    def setup_reports_tab(self):
        """Setup the reports tab with statistics and export options"""
        # Main container
        reports_frame = CTkFrame(self.tab_reports, fg_color="#FFFFFF", corner_radius=15)
        reports_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Title with icon
        title_frame = CTkFrame(reports_frame, fg_color="transparent")
        title_frame.pack(fill=X, padx=15, pady=10)
        
        note_icon = CTkImage(Image.open("TDSAssets/General/note.png"), size=(32, 32))
        
        CTkLabel(
            title_frame,
            text="  التقارير والإحصائيات  ",
            font=("Cairo", 24, "bold"),
            image=note_icon,
            compound="right"
        ).pack(side=RIGHT, padx=10)
        
        # Statistics cards
        stats_container = CTkFrame(reports_frame, fg_color="transparent")
        stats_container.pack(fill=X, padx=15, pady=10)
        
        # Active programs card
        active_card = CTkFrame(stats_container, fg_color="#E3F2FD", corner_radius=15)
        active_card.pack(side=RIGHT, expand=True, fill=X, padx=5)
        
        active_count = len(custom_gains_db.get_active_programs())
        CTkLabel(
            active_card,
            text="البرامج النشطة",
            font=("Cairo", 18, "bold"),
            text_color="#1976D2"
        ).pack(pady=(10, 2))
        CTkLabel(
            active_card,
            text=str(active_count),
            font=("Cairo", 24, "bold"),
            text_color="#1976D2"
        ).pack(pady=(0, 10))
        
        # Total registrations card
        reg_card = CTkFrame(stats_container, fg_color="#E8F5E9", corner_radius=15)
        reg_card.pack(side=RIGHT, expand=True, fill=X, padx=5)
        
        total_regs = custom_gains_db.get_total_registrations()
        CTkLabel(
            reg_card,
            text="إجمالي المشتركين",
            font=("Cairo", 18, "bold"),
            text_color="#388E3C"
        ).pack(pady=(10, 2))
        CTkLabel(
            reg_card,
            text=str(total_regs),
            font=("Cairo", 24, "bold"),
            text_color="#388E3C"
        ).pack(pady=(0, 10))
        
        # Total revenue card
        revenue_card = CTkFrame(stats_container, fg_color="#FFF3E0", corner_radius=15)
        revenue_card.pack(side=RIGHT, expand=True, fill=X, padx=5)
        
        total_revenue = custom_gains_db.get_total_revenue()
        CTkLabel(
            revenue_card,
            text="إجمالي الإيرادات",
            font=("Cairo", 18, "bold"),
            text_color="#E65100"
        ).pack(pady=(10, 2))
        CTkLabel(
            revenue_card,
            text=f"{total_revenue:,} جنيه",
            font=("Cairo", 24, "bold"),
            text_color="#E65100"
        ).pack(pady=(0, 10))
        
        # Export section
        export_frame = CTkFrame(reports_frame, fg_color="#F5F5F5", corner_radius=15)
        export_frame.pack(fill=X, padx=15, pady=10)
        
        CTkLabel(
            export_frame,
            text="تصدير التقارير",
            font=("Cairo", 18, "bold")
        ).pack(pady=10)
        
        # Export buttons
        buttons_frame = CTkFrame(export_frame, fg_color="transparent")
        buttons_frame.pack(pady=10)
        
        CTkButton(
            buttons_frame,
            text="تصدير تقرير البرامج",
            font=("Cairo", 14),
            command=self.export_programs_report,
            fg_color="#2196F3",
            hover_color="#1976D2",
            width=200
        ).pack(side=RIGHT, padx=5)
        
        CTkButton(
            buttons_frame,
            text="تصدير تقرير المشتركين",
            font=("Cairo", 14),
            command=self.export_registrations_report,
            fg_color="#4CAF50",
            hover_color="#388E3C",
            width=200
        ).pack(side=RIGHT, padx=5)
        
        CTkButton(
            buttons_frame,
            text="تصدير تقرير الإيرادات",
            font=("Cairo", 14),
            command=self.export_revenue_report,
            fg_color="#FF9800",
            hover_color="#F57C00",
            width=200
        ).pack(side=RIGHT, padx=5)

    def load_active_programs(self):
        # Clear existing programs
        for widget in self.programs_list.winfo_children():
            widget.destroy()
            
        programs = custom_gains_db.get_active_programs()
        
        for program in programs:
            # Create program card with modern styling
            program_frame = CTkFrame(self.programs_list, fg_color="#F8F9FA", corner_radius=12)
            program_frame.pack(fill=X, padx=10, pady=5)
            
            # Program header
            header_frame = CTkFrame(program_frame, fg_color="#E3F2FD", corner_radius=8)
            header_frame.pack(fill=X, padx=5, pady=5)
            
            CTkLabel(
                header_frame,
                text=program[1],  # Title
                font=("Cairo", 18, "bold"),
                text_color="#1976D2"
            ).pack(side=RIGHT, padx=10, pady=5)
            
            CTkLabel(
                header_frame,
                text=f"النوع: {program[2]}",  # Type
                font=("Cairo", 14),
                text_color="#1976D2"
            ).pack(side=RIGHT, padx=10, pady=5)
            
            # Program details
            details_frame = CTkFrame(program_frame, fg_color="transparent")
            details_frame.pack(fill=X, padx=10, pady=5)
            
            CTkLabel(
                details_frame,
                text=f"التكلفة: {program[3]:,} جنيه",
                font=("Cairo", 14)
            ).pack(side=RIGHT, padx=10)
            
            CTkLabel(
                details_frame,
                text=f"التاريخ: {program[4]} - {program[5]}",
                font=("Cairo", 14)
            ).pack(side=RIGHT, padx=10)
            
            CTkLabel(
                details_frame,
                text=f"المكان: {program[7]}",
                font=("Cairo", 14)
            ).pack(side=RIGHT, padx=10)
            
            # Action buttons
            buttons_frame = CTkFrame(program_frame, fg_color="transparent")
            buttons_frame.pack(fill=X, padx=10, pady=5)
            
            CTkButton(
                buttons_frame,
                text="تسجيل مشترك",
                font=("Cairo", 14),
                fg_color="#4CAF50",
                hover_color="#388E3C",
                command=lambda pid=program[0]: self.show_registration_form(pid)
            ).pack(side=RIGHT, padx=5)
            
            CTkButton(
                buttons_frame,
                text="عرض التفاصيل",
                font=("Cairo", 14),
                fg_color="#2196F3",
                hover_color="#1976D2",
                command=lambda pid=program[0]: self.show_program_details(pid)
            ).pack(side=RIGHT, padx=5)
            
            CTkButton(
                buttons_frame,
                text="إضافة تحديث",
                font=("Cairo", 14),
                fg_color="#FF9800",
                hover_color="#F57C00",
                command=lambda pid=program[0]: self.show_update_form(pid)
            ).pack(side=RIGHT, padx=5)

    def add_new_program(self):
        """Handle adding a new program with validation"""
        try:
            # Get form values
            title = self.title_entry.get().strip()
            type_ = self.type_menu.get()
            cost = self.cost_entry.get().strip()
            start_date = self.start_date_entry.get().strip()
            end_date = self.end_date_entry.get().strip()
            max_students = self.max_students_entry.get().strip()
            location = self.location_entry.get().strip()
            description = self.desc_text.get("1.0", "end-1c").strip()
            
            # Validate required fields
            if not all([title, type_, cost, start_date, end_date, max_students, location, description]):
                messagebox.showerror("خطأ", "برجاء ملء جميع الحقول المطلوبة")
                return
            
            # Validate numeric fields
            try:
                cost = float(cost)
                max_students = int(max_students)
            except ValueError:
                messagebox.showerror("خطأ", "برجاء إدخال قيم صحيحة للتكلفة وعدد المشتركين")
                return
            
            # Add program to database
            program_id = custom_gains_db.add_program(
                title, type_, cost, start_date, end_date,
                max_students, description, location
            )
            
            # Show success message
            messagebox.showinfo("تم", "تم إضافة البرنامج بنجاح")
            
            # Clear form
            self.clear_new_program_form()
            
            # Refresh active programs list
            self.load_active_programs()
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء إضافة البرنامج: {str(e)}")

    def clear_new_program_form(self):
        """Clear all form fields"""
        self.title_entry.delete(0, 'end')
        self.type_menu.set("رحلة")
        self.cost_entry.delete(0, 'end')
        self.start_date_entry.delete(0, 'end')
        self.end_date_entry.delete(0, 'end')
        self.max_students_entry.delete(0, 'end')
        self.location_entry.delete(0, 'end')
        self.desc_text.delete("1.0", "end")

    def show_registration_form(self, program_id):
        # Create registration dialog
        dialog = CTkToplevel()
        dialog.title("تسجيل مشترك جديد")
        dialog.geometry("500x600")
        dialog.attributes('-topmost', True)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Form container
        form_frame = CTkFrame(dialog, fg_color="#FFFFFF")
        form_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Title
        CTkLabel(
            form_frame,
            text="تسجيل مشترك جديد",
            font=("Cairo", 24, "bold")
        ).pack(pady=20)
        
        # Student info
        student_frame = CTkFrame(form_frame, fg_color="transparent")
        student_frame.pack(fill=X, padx=20, pady=10)
        
        CTkLabel(student_frame, text="اسم الطالب:", font=("Cairo", 14)).pack(anchor="e")
        name_entry = CTkEntry(student_frame, font=("Cairo", 14), width=300)
        name_entry.pack(pady=5)
        
        CTkLabel(student_frame, text="رقم الهاتف:", font=("Cairo", 14)).pack(anchor="e")
        phone_entry = CTkEntry(student_frame, font=("Cairo", 14), width=300)
        phone_entry.pack(pady=5)
        
        CTkLabel(student_frame, text="هاتف ولي الأمر:", font=("Cairo", 14)).pack(anchor="e")
        parent_phone_entry = CTkEntry(student_frame, font=("Cairo", 14), width=300)
        parent_phone_entry.pack(pady=5)
        
        # Payment info
        payment_frame = CTkFrame(form_frame, fg_color="transparent")
        payment_frame.pack(fill=X, padx=20, pady=10)
        
        CTkLabel(payment_frame, text="المبلغ المدفوع:", font=("Cairo", 14)).pack(anchor="e")
        amount_entry = CTkEntry(payment_frame, font=("Cairo", 14), width=300)
        amount_entry.pack(pady=5)
        
        def register():
            try:
                name = name_entry.get().strip()
                phone = phone_entry.get().strip()
                parent_phone = parent_phone_entry.get().strip()
                amount = float(amount_entry.get().strip())
                
                if not all([name, phone, parent_phone, amount]):
                    messagebox.showerror("خطأ", "برجاء ملء جميع البيانات المطلوبة")
                    return
                
                custom_gains_db.register_student(
                    program_id,
                    name,
                    phone,
                    parent_phone,
                    amount
                )
                
                messagebox.showinfo("تم", "تم تسجيل المشترك بنجاح")
                dialog.destroy()
                self.load_active_programs()  # Refresh the programs list
                
            except ValueError:
                messagebox.showerror("خطأ", "برجاء إدخال مبلغ صحيح")
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ أثناء التسجيل: {str(e)}")
        
        # Register button
        CTkButton(
            form_frame,
            text="تسجيل",
            font=("Cairo", 16),
            command=register,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        ).pack(pady=20)

    def format_currency(self, amount):
        """Format currency in Egyptian Pounds"""
        if amount is None:
            return "0 جنيه"
        return f"{amount:,.2f} جنيه"

    def show_program_details(self, program_id):
        # Get program details
        program = custom_gains_db.get_program_details(program_id)
        if not program:
            messagebox.showerror("خطأ", "لم يتم العثور على البرنامج")
            return

        # Create details dialog
        dialog = CTkToplevel()
        dialog.title(f"تفاصيل البرنامج - {program[1]}")
        dialog.geometry("800x800")
        dialog.attributes('-topmost', True)

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        # Main container with scrollbar
        main_frame = CTkScrollableFrame(dialog)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Program info section
        info_frame = CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=15)
        info_frame.pack(fill=X, padx=10, pady=10)

        # Title and status
        title_frame = CTkFrame(info_frame, fg_color="transparent")
        title_frame.pack(fill=X, padx=20, pady=(20,10))

        CTkLabel(
            title_frame,
            text=program[1],
            font=("Cairo", 24, "bold")
        ).pack(side=RIGHT)

        status_label = CTkLabel(
            title_frame,
            text=program[9],  # Status
            font=("Cairo", 14),
            fg_color="#4CAF50" if program[9] == "active" else "#FFA000",
            corner_radius=10,
            text_color="white"
        )
        status_label.pack(side=LEFT, padx=10)

        # Details in two columns
        details_frame = CTkFrame(info_frame, fg_color="transparent")
        details_frame.pack(fill=X, padx=20, pady=10)

        left_col = CTkFrame(details_frame, fg_color="transparent")
        left_col.pack(side=LEFT, fill=BOTH, expand=True)

        right_col = CTkFrame(details_frame, fg_color="transparent")
        right_col.pack(side=RIGHT, fill=BOTH, expand=True)

        # Right column details
        CTkLabel(right_col, text=f"النوع: {program[2]}", font=("Cairo", 14)).pack(anchor="e", pady=2)
        CTkLabel(right_col, text=f"التكلفة: {self.format_currency(program[3])}", font=("Cairo", 14)).pack(anchor="e", pady=2)
        CTkLabel(right_col, text=f"المكان: {program[8]}", font=("Cairo", 14)).pack(anchor="e", pady=2)

        # Left column details
        CTkLabel(left_col, text=f"تاريخ البداية: {program[4]}", font=("Cairo", 14)).pack(anchor="e", pady=2)
        CTkLabel(left_col, text=f"تاريخ النهاية: {program[5]}", font=("Cairo", 14)).pack(anchor="e", pady=2)
        CTkLabel(left_col, text=f"الحد الأقصى: {program[6]} مشترك", font=("Cairo", 14)).pack(anchor="e", pady=2)

        # Description
        if program[7]:  # Only show description if it exists
            desc_frame = CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=15)
            desc_frame.pack(fill=X, padx=10, pady=10)

            CTkLabel(desc_frame, text="الوصف:", font=("Cairo", 16, "bold")).pack(anchor="e", padx=10, pady=5)
            CTkLabel(desc_frame, text=program[7], font=("Cairo", 14), wraplength=700).pack(padx=10, pady=5)

        # Registrations section
        reg_frame = CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=15)
        reg_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        reg_header = CTkFrame(reg_frame, fg_color="transparent")
        reg_header.pack(fill=X, padx=10, pady=5)

        CTkLabel(reg_header, text="المشتركون:", font=("Cairo", 16, "bold")).pack(side=RIGHT)
        
        # Add registration button
        CTkButton(
            reg_header,
            text="إضافة مشترك",
            font=("Cairo", 14),
            command=lambda: self.show_registration_form(program_id),
            fg_color="#4CAF50",
            hover_color="#388E3C"
        ).pack(side=LEFT)

        # Create scrollable frame for registrations
        reg_list = CTkScrollableFrame(reg_frame)
        reg_list.pack(fill=BOTH, expand=True, padx=10, pady=5)

        # Get and display registrations
        registrations = custom_gains_db.get_program_registrations(program_id)
        
        if not registrations:
            CTkLabel(
                reg_list,
                text="لا يوجد مشتركين حتى الآن",
                font=("Cairo", 14),
                text_color="gray"
            ).pack(pady=20)
        else:
            total_paid = 0
            for reg in registrations:
                reg_card = CTkFrame(reg_list, fg_color="#F8F9FA", corner_radius=10)
                reg_card.pack(fill=X, padx=5, pady=2)

                # Right side info
                info_frame = CTkFrame(reg_card, fg_color="transparent")
                info_frame.pack(side=RIGHT, fill=Y, padx=10, pady=5)

                CTkLabel(info_frame, text=f"الاسم: {reg[2]}", font=("Cairo", 14)).pack(anchor="e")
                CTkLabel(info_frame, text=f"الهاتف: {reg[3]}", font=("Cairo", 14)).pack(anchor="e")
                
                # Payment info
                payment_frame = CTkFrame(reg_card, fg_color="transparent")
                payment_frame.pack(side=LEFT, fill=Y, padx=10, pady=5)

                payment_status_color = "#4CAF50" if reg[5] == "paid" else "#FFA000"
                CTkLabel(
                    payment_frame,
                    text=f"حالة الدفع: {reg[5]}",
                    font=("Cairo", 12),
                    fg_color=payment_status_color,
                    corner_radius=5,
                    text_color="white"
                ).pack(anchor="w")

                CTkLabel(
                    payment_frame,
                    text=self.format_currency(reg[7]),
                    font=("Cairo", 14)
                ).pack(anchor="w")

                if reg[7]:  # If payment amount exists
                    total_paid += reg[7]

            # Show total payments
            total_frame = CTkFrame(reg_frame, fg_color="#E8F5E9", corner_radius=10)
            total_frame.pack(fill=X, padx=10, pady=10)

            CTkLabel(
                total_frame,
                text=f"إجمالي المدفوعات: {self.format_currency(total_paid)}",
                font=("Cairo", 16, "bold"),
                text_color="#2E7D32"
            ).pack(pady=10)

        # Updates section
        updates_frame = CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=15)
        updates_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        updates_header = CTkFrame(updates_frame, fg_color="transparent")
        updates_header.pack(fill=X, padx=10, pady=5)

        CTkLabel(updates_header, text="التحديثات:", font=("Cairo", 16, "bold")).pack(side=RIGHT)
        
        # Add update button
        CTkButton(
            updates_header,
            text="إضافة تحديث",
            font=("Cairo", 14),
            command=lambda: self.show_update_form(program_id),
            fg_color="#FF9800",
            hover_color="#F57C00"
        ).pack(side=LEFT)

        # Create scrollable frame for updates
        updates_list = CTkScrollableFrame(updates_frame)
        updates_list.pack(fill=BOTH, expand=True, padx=10, pady=5)

        # Get and display updates
        updates = custom_gains_db.get_program_updates(program_id)
        
        if not updates:
            CTkLabel(
                updates_list,
                text="لا توجد تحديثات حتى الآن",
                font=("Cairo", 14),
                text_color="gray"
            ).pack(pady=20)
        else:
            for update in updates:
                update_card = CTkFrame(updates_list, fg_color="#FFF3E0", corner_radius=10)
                update_card.pack(fill=X, padx=5, pady=2)

                CTkLabel(update_card, text=update[4], font=("Cairo", 14)).pack(anchor="e", padx=10, pady=5)
                CTkLabel(
                    update_card,
                    text=f"التاريخ: {update[2]}",
                    font=("Cairo", 12),
                    text_color="gray"
                ).pack(anchor="e", padx=10, pady=(0,5))

    def show_update_form(self, program_id):
        # Create update dialog
        dialog = CTkToplevel()
        dialog.title("إضافة تحديث")
        dialog.geometry("500x400")
        dialog.attributes('-topmost', True)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Form container
        form_frame = CTkFrame(dialog, fg_color="#FFFFFF")
        form_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Title
        CTkLabel(
            form_frame,
            text="إضافة تحديث جديد",
            font=("Cairo", 24, "bold")
        ).pack(pady=20)
        
        # Update content
        CTkLabel(form_frame, text="محتوى التحديث:", font=("Cairo", 14)).pack(anchor="e", padx=20)
        update_text = CTkTextbox(form_frame, font=("Cairo", 14), height=200)
        update_text.pack(fill=X, padx=20, pady=10)
        
        def add_update():
            try:
                content = update_text.get("1.0", "end-1c").strip()
                
                if not content:
                    messagebox.showerror("خطأ", "برجاء كتابة محتوى التحديث")
                    return
                
                custom_gains_db.add_program_update(program_id, content)
                
                messagebox.showinfo("تم", "تم إضافة التحديث بنجاح")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ أثناء إضافة التحديث: {str(e)}")
        
        # Add button
        CTkButton(
            form_frame,
            text="إضافة التحديث",
            font=("Cairo", 16),
            command=add_update,
            fg_color="#FF9800",
            hover_color="#F57C00"
        ).pack(pady=20)

    def export_programs_report(self):
        """Export programs data to Excel"""
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "البرامج"
            
            # Set RTL
            ws.sheet_view.rightToLeft = True
            
            # Headers
            headers = ['العنوان', 'النوع', 'التكلفة', 'تاريخ البداية', 'تاريخ النهاية', 'المكان', 'الحد الأقصى', 'عدد المشتركين']
            ws.append([''] * len(headers))  # Empty row for title
            ws.append(headers)
            
            # Get programs data
            programs = custom_gains_db.get_all_programs()
            
            for program in programs:
                reg_count = len(custom_gains_db.get_program_registrations(program[0]))
                ws.append([
                    program[1],  # Title
                    program[2],  # Type
                    program[3],  # Cost
                    program[4],  # Start date
                    program[5],  # End date
                    program[7],  # Location
                    program[6],  # Max students
                    reg_count    # Current registrations
                ])
            
            # Style the worksheet
            self._style_excel_worksheet(ws, "تقرير البرامج")
            
            # Save file
            filename = f"exports/programs_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            os.makedirs('exports', exist_ok=True)
            wb.save(filename)
            
            messagebox.showinfo("تم", f"تم تصدير التقرير بنجاح إلى:\n{filename}")
            from Views.ExcelReader import ExcelReader
            top = CTkToplevel()
            top.title(f"عرض ملف Excel: {filename}")
            top.attributes("-topmost", True)
            top.geometry("900x600")
            frame = CTkScrollableFrame(top, fg_color="white")
            frame.pack(fill="both", expand=True, padx=10, pady=10)
            ExcelReader(frame, file_path=filename)
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تصدير التقرير: {str(e)}")

    def export_registrations_report(self):
        """Export registrations data to Excel"""
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "المشتركون"
            
            # Set RTL
            ws.sheet_view.rightToLeft = True
            
            # Headers
            headers = ['البرنامج', 'اسم المشترك', 'رقم الهاتف', 'هاتف ولي الأمر', 'المبلغ المدفوع', 'تاريخ التسجيل']
            ws.append([''] * len(headers))  # Empty row for title
            ws.append(headers)
            
            # Get all programs
            programs = custom_gains_db.get_all_programs()
            
            for program in programs:
                registrations = custom_gains_db.get_program_registrations(program[0])
                for reg in registrations:
                    ws.append([
                        program[1],  # Program title
                        reg[2],      # Student name
                        reg[3],      # Phone
                        reg[4],      # Parent phone
                        reg[5],      # Amount paid
                        reg[6]       # Registration date
                    ])
            
            # Style the worksheet
            self._style_excel_worksheet(ws, "تقرير المشتركين")
            
            # Save file
            filename = f"exports/registrations_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            os.makedirs('exports', exist_ok=True)
            wb.save(filename)
            
            messagebox.showinfo("تم", f"تم تصدير التقرير بنجاح إلى:\n{filename}")
            from Views.ExcelReader import ExcelReader
            top = CTkToplevel()
            top.title(f"عرض ملف Excel: {filename}")
            top.attributes("-topmost", True)
            top.geometry("900x600")
            frame = CTkScrollableFrame(top, fg_color="white")
            frame.pack(fill="both", expand=True, padx=10, pady=10)
            ExcelReader(frame, file_path=filename)
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تصدير التقرير: {str(e)}")

    def export_revenue_report(self):
        """Export revenue data to Excel"""
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "الإيرادات"
            
            # Set RTL
            ws.sheet_view.rightToLeft = True
            
            # Headers
            headers = ['البرنامج', 'عدد المشتركين', 'إجمالي الإيرادات']
            ws.append([''] * len(headers))  # Empty row for title
            ws.append(headers)
            
            # Get all programs
            programs = custom_gains_db.get_all_programs()
            total_revenue = 0
            
            for program in programs:
                registrations = custom_gains_db.get_program_registrations(program[0])
                program_revenue = sum(reg[5] for reg in registrations)
                total_revenue += program_revenue
                
                ws.append([
                    program[1],                # Program title
                    len(registrations),        # Number of registrations
                    f"{program_revenue:,}"     # Program revenue
                ])
            
            # Add total row
            ws.append([''] * len(headers))
            ws.append(['الإجمالي', '', f"{total_revenue:,}"])
            
            # Style the worksheet
            self._style_excel_worksheet(ws, "تقرير الإيرادات")
            
            # Save file
            filename = f"exports/revenue_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            os.makedirs('exports', exist_ok=True)
            wb.save(filename)
            
            messagebox.showinfo("تم", f"تم تصدير التقرير بنجاح إلى:\n{filename}")
            from Views.ExcelReader import ExcelReader
            top = CTkToplevel()
            top.title(f"عرض ملف Excel: {filename}")
            top.attributes("-topmost", True)
            top.geometry("900x600")
            frame = CTkScrollableFrame(top, fg_color="white")
            frame.pack(fill="both", expand=True, padx=10, pady=10)
            ExcelReader(frame, file_path=filename)
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تصدير التقرير: {str(e)}")

    def _style_excel_worksheet(self, ws, title):
        """Apply consistent styling to Excel worksheets"""
        # Add title
        ws.merge_cells('A1:' + get_column_letter(ws.max_column) + '1')
        title_cell = ws['A1']
        title_cell.value = title
        title_cell.font = Font(bold=True, size=16, name='Cairo')
        title_cell.alignment = Alignment(horizontal='center', vertical='center')
        title_cell.fill = PatternFill(start_color="4CAF50", end_color="4CAF50", fill_type="solid")
        title_cell.font = Font(bold=True, size=16, name='Cairo', color="FFFFFF")
        
        # Style headers
        header_fill = PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid")
        header_font = Font(bold=True, size=12, name='Cairo')
        header_border = Border(
            bottom=Side(style='medium', color="4CAF50"),
            right=Side(style='thin', color="4CAF50"),
            left=Side(style='thin', color="4CAF50")
        )
        
        for cell in ws[2]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = header_border
        
        # Style data cells
        data_border = Border(
            right=Side(style='thin', color="4CAF50"),
            left=Side(style='thin', color="4CAF50")
        )
        data_font = Font(name='Cairo', size=11)
        
        for row in ws.iter_rows(min_row=3):
            for cell in row:
                cell.border = data_border
                cell.font = data_font
                cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Add bottom border to last row
        for cell in ws[ws.max_row]:
            cell.border = Border(
                bottom=Side(style='medium', color="4CAF50"),
                right=Side(style='thin', color="4CAF50"),
                left=Side(style='thin', color="4CAF50")
            )
        
        # Set row height
        ws.row_dimensions[1].height = 30  # Title row
        ws.row_dimensions[2].height = 25  # Header row
        
        # Adjust column widths
        for idx, column in enumerate(ws.columns, 1):
            max_length = 0
            column = list(column)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[get_column_letter(idx)].width = adjusted_width
        
        # Freeze header row
        ws.freeze_panes = 'A3'

    def go_back(self):
        self.destroy()
        from Views.TeamSelector import TeamView
        TeamView(self.parent).pack(fill=BOTH, expand=True) 