from customtkinter import *
from Proccesors.Database.db import *
from json import loads, dumps
from PIL import Image


def LoadTasks(listview : CTkScrollableFrame, session_data):
    def markAsComp(title):
        ref.execute('SELECT * FROM Sessions WHERE ID = ?', (session_data[0],))
        ref.execute("PRAGMA database_list;")
        team = ((ref.fetchone()[2]).split("\\")[-1]).replace(".db", "")
        conn_checker = connect("Application.db")
        ref_checker  = conn_checker.cursor()
        ref_checker.execute("SELECT * FROM PGroups WHERE Name = ?", (team,))
        type = ref_checker.fetchone()[2]
        if type == "بالحصة":
            tasks = loads(ref.fetchone()[8])
        else:
            tasks = loads(ref.fetchone()[8])
            
        for task in tasks:
            if task['title'] == title:
                if task['title'] == 'عد فلوس الحصه':
                    pop = CTkToplevel()
                    pop.geometry('400x400')
                    pop.attributes('-topmost', True)
                    pop.title('اتمام المهمة')
                    ref.execute('SELECT * FROM Sessions WHERE ID = ?', (session_data[0],))
                    session_data2 = ref.fetchone() 
                    attends_num2 = session_data2[4]
                    price = session_data2[3]
                    total_spends = 0
                    ref.execute('SELECT * FROM Spends')
                    for spend in ref.fetchall():        
                        try:
                            if loads(spend[3])['session-info']['id'] == session_data[0]:
                                total_spends += int(spend[0])
                        except:
                            pass
                    CTkLabel(pop, text='لما هتعد الفلوس هتلاقي المبلغ بعد الحسابات', font=('Cairo Medium', 25), wraplength=300).pack(pady=30)
                    gains = 0
                    ref.execute('SELECT * FROM Gains WHERE ID = ?',  (session_data[0],))
                    for g in ref.fetchall():
                        gains += int(g[2])
                    CTkLabel(pop, text=f'{(gains) - total_spends} EGP', font=('Arial', 50, 'bold'), text_color='#399918').pack(pady=(10,20))

                    def apply(task=task):
                        task['done'] = 'yes'
                        ref.execute('UPDATE Sessions SET Tasks = ? WHERE ID = ?', (dumps(tasks), session_data[0]))
                        conn.commit()
                        pop.destroy()
                        LoadTasks(listview, session_data)

                    CTkButton(pop, text='تأكيد', font=('Cairo Medium', 20), command=apply).pack(fill=X, padx=10, pady=10, side=BOTTOM)
                
                elif task['title'] == 'عد الطلاب في القاعة':
                    pop = CTkToplevel()
                    pop.geometry('400x400')
                    pop.attributes('-topmost', True)
                    pop.title('اتمام المهمة')
                    CTkLabel(pop, text='لما هتعد الطلاب في القاعة هتلاقيهم المفروض', font=('Cairo Medium', 25), wraplength=300).pack(pady=30)
                    ref.execute('SELECT * FROM Sessions WHERE ID = ?',(session_data[0], ))
                    attends_num = ref.fetchone()[4]
                    CTkLabel(pop, text=f'{attends_num} طالب', font=('Cairo Medium', 50), text_color='#399918').pack(pady=(10,20))

                    def apply(task=task):
                        task['done'] = 'yes'
                        ref.execute('UPDATE Sessions SET Tasks = ? WHERE ID = ?', (dumps(tasks), session_data[0]))
                        conn.commit()
                        pop.destroy()
                        LoadTasks(listview, session_data)

                    CTkButton(pop, text='تأكيد', font=('Cairo Medium', 20), command=apply).pack(fill=X, padx=10, pady=10, side=BOTTOM)
                
                else:
                    task['done'] = 'yes'
                    ref.execute('UPDATE Sessions SET Tasks = ? WHERE ID = ?', (dumps(tasks), session_data[0]))
                    conn.commit()
                    LoadTasks(listview, session_data)

    for x in listview.winfo_children():
        x.destroy()
    ref.execute('SELECT * FROM Sessions WHERE ID = ?', (session_data[0],))
    tasks = loads(ref.fetchone()[7])
    for task in tasks:
        task_frame = CTkFrame(listview, fg_color='#FEFFD2')
        task_frame.pack(fill=X, padx=5, pady=(5,5))
        CTkLabel(task_frame, text=task['title'], font=('Cairo Medium', 20)).pack(side=RIGHT, padx=15, pady=10)
        if task['done'] == 'no':
            CTkButton(task_frame, text='تحديد كمكتمل', font=('Cairo Medium', 16), command = lambda tit=task['title']: markAsComp(tit)).pack(side=LEFT, padx=15)
        else:
            CTkLabel(task_frame, text='', image=CTkImage(Image.open('TDSAssets/General/done_unthemed.png'), size=(50,50))).pack(side=LEFT, padx=15)



