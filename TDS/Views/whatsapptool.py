from requests import post, get
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
from Views import AddStdForm,whatsapptool,Dashboard ,Spends, AddSpend, Sessions, SessionsSettings, Exams, Money, Groups, AllStudents, Teachers
from time import localtime
from ServicesApplier.MLPowerdSelection import View
from customtkinter import *
from Proccesors.Database.db import *
from Views import StudentAccount
from random import randint
from tkinter import messagebox
class WhatsAppHelper:
    def __init__(self): 
        self.identifier = randint(000000000000, 999999999999)
        self.stats      = {"active" : True}
    
    def UIPage(self, parent : CTkScrollableFrame):
        for x in parent.winfo_children():
            x.destroy()
        UpperingFrame = CTkFrame(parent, fg_color='white')
        UpperingFrame.pack(fill=X, padx=15, pady=10)
        CTkLabel(UpperingFrame, text='', image=CTkImage(Image.open('TDSAssets/General/whatsapp.png'), size=(70,70))).pack(side=RIGHT, padx=10, pady=10)
        CTkLabel(UpperingFrame, text="حملات الواتساب", font=('Cairo Medium', 20)).pack(side=RIGHT, padx=10, pady=(15,10))
        def back():
            for x in parent.winfo_children():
                x.destroy()
            Dashboard.Dashboard(parent).pack(fill=BOTH, expand=True)
        CTkButton(UpperingFrame, text='الرجوع الي الرئيسية', font=('Cairo Medium', 16), command=back).pack(side=LEFT, padx=10, ipady=10, ipadx=17)

        frame2 = CTkFrame(parent, fg_color='White')
        frame2.pack(fill=BOTH, expand=True, padx=10)
        CTkLabel(frame2, text='       حـملة جـــديـدة      ', font=('Cairo Medium', 22), anchor='e', fg_color='#f6f9fc').pack(fill=X, ipadx=10, ipady=5)
        name = Entries.UpperLabeledEntry(frame2, 'عنوان الحملة')
        name.pack(pady=(10,10), fill=X, padx=10)
        I = StringVar(value = 'المجموعة المستهدفة')
        ref.execute("select * from groups")
        PreGroups = ref.fetchall()
        Groups = [Group[0] for Group in PreGroups]
        message = Entries.UpperLabeledEntry(frame2, 'الرسالة او التنويه')
        message.pack(pady=(10,10), fill=X, padx=10)
        CTkOptionMenu(frame2, font=("Cairo Medium", 20 ), dropdown_font=("Cairo Medium", 20), variable=I, values=Groups).pack(fill=X, padx=16,pady=10)
        campigans = CTkScrollableFrame(parent, height=300)
        
        def add():
            if CheckBlank(name.entry) :
                ref.execute("INSERT INTO Campigans VALUES (?,?,?,?)", ("", name.get_input(), I.get(), "{}")) 
                ref.connection.commit()
                refresh()
                messagebox.showinfo("جاري العمل", "تم بدء الحملة .. تأكد من ثبات الانترنت لفترة 5 دقايق كمان")
                ref.execute("SELECT * FROM Students WHERE Badges = ?", (I.get(),))
                selected = ref.fetchall()
                _processess = []
                for std in selected :
                    _processess.append({"std_name" : std[1], "number" : std[3]})
                helper = whatsapptool.WhatsAppHelper()
                for _worker in _processess:
                    helper.SendMessage({"type" : "Custom", "std_name" : _worker["std_name"], "message" : message.get_input()}, _worker["number"])
        CTkButton(frame2,command=add, text="بدء الحملة", font=("Cairo Medium", 17)).pack(pady=(0, 10), ipadx=30)
        def refresh():
            for x in campigans.winfo_children():
                x.destroy()
            ref.execute("SELECT * FROM Campigans")
            camps = ref.fetchall()
            for camp in camps:
                ff = CTkFrame(campigans, fg_color="white")
                ff.pack(fill=X, padx=10,pady=5)
                CTkFrame(ff, fg_color="green", width=30, height=30, corner_radius=180).pack(side=RIGHT, pady=10,padx=(10, 5))
                CTkLabel(ff, text=camp[1], font=("Cairo Medium", 21)).pack(side=RIGHT)
                CTkLabel(ff, text=camp[2], font=("Cairo Medium", 19)).pack(side=RIGHT, padx=10)
        refresh()
        campigans.pack(pady=10, padx=10, fill=X)
        
        
    def SendMessage(self, settings, number):
        if settings["type"] == "NAttend" :
            template_of_message = f"""
مرحبًا بك ولي أمر الطالب {settings["std_name"]} .
نود إعلامكم بغياب الطالب عن حصة {settings["sess_name"]} اليوم ,
في المجموعة {settings["g_name"]}

تنويه : كثرة الغياب يؤدي إلى حذف حساب الطالب من النظام الخاص بنا.
هذه رسالة تلقائية من نظام إدارة الدروس المتقدم
شكرا
            """


        elif settings["type"] == "DAttend" :
            template_of_message = f"""
مرحبًا بك ولي أمر الطالب {settings["std_name"]} .
نود إبلاغكم بإنتهاء الحصة حالًا وخروج الطالب من السنتر بأمان

هذه رسالة تلقائية من نظام إدارة الدروس المتقدم
شكرا
            """
        elif settings["type"] == "PMonth":
            template_of_message = f"""
مرحبًا بك ولي أمر الطالب {settings["std_name"]} .
نشكركم على سداد الإشتراك الشهري في السنتر
هذه رسالة تلقائية من نظام إدارة الدروس المتقدم
شكرا
            """
        elif settings["type"] == "SubscribeNum":
            template_of_message = f"""
مرحبًا بك ولي أمر الطالب {settings["std_name"]} .
تم تسجيل الرقم الخاص بك كرقم ولي أمر للطالب المشار إليه أدناه

هذه رسالة تلقائية من نظام إدارة الدروس المتقدم
شكرا
            """
        elif settings["type"] == "SubscribeStd":
            template_of_message = f"""
أهلًا أهلًا بيك يا {settings["std_name"]} في عائلتنا المميزة
يسعدنا إشتراكك في سنتر الاوائل
الكود الخاص بيك : {settings["std_id"]}
اسمك المسجل عندنا : {settings["std_name"]}

هذه رسالة تلقائية من نظام إدارة الدروس المتقدم
شكرا
            """
        elif settings["type"] == "ExmDeg":
            template_of_message = f"""
مرحبًا بك ولي أمر الطالب {settings["std_name"]} .
تم تسجيل للتو درجة امتحان الطالب
*الدرجة*
عنوان الامتحان : {settings["extitle"]}
الدرجة : {settings["exdeg"]} من {settings["exmax"]}

هذه رسالة تلقائية من نظام إدارة الدروس المتقدم
شكرا
            """
        elif settings["type"] == "Custom":
            template_of_message = f"""
رسالة لولي أمر الطالب {settings["std_name"]}
الرسالة : 

{settings["message"]}

وشكرًا
"""
        elif settings["type"] == "GAdd":
            template_of_message = f"""
مرحبًا بك ولي أمر الطالب {settings["std_name"]} .
تم تسجيل الطالب في مجموعة جديدة
اسم المجموعة \ المادة : {settings["inv_name"]}
زيادة الإشتراك الشهري  : {settings["inv_price"]} جنيه
المعاد : {settings["inv_time"]}


هذه رسالة تلقائية من نظام إدارة الدروس المتقدم
شكرا
            """
        try:
            response = post(
                "https://noti-fire.com/api/send/message",
                json={
                    "device_id": "2f122a71-626e-4b1f-bd14-0b7d1e066fed",
                    "to": f"+2{number}",
                    "message": template_of_message
                },
                headers={"Content-Type": "application/json"}
            )

            print(response.text)  # Print API response
        except Exception as e:
            print(e)
        