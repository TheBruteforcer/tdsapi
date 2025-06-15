from customtkinter import *
from Proccesors.Database.db import *
from Views import StudentAccount

def Search(parent,key):
    root2 = CTk()
    root2.title(f'نتائج البحث عن {key}')
    root2.geometry('570x400')
    tt = CTkScrollableFrame(root2, fg_color='white')
    tt.pack(fill=BOTH, expand=True)
    try:
        
        int(key)
        ref.execute(f'SELECT * FROM Students WHERE ID = "{key}"')
        students = ref.fetchall()

        for student in students:
            ff = CTkFrame(tt)
            ff.pack(fill=X, padx=10, pady=5)
            CTkLabel(ff, text=student[1], font=('Cairo Medium', 17)).pack(side=RIGHT, padx=(3,7), pady=3)
            CTkLabel(ff, text=f'    كود الطالب : {student[0]}    ',fg_color='#FFD35A', font=('Cairo Medium', 17)).pack(side=RIGHT, pady=3, padx=10)
            CTkButton(ff, text='الذهاب الي صفحة الطالب', font=('Cairo Medium', 15), command = lambda sd = student: StudentAccount.ShowAccount(parent, sd) ).pack(side=LEFT, padx=5, pady=3)
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
            CTkLabel(ff, text=f'    كود الطالب : {student[0]}    ',fg_color='#FFD35A', font=('Cairo Medium', 17)).pack(side=RIGHT, pady=3, padx=10)
            CTkButton(ff, text='الذهاب الي صفحة الطالب', font=('Cairo Medium', 15), command = lambda sd = student: StudentAccount.ShowAccount(parent, sd) ).pack(side=LEFT, padx=5, pady=3)
        if students == []:
            CTkLabel(tt, text='لا نتائج', font=('Cairo Medium', 37)).pack(fill=BOTH, expand=True, padx=(3,7), pady=3)
        
    root2.mainloop()


