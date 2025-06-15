from customtkinter import *
from tkinter import messagebox, filedialog
import datetime
import csv
from Proccesors.Database.db import get_all_pending_codes, delete_all_pending_codes, init_codes_db

class PendingCodesView(CTkFrame):
    def __init__(self, parent, back_callback=None):
        super().__init__(parent, fg_color='white')
        self.pack(fill=BOTH, expand=True)
        self.back_callback = back_callback
        init_codes_db()
        self.create_ui()

    def create_ui(self):
        for widget in self.winfo_children():
            widget.destroy()
        top_frame = CTkFrame(self, fg_color='transparent')
        top_frame.pack(fill=X, pady=(10,0), padx=10)
        back_btn = CTkButton(top_frame, text='الرجوع', font=('Cairo Medium', 16), fg_color='#fc5f7d', command=self.go_back)
        back_btn.pack(side=LEFT, padx=5)
        CTkLabel(top_frame, text='الكروت الغير مطبوعة', font=('Cairo Medium', 24, 'bold')).pack(side=RIGHT, pady=10, padx=10)
        self.codes_table = CTkFrame(self, fg_color='#f7f7f7', corner_radius=12)
        self.codes_table.pack(fill=BOTH, expand=True, padx=20, pady=10)
        self.load_codes()
        btns = CTkFrame(self, fg_color='transparent')
        btns.pack(pady=10)
        CTkButton(btns, text='تصدير إلى Excel', font=('Cairo Medium', 16), command=self.export_to_excel, fg_color='#1976D2').pack(side=RIGHT, padx=10)
        CTkButton(btns, text='وضع علامة تم وطباعة', font=('Cairo Medium', 16), command=self.mark_all_done, fg_color='#13b272').pack(side=RIGHT, padx=10)

    def load_codes(self):
        for widget in self.codes_table.winfo_children():
            widget.destroy()
        codes = get_all_pending_codes()
        if not codes:
            CTkLabel(self.codes_table, text='لا يوجد كروت غير مطبوعة حالياً', font=('Cairo Medium', 18)).pack(pady=30)
            return
        header = CTkFrame(self.codes_table, fg_color='#e0e0e0')
        header.pack(fill=X, padx=5, pady=2)
        for col, txt in enumerate(['ID', 'كود الطالب', 'اسم الطالب', 'تاريخ الإضافة']):
            CTkLabel(header, text=txt, font=('Cairo Medium', 16, 'bold')).grid(row=0, column=col, padx=10, pady=5)
        for i, row in enumerate(codes):
            row_frame = CTkFrame(self.codes_table, fg_color='white')
            row_frame.pack(fill=X, padx=5, pady=1)
            for col, val in enumerate(row):
                CTkLabel(row_frame, text=str(val), font=('Cairo Medium', 15)).grid(row=0, column=col, padx=10, pady=4)

    def export_to_excel(self):
        codes = get_all_pending_codes()
        if not codes:
            messagebox.showinfo('تنبيه', 'لا يوجد بيانات لتصديرها.')
            return
        file_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')], title='حفظ ملف الكروت')
        if not file_path:
            return
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'كود الطالب', 'اسم الطالب', 'تاريخ الإضافة'])
            for row in codes:
                writer.writerow(row)
        messagebox.showinfo('تم', 'تم تصدير الكروت بنجاح!')

    def mark_all_done(self):
        if messagebox.askyesno('تأكيد', 'هل أنت متأكد من وضع علامة تم وحذف جميع الكروت الغير مطبوعة؟'):
            delete_all_pending_codes()
            self.load_codes()
            messagebox.showinfo('تم', 'تم حذف جميع الكروت الغير مطبوعة!')

    def go_back(self):
        if self.back_callback:
            self.back_callback()
        else:
            self.destroy()

def PendingCodesViewLauncher(parent):
    PendingCodesView(parent) 