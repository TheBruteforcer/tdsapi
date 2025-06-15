from customtkinter import *
from json import loads, dumps, load, dump
from sqlite3 import *
from Views.StudentAccount import ShowAccount
from PIL import Image
import datetime
from threading import Thread
from tkinter import messagebox

def ViewPSec(parent:CTkScrollableFrame, db_name):
    
    conn = connect(db_name)
    ref = conn.cursor()
    total_paid = 0
    total_npaid = 0
    total_spaid = 0
    ref.execute("select * from Students")
    for std in ref.fetchall():
        mm = str(datetime.datetime.now().month)
        mm.replace("0", "")
        if std[10] != "BySession":
            for month in loads(std[10]):
                if mm == str(month["month"]).replace("شهر", "").strip():
                    paid = True if month["state"] == "تم" else False
            if paid == True :
                total_paid +=1
            else:
                total_npaid -= 1
        else:
            total_spaid += 1
    ref.execute("PRAGMA database_list;")
    team = ((ref.fetchone()[2]).split("\\")[-1]).replace(".db", "")
    for widget in parent.winfo_children():
        widget.destroy()

    # -- Title Frame -- #
    UpperingFrame = CTkFrame(parent, fg_color='white', corner_radius=20)
    UpperingFrame.pack(fill=X, padx=15, pady=10)

    CTkLabel(UpperingFrame, text='', image=CTkImage(Image.open('TDSAssets/General/student2.png'), size=(70,70))).pack(side=RIGHT, padx=10, pady=10)
    CTkLabel(UpperingFrame, text="صفحة جرد الطلاب", font=('Cairo Medium', 27)).pack(side=RIGHT, padx=10, pady=(15,10))
    def back():
        from Views.Admin import SuperUser
        for x in parent.winfo_children():
            x.destroy()
        SuperUser().UI(parent).pack(fill=BOTH, expand=True)
    CTkButton(UpperingFrame, text='الرجوع الي الرئيسية', font=('Cairo Medium', 16), command=back).pack(side=LEFT, padx=10, ipady=10, ipadx=17)
    MainingFrame = CTkFrame(parent, fg_color="white", height=630, corner_radius=20)
    FilterationFrame = CTkFrame(MainingFrame, fg_color="light Grey", corner_radius=10)
    CTkLabel(FilterationFrame,text="الفلاتر", font=("Cairo Medium", 22)).pack(pady=2, padx=(20, 10), side=RIGHT)
    avg_lbl = CTkLabel(FilterationFrame, font=("Cairo Medium", 20))
    def ShowAvgLBL(info):
        avg_lbl.configure(text = f"متوسط نسبة الحضور : {int(info['average_o_percentage'])}")
    ref.execute("SELECT * FROM Groups")
    PreGroups = ref.fetchall()
    
    Groups = ["  " + x[0] + "  " for x in PreGroups]
    Groups.insert(0, "  الفرقة العامة  ")
    StudentsList = CTkScrollableFrame(MainingFrame, height=530)
    
    
    
    stdimg = CTkImage(Image.open('TDSAssets/General/student2.png'), size=(40,40))
    def View(StudentsData):
        for XCV in StudentsList.winfo_children():
            XCV.destroy()
        print(StudentsData)
        for Student in StudentsData:
            mm = str(datetime.datetime.now().month)
            mm.replace("0", "")
            if Student[10] != "BySession":
                for month in loads(Student[10]):
                    if mm == str(month["month"]).replace("شهر", "").strip():
                        paid = True if month["state"] == "تم" else False
                        
            CustomViewFrame = CTkFrame(StudentsList, fg_color="#fffff0")
            CTkLabel(CustomViewFrame, text='', image=stdimg).pack(side=RIGHT, padx=20, pady=20)
            _CL1 = CTkFrame(CustomViewFrame, fg_color="transparent")
            _CL1.pack(fill=Y, padx=5, pady=5, side=RIGHT)
            CTkLabel(_CL1, text=Student[1], font=("Cairo Medium", 20), anchor="e").pack(pady=(15,2), fill=X) 
            CTkLabel(_CL1, text=Student[3], font=("Cairo Medium", 13), anchor="e").pack(fill=X, pady=(3,2)) 
            _CL2 = CTkFrame(CustomViewFrame, fg_color="transparent")
            _CL2.pack(fill=Y, padx=(5,15), pady=5, side=RIGHT)
            CTkLabel(_CL2, text=f"الفرقة : {Student[8]}", font=("Cairo Medium", 16), anchor="e").pack(pady=(15,2), fill=X) 
            CTkLabel(_CL2, text=f"نسبة الحضور : {Student[9]}", font=("Cairo Medium", 16), anchor="e").pack(fill=X, pady=(3,2)) 
            if Student[10] != "BySession":
                CTkFrame(CustomViewFrame, fg_color = "green" if paid else "red", corner_radius=180, width=20, height=20).pack(padx=(10, 30), side=RIGHT)
                CTkLabel(CustomViewFrame, text=f"الطالب دافع الشهر" if paid else "الطالب مدفعش الشهر", font=("Cairo Medium", 16)).pack(side=RIGHT) 
                
            
            
            
            
            CustomViewFrame.pack(fill=X, pady=(5,5), padx=10)
    
    
    
    
    
    
    def Listing(_temp):
        if GroupQuery.get() == "  الفرقة / المجموعة  " or GroupQuery.get() == "  الفرقة العامة  ":
            avg_lbl.pack_forget()
            if OPercentageQuery.get() == "  الترتيب حسب نسبة الحضور  " or OPercentageQuery.get() ==  "  بدون ترتيب  ":
                ref.execute("SELECT * FROM Students")
                View(ref.fetchall())
            elif OPercentageQuery.get() == "  تصاعديًا  ":
                ref.execute("SELECT * FROM Students ORDER BY CAST(OPercentage AS INTEGER)")
                View(ref.fetchall())
            elif OPercentageQuery.get() == "  تنازليًا  ":
                ref.execute("SELECT * FROM Students ORDER BY CAST(OPercentage AS INTEGER) DESC")
                View(ref.fetchall())
        else:
            ref.execute("PRAGMA database_list;")
            team = ((ref.fetchone()[2]).split("\\")[-1]).replace(".db", "")
            with open(f'{team}/cache_{GroupQuery.get().strip()}.json', 'r') as infofile:
                info = load(infofile) 
            ShowAvgLBL(info)
            avg_lbl.pack(side=LEFT, padx=30)
            ref.execute("SELECT * FROM Students")
            stds = ref.fetchall()
            for std in stds:
                droosin = loads(std[12])
                droosinlst = [droosini["name"] for droosini in droosin]
                print("filtred list : ",droosinlst)
                print("Option : ",(GroupQuery.get().strip()).split("|")[1])
                print("Non Filtred : ",droosin)
                if ((GroupQuery.get().strip()).split("|")[1]).strip() in droosinlst:
                    print((GroupQuery.get().strip()).split("|")[1])
                    ref.execute("UPDATE Students SET Badges = ? WHERE ID = ?", (GroupQuery.get().strip(), std[0]))
            ref.connection.commit()
            if OPercentageQuery.get() == "  الترتيب حسب نسبة الحضور  " or OPercentageQuery.get() ==  "  بدون ترتيب  ":
                ref.execute("SELECT * FROM Students WHERE Badges = ?", (GroupQuery.get().strip(),))
                View(ref.fetchall())
            elif OPercentageQuery.get() == "  تصاعديًا  ":
                ref.execute("SELECT * FROM Students WHERE Badges = ? ORDER BY CAST(OPercentage AS INTEGER)", (GroupQuery.get().strip(),))
                View(ref.fetchall())
            elif OPercentageQuery.get() == "  تنازليًا  ":
                ref.execute("SELECT * FROM Students WHERE Badges = ? ORDER BY CAST(OPercentage AS INTEGER) DESC", (GroupQuery.get().strip(),))
                View(ref.fetchall())
            
        
                
                
    
    GroupQuery = StringVar(value="  الفرقة / المجموعة  ")
    OPercentageQuery = StringVar(value="  الترتيب حسب نسبة الحضور  ")
    CTkOptionMenu(FilterationFrame, command=Listing, variable=GroupQuery, values=Groups, font=('Cairo Medium', 16),dropdown_font=('Cairo Medium', 16), anchor='e').pack(side=RIGHT, padx=10, ipadx=10, pady=5)
    CTkOptionMenu(FilterationFrame, command=Listing, variable=OPercentageQuery, values=["  تصاعديًا  ", "  تنازليًا  ", "  بدون ترتيب  "], font=('Cairo Medium', 16),dropdown_font=('Cairo Medium', 16), anchor='e').pack(side=RIGHT, padx=10, ipadx=10, pady=5)
    FilterationFrame.pack(fill=X, pady=(10, 20), padx=10)
    StudentsList.pack(fill=X, padx=10, pady=(0, 10))
    MainingFrame.pack(padx=15, pady=(0, 10), fill=X)
    
    FooterFrame = CTkFrame(parent , fg_color = "white")
    
    FLabelingFrame = CTkFrame(FooterFrame, fg_color="#FFFFA0", corner_radius=10)
    CTkLabel(FLabelingFrame, text="الأدوات المتاحة للجرد", font=("Cairo Medium", 21)).pack(pady=5)
    FLabelingFrame.pack(fill=X, padx=10, pady=10)
    
    DeleteNAStudentsFrame = CTkFrame(FooterFrame, fg_color="#F2F2F2")
    _DNAF1 = CTkFrame(DeleteNAStudentsFrame, fg_color="transparent")
    _DNAF1.pack(side= RIGHT, pady=10, padx=10)
    CTkLabel(_DNAF1, text=f"حذف جميع الطلاب الغير نشطين", font=("Cairo Medium", 25), anchor="e").pack(pady=(15,2), fill=X) 
    CTkLabel(_DNAF1, text=f"سيتم حذف الطلاب الذين يحملون نسبة حضور أقل من المتوسطة . هذه الخطوة لا رجعة فيها", font=("Cairo Medium", 14), anchor="e").pack(pady=(3,2), fill=X) 
    def DeleteNAStudents():
        if GroupQuery.get() == "  الفرقة / المجموعة  " or GroupQuery.get() == "  الفرقة العامة  ":
            messagebox.showerror("حدث خطأ", "لا يمكن اتمام هذه العملية بدون اختيار فرقة من الاعلى في سطر الفلاتر")
            return
        resp = CTkInputDialog(title="تأكيد الحذف", text="55102 لتأكيد عملية الحذف اكتب",font=("Cairo Medium", 20)).get_input()
        if int(resp) == 55102:    
            with open(f'{team}/cache_{GroupQuery.get().strip()}.json', 'r') as infofile:
                info = load(infofile) 
            ref.execute("DELETE FROM Students WHERE ? > CAST(OPercentage AS INTEGER) AND Group = ?", (info['average_o_percentage'],GroupQuery.get().strip(),))
            ref.connection.commit()
            Thread(Listing("_temp")).run()
        else: 
            return
    CTkButton(DeleteNAStudentsFrame,command=DeleteNAStudents, text="بدء العملية", fg_color="red", hover_color="red", text_color="white", font=("Cairo Medium", 16)).pack(side=LEFT, padx=20, pady=10, ipady=20)
    DeleteNAStudentsFrame.pack(fill=X, padx=10, pady=10)
    
    FooterFrame.pack(fill=X, padx=15)

    Thread(Listing("_temp")).run()

def StudentSView(parent):
    selection = ""
    for widget in parent.winfo_children():
        widget.destroy()
    
    conn = connect(f"Application.db")
    ref  = conn.cursor()
    
    ref.execute('SELECT * FROM PGroups')
    Groups = ref.fetchall()
    print(Groups)
    for Group in Groups:
        def OpenDashboard(database_name):
            ViewPSec(parent, database_name)
        CTkButton(parent,command= lambda dn = f"{Group[1]}.db" : OpenDashboard(dn), text=Group[1], font=("Tajawal Medium", 40)).pack(pady=10, ipadx=20)


