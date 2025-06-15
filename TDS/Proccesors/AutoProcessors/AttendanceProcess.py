import threading
import requests
import json
from time import localtime, sleep
from Proccesors.Database.db import *


class AProccess:
    def __init__(self, session_data, attendslbl1, AttendsNum, attendplbl, nattendplbl):
        ref.execute("PRAGMA database_list;")
        team = ((ref.fetchone()[2]).split("\\")[-1]).replace(".db", "")
        conn_checker = connect("Application.db")
        ref_checker = conn_checker.cursor()
        ref_checker.execute("SELECT * FROM PGroups WHERE Name = ?", (team,))
        
        self.sd = session_data
        self.attendslbl1 = attendslbl1
        self.AttendsNum = AttendsNum
        self.attendplbl = attendplbl
        self.nattendplbl = nattendplbl

        # Start the thread to search attendance
        self.thread = threading.Thread(target=self.search_attendance)
        self.thread.start()

    def search_attendance(self):
        conn = create_db_connection()
        if conn is None:
            print("Failed to connect to the database.")
            return
        
        for _ in range(800):
            try:
                info = requests.get('https://tdsworks.pythonanywhere.com/get_attendance').json()
                
                print(info)

                for attnd in info['sessions'].get(self.sd[0], {}).get('attendance', []):
                    with conn:
                        ref = conn.cursor()
                        
                        # Fetch student attendance record
                        ref.execute('SELECT * FROM Students WHERE ID = ?', (attnd,))
                        print(f"Checking student ID from API: {attnd}")

                        student_record = ref.fetchone()
                        print(student_record)
                        
                        if not student_record:
                            print(f"No student found with ID {attnd}")
                            continue
                        
                        attnds = json.loads(student_record[6])
                        
                        if any(d.get(self.sd[1]) == 'Attended.' for d in attnds):
                            continue
                        
                        # Update attendance
                        attnds.append({f"{self.sd[1]}": "Attended."})
                        attnds_json = json.dumps(attnds)
                        ref.execute("UPDATE Students SET Attendance = ? WHERE ID = ?", (attnds_json, attnd))
                        
                        # Fetch total students in session group
                        ref.execute('SELECT * FROM Students WHERE Badges = ?', (self.sd[10 if self.type_of_payment == "بالحصة" else 9],))
                        studentsnum = len(ref.fetchall())
                        
                        # Update session attendance count
                        ref.execute('SELECT * FROM Sessions WHERE ID = ?', (self.sd[0],))
                        session_data2 = ref.fetchone()
                        new_attends = int(session_data2[4]) + 1
                        ref.execute('UPDATE Sessions SET Attendance = ? WHERE ID = ?', (new_attends, self.sd[0]))
                        
                        # Insert gains record
                        if student_record[10] == "BySession":
                            today = f'{localtime().tm_mday} \ {localtime().tm_mon} \ {localtime().tm_year}'
                            ref.execute('INSERT INTO Gains VALUES (?, ?, ?, ?)', (self.sd[0], None, self.sd[3], today))
                            
                        # Fetch updated session data
                        ref.execute('SELECT * FROM Sessions WHERE ID = ?', (self.sd[0],))
                        session_data3 = ref.fetchone()

                        # Update the UI in the main thread
                        self.attendslbl1.after(0, self.update_ui, session_data3[4 if self.type_of_payment == "بالحصة" else 3], studentsnum, new_attends)
                
                sleep(5)  # Prevent CPU overuse

            except requests.RequestException as e:
                print(f"Request failed: {e}")
                
            except Exception as e:
                print(f"Error: {e}")


    def update_ui(self, attendance, studentsnum, new_attends):
        self.attendslbl1.configure(text=f'عدد الحضور : {attendance}')
        self.AttendsNum.configure(text=f'عدد الحضور : {attendance}')
        per = (new_attends / studentsnum) * 100
        self.attendplbl.configure(text=f"{int(per)}%")
        self.nattendplbl.configure(text=f"{100-int(per)}%")

    def eliminate(self):
        self.thread.join()  # Ensure the thread terminates completely
        print("Thread terminated successfully.")
