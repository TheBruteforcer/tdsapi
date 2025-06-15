from customtkinter import *
from PIL import Image
from Widgets import Entries
from Proccesors import *
from requests import *
from Proccesors.Database.db import *
from threading import Thread
from Proccesors.Genric.SearchStudent import *
from AlphaControllers.EntryValidators import CheckBlank
from Views import AddStdForm, Spends, AddSpend, Sessions, SessionsSettings, Exams, Money, Groups, AllStudents, Dashboard
from time import localtime
from ServicesApplier.MLPowerdSelection import View
from json import loads
def Teachers(parent : CTkScrollableFrame):
    # GUI
    for widget in parent.winfo_children():
        widget.destroy()
    parent.update()
    # -- Title Frame -- #
    UpperingFrame = CTkFrame(parent, fg_color='white')
    UpperingFrame.pack(fill=X, padx=15, pady=10)

    ref.execute("SELECT * FROM Teachers")
    TeachersData = ref.fetchall()
    CTkLabel(UpperingFrame, text='', image=CTkImage(Image.open('TDSAssets/General/folder.png'), size=(70,70))).pack(side=RIGHT, padx=10, pady=10)
    CTkLabel(UpperingFrame, text="شؤون المعلمين", font=('Cairo Medium', 20)).pack(side=RIGHT, padx=10, pady=(15,10))
    def back():
        for x in parent.winfo_children():
            x.destroy()
        Dashboard.Dashboard(parent).pack(fill=BOTH, expand=True)
    CTkButton(UpperingFrame, text='الرجوع الي الرئيسية', font=('Cairo Medium', 16), command=back).pack(side=LEFT, padx=10, ipady=10, ipadx=17)

    MainingFrame = CTkFrame(parent, fg_color="white", height=630, corner_radius=20)
    TeachersList = CTkScrollableFrame(MainingFrame, height=530)
    GroupsOriList = []
    def SettingUpAvailableGroups():
        ref.execute("SELECT * FROM Groups")
        AllGroups = ref.fetchall()
        ref.execute("SELECT * FROM Teachers")
        AllTeachers = ref.fetchall()
        for SGroup in AllGroups:
            for T in AllTeachers:
                if SGroup[0] in loads(T[2]):
                    GroupsOriList.append(
                        SGroup[0]
                    )
        print(GroupsOriList)
    def TeacherDetails(TeacherInfo):
        xshow = CTkToplevel()
        xshow.geometry("850x600")
        xshow.attributes("-topmost", True)
        MainxshowFrame = CTkScrollableFrame(xshow, fg_color="white")
        MainxshowFrame.pack(fill=BOTH, expand=True)
        TeachersGroups = CTkScrollableFrame(MainxshowFrame, label_font=("Cairo Medium", 23), label_text="مجموعات المدرس", height=300)
        GroupsData = loads(TeacherInfo[2])
        for Group in GroupsData:
            ff = CTkFrame(TeachersGroups, fg_color="light grey")
            ff.pack(fill=X, padx=5, pady=5)
            CTkLabel(ff, text=Group, font=("Cairo Medium", 20)).pack(side=RIGHT, padx=10, pady=5)
        TeachersGroups.pack(padx=10, pady=10, fill=X)
        def AddNewGroupToTeacher():
            SettingUpAvailableGroups()
            xshow1 = CTkFrame(xshow, fg_color="transparent", corner_radius=15, height=300, width=330, border_width=2, border_color="grey")
            xshow1.place(relx = 0.5, rely=0.5, anchor = CENTER)
            menu = CTkFrame(xshow1, fg_color="#E5E5E5", corner_radius=10)
            CTkLabel(menu, text="المجموعات الغير مربوطة", font=("Cairo Medium", 15)).pack(side=RIGHT, padx=10, pady=3)
            CTkButton(menu, text="X",command=lambda:xshow1.destroy() , font=("Arial", 15),text_color="white", fg_color="red", hover=False, width=30, height=30).pack(side=LEFT, padx=(3,0), pady=3)
            menu.pack(fill=X, pady=(5, 5), padx=5)
            Mainxshow1Frame = CTkScrollableFrame(xshow1, fg_color="white", height=300, width=330)
            Mainxshow1Frame.pack(fill=BOTH, pady=5, padx=5)
            ref.execute("SELECT * FROM Groups")
            AllGroups = ref.fetchall()
            print(AllGroups)
            print(GroupsOriList)
            _counter = 0
            for PreGroup in AllGroups:
                try:
                    if PreGroup[0] in GroupsOriList:
                        AllGroups.remove(PreGroup[0])
                    else:
                        ff = CTkFrame(Mainxshow1Frame, fg_color="light grey")
                        ff.pack(fill=X, padx=5, pady=5)
                        CTkLabel(ff, text=PreGroup[0], font=("Cairo Medium", 15)).pack(side=RIGHT, padx=10, pady=5)
                        def add(GroupName):
                            GroupsInfoList = loads(TeacherInfo[2])
                            GroupsInfoList.append(GroupName)
                            ref.execute("UPDATE Teachers SET Groups = ? WHERE ID = ?", (dumps(GroupsInfoList),TeacherInfo[0],))
                            ref.connection.commit()
                            eventbutton.configure(state="disabled", text = "تم الإضافة", fg_color="grey")
                            View()
                            ref.execute("SELECT * FROM Teachers WHERE ID = ?", (TeacherInfo[0],))
                            TeacherInfo2 = ref.fetchall()[0]
                            print(TeacherInfo2)
                            GroupsData = loads(TeacherInfo2[2])
                            for w in TeachersGroups.winfo_children():
                                w.destroy()
                            for Group in GroupsData:
                                ff = CTkFrame(TeachersGroups, fg_color="light grey")
                                ff.pack(fill=X, padx=5, pady=5)
                                CTkLabel(ff, text=Group, font=("Cairo Medium", 20)).pack(side=RIGHT, padx=10, pady=5)
                                TeachersGroups.pack(padx=10, pady=10, fill=X)
                                CTkButton(TeachersGroups, command=AddNewGroupToTeacher , font=("Cairo Medium", 20), text="ربط مجموعة بالمدرس").pack(side=BOTTOM, fill=X, pady=10, padx=5)

                        eventbutton = CTkButton(ff,command=lambda g = PreGroup[0] :add(g), text="إضافة", font=("Cairo Medium", 15))
                        eventbutton.pack(side=LEFT, pady=5, padx=5)
                    _counter += 1
                except Exception as e:
                    print(e)
            
        CTkButton(TeachersGroups, command=AddNewGroupToTeacher , font=("Cairo Medium", 20), text="ربط مجموعة بالمدرس").pack(side=BOTTOM, fill=X, pady=10, padx=5)
    def View():
        for XCV in TeachersList.winfo_children():
            XCV.destroy()
        ref.execute("SELECT * FROM Teachers")
        TeachersData = ref.fetchall()
        print(TeachersData)
        for Teacher in TeachersData:
            CustomViewFrame = CTkFrame(TeachersList, fg_color="#fffff0")
            CTkLabel(CustomViewFrame, text='', image=CTkImage(Image.open('TDSAssets/General/bulb.png'), size=(60,60))).pack(side=RIGHT, padx=20, pady=20)
            _CL1 = CTkFrame(CustomViewFrame, fg_color="transparent")
            _CL1.pack(fill=Y, padx=5, pady=5, side=RIGHT)
            CTkLabel(_CL1, text=Teacher[1], font=("Cairo Medium", 20), anchor="e").pack(pady=(15,2), fill=X) 
            CTkLabel(_CL1, text=f"عدد المجموعات : {len(loads(Teacher[2]))}", font=("Cairo Medium", 13), anchor="e").pack(fill=X, pady=(3,2)) 
            _CL2 = CTkFrame(CustomViewFrame, fg_color="transparent")
            _CL2.pack(fill=Y, padx=15, pady=5, side=LEFT)
            CTkButton(_CL2, text="تفاصيل المدرس", command=lambda:TeacherDetails(Teacher) ,font=("Cairo Medium", 16), fg_color="green", hover_color="lime", text_color="light grey").pack(pady=10)
            CTkButton(_CL2, text="حذف المدرس", font=("Cairo Medium", 16), fg_color="red", hover_color="pink", text_color="white").pack(pady=(0, 10))
            CustomViewFrame.pack(fill=X, pady=(5,5), padx=10)
    View()
    TeachersList.pack(fill=X, padx=10, pady=(10, 10))
    MainingFrame.pack(padx=15, pady=(0, 10), fill=X)
    
    FooterFrame = CTkFrame(parent , fg_color = "white")
    
    FLabelingFrame = CTkFrame(FooterFrame, fg_color="#FFFFA0", corner_radius=10)
    CTkLabel(FLabelingFrame, text="الأدوات المُتوفرة للإدارة", font=("Cairo Medium", 19)).pack(pady=5)
    FLabelingFrame.pack(fill=X, padx=10, pady=10)
    
    AddTeacher = CTkFrame(FooterFrame, fg_color="#F2F2F2")
    _DNAF1 = CTkFrame(AddTeacher, fg_color="transparent")
    _DNAF1.pack(side= RIGHT, pady=10, padx=10)
    CTkLabel(_DNAF1, text=f"إضافة مدرس جديد", font=("Cairo Medium", 25), anchor="e").pack(pady=(15,2), fill=X) 
    CTkLabel(_DNAF1, text=f"إضافة مدرس جديد إلى مجموعة مدرسينا في السنتر", font=("Cairo Medium", 14), anchor="e").pack(pady=(3,2), fill=X) 
    def AddTeacherToListHim():
        teacherName = CTkInputDialog(title="إضافة المدرس", font=("Tajawal Medium", 15), text="اسم المدرس")
        name = teacherName.get_input()
        if not name == None:
            ref.execute("SELECT * FROM Teachers")
            id = len(ref.fetchall())
            ref.execute("INSERT INTO Teachers VALUES (?,?,?,?)", (str(id), name, "[]", ""))
            ref.connection.commit()
        View()
        return
    CTkButton(AddTeacher,command=AddTeacherToListHim, text="إضافة", hover_color="red", text_color="white", font=("Cairo Medium", 16)).pack(side=LEFT, padx=20, pady=10, ipady=20)
    AddTeacher.pack(fill=X, padx=10, pady=10)
    
    FooterFrame.pack(fill=X, padx=15)






