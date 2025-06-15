from customtkinter import *
from json import loads, dumps
from Proccesors.Database.db import *
from threading import Thread
from PIL import Image
from Views import Dashboard, whatsapptool
import json
from openpyxl import *
import requests
def show_complete(parent : CTkScrollableFrame,session_data):
    for x in parent.winfo_children():
        x.destroy()
    ff = CTkFrame(parent, fg_color='white', corner_radius=10)
    ff.pack(fill=BOTH, padx=10,pady=10,expand=True)
    CTkLabel(ff, text='', image=CTkImage(Image.open('TDSAssets/General/done_unthemed.png'), size=(100,100))).pack(pady=(200,10))
    CTkLabel(ff,text='تم اكمال الحصة بنجاح', font=('Tajwal Medium', 25)).pack(pady=10)
    CTkLabel(ff, text=session_data[1], font=('Tajwal Medium', 20)).pack(pady=5)
    CTkLabel(ff,text='تم حفظ تقارير الغياب في ملف التقارير', font=('Tajwal Medium', 25)).pack(pady=10)
    def back():
            for x in parent.winfo_children():
                x.destroy()
            Dashboard.Dashboard(parent).pack(fill=BOTH, expand=True)
    def Messages():

        ref.execute("SELECT * FROM Students WHERE Badges = ?", (session_data[10],))
        new_data = [
                    
                ]
        for y in ref.fetchall():
            attendance_list = json.loads(y[6])
            if any(d.get(session_data[1]) == 'Attended.' for d in attendance_list):
                try:
                    helper = whatsapptool.WhatsAppHelper()
                    helper.SendMessage({"type" : "DAttend", "std_name" : y[1]}, y[3])
                    helper.SendMessage({"type" : "DAttend", "std_name" : y[1]}, y[4])
                    print({"type" : "NAttend", "std_name" : y[1], "sess_name" : session_data[1], "g_name" : session_data[10]})
                except Exception as e:
                    print(e)
            else:
                try:
                    helper = whatsapptool.WhatsAppHelper()
                    helper.SendMessage({"type" : "NAttend", "std_name" : y[1], "sess_name" : session_data[1], "g_name" : session_data[10]}, y[3])
                    helper.SendMessage({"type" : "NAttend", "std_name" : y[1], "sess_name" : session_data[1], "g_name" : session_data[10]}, y[4])
                    print({"type" : "NAttend", "std_name" : y[1], "sess_name" : session_data[1], "g_name" : session_data[10]})
                except Exception as e:
                    print(e)
                new_data.append((y[1], f"{y[3]} | {y[4]}"))
        from openpyxl import load_workbook
        from openpyxl.styles import Font, Alignment

        # Load the workbook and select the active sheet
        file_path = "Templates/NonAttendanceTemplate.xlsx"
        wb = load_workbook(file_path)
        ws = wb.active  # Change to a specific sheet with wb["SheetName"] if needed

        # Define new data (example)

        # Find the first empty row starting from row 4
        start_row = 4
        while ws.cell(row=start_row, column=1).value:  # Check if the row is occupied
            start_row += 1

        font = Font(size=14)  # Adjust font size as needed
        alignment = Alignment(horizontal="center", vertical="center")

        for i, (name, phone) in enumerate(new_data):
            row = start_row + i
            ws.row_dimensions[row].height = 25  # Adjust row height
            
            cell_name = ws.cell(row=row, column=1, value=name)
            cell_phone = ws.cell(row=row, column=2, value=phone)
            
            cell_name.font = font
            cell_phone.font = font
            
            cell_name.alignment = alignment
            cell_phone.alignment = alignment

        # Save the workbook
        export_path = f"التقارير/تقرير_غياب_حصة_{session_data[1]}.xlsx"
        wb.save(export_path)

        print("Rows added successfully with larger font size!")
        # Open the saved file in ExcelReader (topmost window)
        from Views.ExcelReader import ExcelReader
        top = CTkToplevel()
        top.title(f"عرض ملف Excel: {export_path}")
        top.attributes("-topmost", True)
        top.geometry("900x600")
        frame = CTkScrollableFrame(top, fg_color="white")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        ExcelReader(frame, file_path=export_path)
                
    # Messages()
    CTkButton(ff, text='تمام , شكرًا', font=('Cairo Medium', 20), command=back).pack(fill=X,padx=50,pady=(40,200))